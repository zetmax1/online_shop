# Online shop API

A simple Django REST API for managing users, products, and orders with JWT authentication.
This project provides a complete backend solution for an e-commerce platform. Users can register, browse products, and
place orders. Admins can manage products and view all orders. The API uses JWT tokens for secure authentication and
includes proper permission controls to ensure users can only access their own data.

## IMPORTANT
I changed email's so you can write your email and password inside of setting.
Database settings must be adjusted before running the project
## Features

- User registration and authentication with JWT
- Product management (CRUD operations)
- Order system with order items
- Permission-based access control
- API filtering and pagination

## Tech Stack

- Django & Django REST Framework
- JWT Authentication (Simple JWT)
- PostgreSQL
- Python Decouple for environment variables

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/zetmax1/ecommerce-api.git
cd ecommerce-api
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
```

4. Run migrations:

```bash
python manage.py migrate
python manage.py migrate token_blacklist
```

5. Create superuser:

```bash
python manage.py createsuperuser
```

6. Start the server:

```bash
python manage.py runserver
```
