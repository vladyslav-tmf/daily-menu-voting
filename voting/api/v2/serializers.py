from rest_framework import serializers

from restaurants.serializers import MenuDetailSerializer
from voting.models import Vote


class VoteSerializerV2(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ("id", "menu", "date")
        read_only_fields = ("id", "date")

    def validate_menu(self, menu):
        if not menu.is_today:
            raise serializers.ValidationError("You can only vote for today's menu")
        return menu

    def create(self, validated_data):
        validated_data["employee"] = self.context["request"].user
        return super().create(validated_data)


class VoteDetailSerializerV2(serializers.ModelSerializer):
    menu = MenuDetailSerializer(read_only=True)
    employee_email = serializers.EmailField(source="employee.email", read_only=True)
    employee_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Vote
        fields = ("id", "menu", "date", "employee_email", "employee_name")

    def get_employee_name(self, obj):
        return f"{obj.employee.get_full_name()}"


class VotingResultSerializerV2(serializers.Serializer):
    menu_id = serializers.IntegerField(source="menu")
    votes_count = serializers.IntegerField()
    menu_details = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    def get_menu_details(self, obj):
        menu = obj["menu"]
        return MenuDetailSerializer(menu).data

    def get_restaurant_name(self, obj):
        return obj["menu"].restaurant.name

    def get_percentage(self, obj):
        total_votes = sum(item["votes_count"] for item in self.context["results"])
        if total_votes == 0:
            return 0
        return round((obj["votes_count"] / total_votes) * 100, 1)
