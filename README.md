# Employee Service Request Management System

This is a backend project developed using **Python, Django and Django REST Framework**.

The main purpose of this project is to allow employees to create service requests and track their requests. The system also provides different permissions for employees and authorized users.

## Technologies Used

* Python
* Django
* Django REST Framework
* JWT Authentication
* SQLite
* Thunder Client
* Git & GitHub

## Features

* User registration and login
* JWT authentication
* Employee and admin roles
* Create service requests
* View service requests
* Update service request status
* Delete service requests
* Employee can view their own requests
* Role-based permissions
* REST APIs

## How the Project Works

1. User registers in the system.
2. User logs in and gets a JWT access token.
3. The token is used to access protected APIs.
4. Employee creates a service request.
5. Employee can view their service requests.
6. Authorized users can manage the requests and update the status.

## API Endpoints

### Authentication

```text
POST /api/register/
POST /api/login/
```

### Service Requests

```text
GET    /api/service-requests/
POST   /api/service-requests/
GET    /api/service-requests/{id}/
PUT    /api/service-requests/{id}/
PATCH  /api/service-requests/{id}/
DELETE /api/service-requests/{id}/
```

## Authentication

I used **JWT authentication** in this project.

After login, the user gets an access token. The token is sent in the request header to access protected APIs.

```text
Authorization: Bearer <access_token>
```

## Role-Based Permissions

The project uses role-based permissions.

### Employee

* Create service request
* View own requests
* Track request status

### Admin / Authorized User

* View requests
* Manage requests
* Update request status

## Database

I used Django models and Django ORM to store users and service requests.

A service request is connected to the user who created it.

```text
User
  |
  | 1
  |
  | many
  ↓
Service Request
```

## Testing

I tested the APIs using **Thunder Client**.

I tested:

* User registration
* Login
* JWT authentication
* Creating requests
* Getting requests
* Updating requests
* Deleting requests
* Permission restrictions

## What I Learned

Through this project, I learned:

* How to create REST APIs using Django REST Framework
* How serializers work
* How to use Django ORM
* JWT authentication
* Authentication and authorization
* Role-based permissions
* Model relationships
* API testing using Thunder Client

## Future Improvements

* Email notifications
* File attachments
* Search and filtering
* Pagination
* Swagger API documentation
* Deploying the project to the cloud

## Author

**Kummara Anoop**

Python | Django | REST API | SQL | AI/ML
