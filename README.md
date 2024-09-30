# **Lunch Decider API**

**Lunch Decider API** is a backend service designed for employees to help them vote for their preferred lunch places. Restaurants upload their daily menus, and employees can vote for their favorite menu. The API supports multiple versions of the employee app, with older versions accepting a single menu vote, and newer versions allowing voting for up to three menus with different points.

## **Table of Contents**
- [Description](#description)
- [Features](#features)
- [Requirements](#requirements)
- [Installation and Setup](#installation-and-setup)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Swagger Documentation](#swagger-documentation)

## **Description**

The **Lunch Decider API** enables:
- Restaurants to upload their daily menus.
- Employees to vote for their favorite lunch menu before heading out.
- The system to handle app versioning to ensure compatibility between old and new versions of the employee app.

### **API Features:**
- **Authentication**: Employees must authenticate to vote or upload menus.
- **Menu Upload**: Restaurants can upload a menu for each day.
- **Voting**: Employees can vote for the available menus.
  - **Old app version**: Employees can vote for a single menu with a point value of 1.
  - **New app version**: Employees can vote for up to three menus, assigning 1, 2, or 3 points based on their preference.
- **Voting Results**: Employees can view the results of the day’s voting.

---

## **Features**

1. **Employee Management**:
   - Create employees and manage authentication using JWT tokens.

2. **Restaurant and Menu Management**:
   - Create restaurants and upload menus daily.

3. **Voting System**:
   - Employees can vote for their favorite menus, with support for multiple app versions.

4. **Versioning Support**:
   - Old app versions can only vote for one menu.
   - New app versions can vote for up to three menus with different points.

5. **Swagger Documentation**:
   - Detailed API documentation with Swagger UI to test and explore the API endpoints.

---

## **Requirements**

Make sure you have the following installed before proceeding:

- **Python** (3.9 or above)
- **pip** (Python package manager)
- **SQLite** (used as the default database)

---

## **Installation and Setup**

### Step 1: Clone the Repository

```bash
git clone https://github.com/abhipythondev05/lunch_decider.git
cd lunch_decider
```

### Step 2: Set Up Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
```
#### Activate the virtual environment:
* On macOS/Linux:

    ```bash
    source venv/bin/activate
    ```
* On Windows:

    ```bash
    venv\Scripts\activate
    ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Apply Migrations
```bash
python manage.py migrate
```
This will set up the SQLite database and apply all migrations.

### Step 5: Create a Superuser (Optional)
To access the Django admin panel, you need a superuser account. You can create one by running:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up the username, email, and password for the superuser.

### Step 6: Run the Development Server
Start the Django development server:

```bash
python manage.py runserver
```
Your API will be available at http://127.0.0.1:8000/.

---
## API Endpoints

Here are some of the key API endpoints available in the Lunch Decider API:

### Authentication
  * ### POST /api/token/: Obtain JWT token for authentication.
    * ### Request:
        ```json
        {
            "username": "your-username",
            "password": "your-password"
        }
        ```
### Employee Endpoints
  * ### POST /api/employees/: Create a new employee (for registration).
    * ### Request:
        ```json
        {
            "username": "newemployee",
            "email": "newemployee@example.com",
            "password": "your-password"
        }
        ```
### Restaurant Endpoints
  * ### POST /api/restaurants/: Create a new restaurant.

    * ### Request:
        ```json
        {
            "name": "Restaurant Name"
        }
        ```

  * ### POST /api/menu/: Upload today's menu for a restaurant.

    * ### Request:
        ```json
        {
            "restaurant": 1,
            "date": "YYYY-MM-DD",
            "items": "Item1, Item2, Item3"
        }
        ```

### Voting Endpoints
  * ### POST /api/vote/: Vote for today’s menu (supports both old and new app versions).

    * ### Request (Old Version):

        ```json
        {
        "menu_ids": [1]
        }
        ```
    * ### Request (New Version):

        ```json
        {
        "menu_ids": [1, 2, 3],
        "points": [3, 2, 1]
        }
        ```
  * ### GET /api/results/today/: Get today’s voting results.

### Testing
You can run tests using pytest. Make sure to install the testing dependencies listed in requirements.txt.

```bash
python manage.py test
```
This will run the test suite to validate the functionality of the APIs.

### Swagger Documentation
The API is fully documented with Swagger.

Once your development server is running, you can access the Swagger UI for interactive API documentation and testing at:

http://127.0.0.1:8000/swagger/

You can view and interact with all available API endpoints, making it easier to test and explore the API.
