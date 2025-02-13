from rest_framework import serializers

from restaurants.models import Menu
from voting.models import Vote


class VoteSerializerV1(serializers.ModelSerializer):
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


class VoteDetailSerializerV1(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="menu.restaurant.name")
    menu_date = serializers.DateField(source="menu.date")

    class Meta:
        model = Vote
        fields = ("id", "restaurant_name", "menu_date")


class VotingResultSerializerV1(serializers.Serializer):
    votes_count = serializers.IntegerField()
    restaurant_name = serializers.SerializerMethodField()

    def get_restaurant_name(self, obj):
        menu = Menu.objects.get(id=obj["menu"])
        return menu.restaurant.name
