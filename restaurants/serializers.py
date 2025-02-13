from rest_framework import serializers

from restaurants.models import Menu, MenuItem, Restaurant


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ("id", "name", "description", "price")


class MenuSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, required=False)
    date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = Menu
        fields = ("id", "restaurant", "date", "items")
        read_only_fields = ("restaurant",)

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        menu = Menu.objects.create(**validated_data)

        MenuItem.objects.bulk_create(
            [MenuItem(menu=menu, **item_data) for item_data in items_data]
        )

        return menu


class MenuDetailSerializer(MenuSerializer):
    restaurant = serializers.StringRelatedField()


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = (
            "id",
            "name",
            "address",
            "contact_phone",
            "contact_email",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")


class RestaurantDetailSerializer(RestaurantSerializer):
    today_menu = serializers.SerializerMethodField()

    class Meta(RestaurantSerializer.Meta):
        fields = RestaurantSerializer.Meta.fields + ("today_menu",)

    def get_today_menu(self, obj):
        menu = obj.get_menu_for_date()
        if menu:
            return MenuDetailSerializer(menu).data
        return None
