from rest_framework import serializers

from .models import Employee, Menu, Restaurant, Vote


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["username", "email"]


class EmployeeCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Employee
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        # Create a new employee with a hashed password
        employee = Employee(
            username=validated_data["username"], email=validated_data.get("email", "")
        )
        employee.set_password(validated_data["password"])  # Hash the password
        employee.save()
        return employee


class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ["id", "name"]


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ["id", "restaurant", "date", "items"]


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ["employee", "menu", "points"]
