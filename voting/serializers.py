from rest_framework import serializers

from restaurants.models import Menu
from restaurants.serializers import MenuDetailSerializer
from voting.models import Vote


class VoteSerializer(serializers.ModelSerializer):
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


class VoteDetailSerializer(VoteSerializer):
    menu = MenuDetailSerializer(read_only=True)


class VotingResultSerializer(serializers.Serializer):
    menu_id = serializers.IntegerField(source="menu")
    votes_count = serializers.IntegerField()
    menu_details = serializers.SerializerMethodField()
    restaurant_name = serializers.SerializerMethodField()

    def get_menu_details(self, obj):
        menu = Menu.objects.get(id=obj["menu"])
        return MenuDetailSerializer(menu).data

    def get_restaurant_name(self, obj):
        menu = Menu.objects.get(id=obj["menu"])
        return menu.restaurant.name
