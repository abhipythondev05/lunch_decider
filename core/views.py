from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee, Menu, Restaurant, Vote
from .serializers import (
    EmployeeCreateSerializer,
    EmployeeSerializer,
    MenuSerializer,
    RestaurantSerializer,
    VoteSerializer,
)


class CreateEmployeeView(generics.CreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeCreateSerializer

    def create(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateRestaurantView(APIView):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = RestaurantSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UploadMenuView(generics.CreateAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        restaurant = request.data.get("restaurant")
        date = request.data.get("date")
        if Menu.objects.filter(restaurant=restaurant, date=date).exists():
            return Response(
                {"error": "Menu for this restaurant already exists for the day."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = MenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TodayMenuView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        menus = Menu.objects.filter(date=today)
        serializer = MenuSerializer(menus, many=True)
        if serializer.data:
            return Response(serializer.data)
        return Response({"error": "No menu found."}, status=status.HTTP_404_NOT_FOUND)


class VoteView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        build_version = request.headers.get("Build-Version")
        menu_ids = request.data.get("menu_ids")  # List of menu IDs
        points = request.data.get("points")  # List of points

        today = timezone.now().date()
        available_menus = Menu.objects.filter(date=today).values_list("id", flat=True)

        if not menu_ids or not isinstance(menu_ids, list):
            return Response(
                {"error": "Menu IDs must be provided as a list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if build_version.startswith("1."):
            # Old version: accept only one menu ID and assign 1 point
            if len(menu_ids) != 1:
                return Response(
                    {"error": "Old version only allows voting for one menu."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            points = [1]  # Assign default point
        else:
            # New version: Validate the number of menus and points
            if not points or not isinstance(points, list):
                return Response(
                    {"error": "Points must be provided as a list."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(menu_ids) != len(points):
                return Response(
                    {"error": "Number of menu IDs and points must match."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(menu_ids) > 3 or len(menu_ids) < 1:
                return Response(
                    {"error": "You must vote for between one and three menus."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(menu_ids) > len(available_menus):
                return Response(
                    {
                        "error": f"Only {len(available_menus)} menus available for voting today."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if len(set(points)) != len(points):
                return Response(
                    {"error": "Points must be unique for each menu."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if any(p not in [1, 2, 3] for p in points):
                return Response(
                    {"error": "Invalid points; must be 1, 2, or 3."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Ensure employee hasn"t already voted today
        if Vote.objects.filter(employee=request.user, menu__date=today).exists():
            return Response(
                {"error": "You have already voted today."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate that each menu_id is valid and for today
        for menu_id in menu_ids:
            if menu_id not in available_menus:
                return Response(
                    {"error": f"Menu ID {menu_id} is not valid for today."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Save the votes for each menu
        for menu_id, point in zip(menu_ids, points):
            Vote.objects.create(employee=request.user, menu_id=menu_id, points=point)

        return Response(
            {"status": "Votes cast successfully"}, status=status.HTTP_201_CREATED
        )


class TodayResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        votes = Vote.objects.filter(menu__date=today)
        results = {}
        for vote in votes:
            menu_id = vote.menu_id
            if menu_id not in results:
                results[menu_id] = 0
            results[menu_id] += vote.points
        return Response(results)
