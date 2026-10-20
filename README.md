# Personal Notes Tracker API

A secure, RESTful Flask API backend designed for user-owned notes management. This project features session-based authentication, secure password hashing using Flask-Bcrypt, data isolation so users can only access their own notes, and paginated resource endpoints built with Flask-RESTful.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Installation & Setup](#installation--setup)
- [Database Setup & Seeding](#database-setup--seeding)
- [Running the Application](#running-the-application)
- [API Endpoints Documentation](#api-endpoints-documentation)
- [Testing with Postman](#testing-with-postman)

---

## Project Overview

This API serves as the backend service for a personal note-taking application. It ensures secure account registration, session login management, and full CRUD (Create, Read, Update, Delete) capability for notes tied strictly to authenticated users.

### Key Requirements Met
- **Authentication & Authorization**: Session-based user sign-up, login, logout, and active session verification (`/check_session`).
- **Data Protection**: Route protection ensuring users cannot view, edit, or delete notes belonging to other accounts.
- **Pagination**: Paginated index endpoint (`/notes?page=1&per_page=5`) for efficient data loading.

---

## Tech Stack

- **Python**: `3.8+`
- **Framework**: `Flask` & `Flask-RESTful`
- **Database & ORM**: `SQLite`, `Flask-SQLAlchemy`, `Flask-Migrate`
- **Security**: `Flask-Bcrypt` for password hashing
- **Environment & Tools**: `Pipenv`, `Faker` (for sample seeding)

---

## Installation & Setup

Follow these steps to set up the development environment on your local machine:

1. **Clone the Repository**
   ```bash
   git clone <your-repository-url>
   cd flask-c10-summative-lab-sessions-and-jwt-clients
   ```

2. **Install Dependencies**  
   Ensure `pipenv` is installed on your system, then install the required packages:
   ```bash
   pipenv install
   ```

3. **Activate the Virtual Environment**
   ```bash
   pipenv shell
   ```

---

## Database Setup & Seeding

1. **Initialize Migration Folder**
   ```bash
   flask db init
   ```

2. **Generate Database Migrations**
   ```bash
   flask db migrate -m "Initial database setup"
   ```

3. **Apply Migrations to Create Database (`app.db`)**
   ```bash
   flask db upgrade
   ```

4. **Seed the Database with Test Data**  
   Run the seed script to create initial test users (`kamau`, `wanjiru`) and localized sample notes:
   ```bash
   python seed.py
   ```

---

## Running the Application

To start the Flask development server, execute:

```bash
python app.py
```

The server will start locally at: `http://127.0.0.1:5555/`

---

## API Endpoints Documentation

### Authentication Routes

| Endpoint | HTTP Method | Description | Request Body Example | Status Codes |
|---|---|---|---|---|
| `/signup` | `POST` | Registers a new user account and creates an active session. | `{"username": "charlie", "password": "password123"}` | `201 Created`, `400 Bad Request`, `422 Unprocessable` |
| `/login` | `POST` | Authenticates existing user credentials and opens a session. | `{"username": "kamau", "password": "password123"}` | `200 OK`, `401 Unauthorized` |
| `/logout` | `DELETE` | Terminates current user session and clears the session cookie. | None | `204 No Content`, `401 Unauthorized` |
| `/check_session` | `GET` | Validates active session and returns currently logged-in user info. | None | `200 OK`, `401 Unauthorized` |

### Notes (User-Bound Resource) Routes

| Endpoint | HTTP Method | Description | Request Body / Parameters | Status Codes |
|---|---|---|---|---|
| `/notes` | `GET` | Fetches a paginated list of notes owned by the logged-in user. | Query Params: `?page=1&per_page=5` | `200 OK`, `401 Unauthorized` |
| `/notes` | `POST` | Creates a new note assigned to the current user. | `{"title": "M-Pesa Expense", "content": "Paid electricity bill", "category": "Finance"}` | `201 Created`, `400 Bad Request`, `401 Unauthorized` |
| `/notes/<id>` | `PATCH` | Updates an existing note owned by the user. | `{"title": "Updated Title", "content": "Updated Content"}` | `200 OK`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found` |
| `/notes/<id>` | `DELETE` | Deletes a specific note owned by the user. | None | `204 No Content`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found` |

---

## Testing with Postman

1. Ensure the server is running (`python app.py`).
2. Perform a `POST` request to `http://127.0.0.1:5555/login` with valid credentials.
3. Postman will automatically persist the session cookie.
4. Execute `GET http://127.0.0.1:5555/notes` to view the authenticated user's notes.