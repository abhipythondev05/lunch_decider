import json

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Employee, Menu, Restaurant, Vote


class BaseTest(APITestCase):
    def setUp(self):
        # Create an employee user for testing
        self.employee = Employee.objects.create_user(
            username="testuser", password="testpass"
        )
        self.employee2 = Employee.objects.create_user(
            username="testuser2", password="testpass"
        )
        self.restaurant = Restaurant.objects.create(name="Test Restaurant")
        self.today = timezone.now().date()

    def createMenu(self):
        self.menu = Menu.objects.create(
            restaurant=self.restaurant, date=str(self.today), items="Item1, Item2"
        )
        self.menu2 = Menu.objects.create(
            restaurant=self.restaurant, date=str(self.today), items="Item3, Item4"
        )
        self.menu3 = Menu.objects.create(
            restaurant=self.restaurant, date=str(self.today), items="Item5, Item6"
        )
        self.menu4 = Menu.objects.create(
            restaurant=self.restaurant, date=str(self.today), items="Item7, Item8"
        )

    def authenticate(self, username="testuser", password="testpass"):
        # Helper method to authenticate
        self.client.login(username=username, password=password)

    def jwt_authenticate(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            '{"username": "testuser", "password": "testpass"}',
            content_type="application/json",
        )
        # Check if the response is valid and contains the access token
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data.get("access", None)
        self.assertIsNotNone(token, "Access token not found in response")
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)


class AuthenticationTests(BaseTest):
    def test_create_employee(self):
        self.jwt_authenticate()  # Authenticate the request
        url = reverse("employee-create")
        data = {
            "username": "newemployee",
            "email": "newemployee@example.com",
            "password": "securepassword",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_employee_login(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            '{"username": "testuser", "password": "testpass"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_invalid_employee_login(self):
        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            '{"username": "testuser", "password": "wrongpass"}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RestaurantTests(BaseTest):
    def test_create_restaurant(self):
        self.jwt_authenticate()
        url = reverse("restaurant-create")
        data = {"name": "New Restaurant"}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Restaurant")

    def test_create_restaurant_without_authentication(self):
        url = reverse("restaurant-create")
        data = {"name": "New Restaurant"}
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MenuTests(BaseTest):
    def test_create_menu(self):
        self.jwt_authenticate()
        url = reverse("menu-create")
        data = {
            "restaurant": self.restaurant.id,
            "date": str(self.today),
            "items": "Item5, Item6",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_duplicate_menu(self):
        self.jwt_authenticate()
        url = reverse("menu-create")
        data = {
            "restaurant": self.restaurant.id,
            "date": str(self.today),
            "items": "Item1, Item2",
        }
        self.client.post(
            url, json.dumps(data), content_type="application/json"
        )  # First menu creation
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )  # Try to create the same menu again
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_menu_without_authentication(self):
        url = reverse("menu-create")
        data = {
            "restaurant": self.restaurant.id,
            "date": str(self.today),
            "items": "Item1, Item2",
        }
        response = self.client.post(
            url, json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TodayMenuTests(BaseTest):
    def test_get_today_menu(self):
        self.createMenu()
        self.jwt_authenticate()
        url = reverse("menu-today")
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_get_today_menu_no_menus(self):
        self.jwt_authenticate()
        Menu.objects.all().delete()  # Remove all menus
        url = reverse("menu-today")
        response = self.client.get(url, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class VotingTests(BaseTest):
    def test_vote_with_old_version(self):
        self.createMenu()
        self.jwt_authenticate()
        url = reverse("vote")
        data = {"menu_ids": [self.menu.id]}
        response = self.client.post(
            url,
            json.dumps(data),
            HTTP_BUILD_VERSION="1.0",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_vote_with_new_version(self):
        self.createMenu()
        self.jwt_authenticate()
        url = reverse("vote")
        data = {"menu_ids": [self.menu.id, self.menu2.id], "points": [2, 1]}
        response = self.client.post(
            url,
            json.dumps(data),
            HTTP_BUILD_VERSION="2.0",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_vote_invalid_menu(self):
        self.createMenu()
        self.jwt_authenticate()
        url = reverse("vote")
        data = {"menu_ids": [999], "points": [1]}  # Invalid menu ID
        response = self.client.post(
            url,
            json.dumps(data),
            HTTP_BUILD_VERSION="2.0",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Menu ID 999 is not valid", response.data["error"])

    def test_vote_duplicate_points(self):
        self.createMenu()
        self.jwt_authenticate()
        url = reverse("vote")
        data = {
            "menu_ids": [self.menu.id, self.menu2.id],
            "points": [1, 1],
        }  # Duplicate points
        response = self.client.post(
            url,
            json.dumps(data),
            HTTP_BUILD_VERSION="2.0",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Points must be unique", response.data["error"])

    def test_vote_more_than_three_menus(self):
        self.createMenu()
        self.jwt_authenticate()
        Menu.objects.create(
            restaurant=self.restaurant, date=str(self.today), items="Item5"
        )
        url = reverse("vote")
        data = {
            "menu_ids": [self.menu.id, self.menu2.id, self.menu3.id, self.menu4.id],
            "points": [3, 2, 1, 1],
        }  # More than three menus
        response = self.client.post(
            url,
            json.dumps(data),
            HTTP_BUILD_VERSION="2.0",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "You must vote for between one and three menus.", response.data["error"]
        )

    def test_vote_already_voted(self):
        self.createMenu()
        self.jwt_authenticate()
        url = reverse("vote")
        data = {"menu_ids": [self.menu.id], "points": [1]}
        self.client.post(
            url,
            json.dumps(data),
            HTTP_BUILD_VERSION="2.0",
            content_type="application/json",
        )  # First vote
        response = self.client.post(
            url,
            json.dumps(data),
            HTTP_BUILD_VERSION="2.0",
            content_type="application/json",
        )  # Try voting again
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("You have already voted today.", response.data["error"])


class ResultsTests(BaseTest):
    def test_get_today_results(self):
        self.createMenu()
        self.jwt_authenticate()
        Vote.objects.create(employee=self.employee, menu=self.menu, points=1)
        Vote.objects.create(employee=self.employee2, menu=self.menu2, points=2)
        url = reverse("results-today")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.menu.id, response.data)
        self.assertIn(self.menu2.id, response.data)

    def test_get_today_results_no_votes(self):
        self.jwt_authenticate()
        url = reverse("results-today")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})
