# 🍽 Daily Menu Voting API

A RESTful API service that enables company employees to vote for their preferred restaurant's daily menu.

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Requirements](#-system-requirements)
- [Installation](#-installation)
  - [Local Setup](#local-setup)
  - [Docker Setup](#docker-setup)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)

## 🌐 Overview

Daily Menu Voting API is a sophisticated system designed to streamline the process of daily restaurant menu voting within a company. The service allows restaurants to post their daily menus and employees to vote for their preferred menu before 11:00 AM each day. The system provides comprehensive API endpoints for menu management, voting, and results tracking.

## ✨ Features

### Authentication & Authorization
- JWT-based authentication
- Employee registration and profile management
- Role-based access control (Admin/Employee)

### Restaurant Management
- Create and manage restaurant profiles
- Daily menu creation and updates
- Menu item management with prices

### Voting System
- Daily menu voting (before 11:00 AM)
- One vote per employee per day
- Real-time voting results
- Historical vote tracking

### API Versioning
- Support for multiple API versions (v1, v2)
- Backward compatibility
- Enhanced response details in v2

### Additional Features
- Comprehensive API documentation (Swagger/ReDoc)
- Automated testing suite
- Docker containerization

## 🛠 Tech Stack

- **Python 3.12**
- **Uv package manager**
- **Django 5**
- **Django REST Framework**
- **PostgreSQL**
- **Docker & Docker Compose**
- **JWT Authentication**
- **Swagger/ReDoc Documentation**
- **pytest & Factory Boy for testing**

## 💻 System Requirements

- Python 3.12+
- Uv (for local setup)
- PostgreSQL (for local setup)
- Docker & Docker Compose (for containerized setup)

## 🚀 Installation

### Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vladyslav-tmf/daily-menu-voting
   cd daily-menu-voting
   ```

2. Create and activate virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   # or
   .venv\Scripts\activate  # Windows
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Create .env file:
   ```bash
   cp .env.sample .env
   # Edit .env file with your configurations
   ```

5. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

6. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vladyslav-tmf/daily-menu-voting
   cd daily-menu-voting
   ```

2. Create .env file:
   ```bash
   cp .env.sample .env
   # Edit .env file with your configurations
   ```

3. Build and run containers:
   ```bash
   docker-compose up --build
   ```

The application will be available at:
- API: http://localhost:8000/api/v1/
- Admin panel: http://localhost:8000/admin/
- API Documentation (swagger): http://localhost:8000/api/docs/
- API Documentation (redoc): http://localhost:8000/api/redoc/

## 📚 API Documentation

The API documentation is available in Swagger UI format at `/api/docs/` and ReDoc format at `/api/redoc/` when the server is running. It provides detailed information about:

- Available endpoints
- Request/Response formats
- Authentication methods
- API versioning

### Employee
- Custom user model with email authentication
- Profile information (first name, last name)
- Role-based permissions

### Restaurant
- Basic information (name, address, contacts)
- Relationship with menus
- Indexed fields for optimal querying

### Menu
- Daily menu for restaurants
- Date-based organization
- Relationship with menu items
- Composite indexes for efficient queries

### MenuItem
- Menu item details (name, description, price)
- Relationship with specific menu
- Price validation

### Vote
- Employee's daily vote
- Relationship with menu and employee
- Time-based validation (before 11:00 AM)
- One vote per day constraint

## 🧪 Testing

The project includes comprehensive tests for:
- Models
- Serializers
- Views
- Authentication
- API versioning
- Validation rules

Run tests using:

Local environment:
  ```bash
  pytest
  ```

Docker environment:
  ```bash
  docker-compose exec app pytest
  ```
