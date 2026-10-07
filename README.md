# College Student & Placement Management System

A web-based **College Student & Placement Management System** built with **Django MVT**, **Django REST Framework**, **MySQL**, and **Docker**.

The system manages students, faculty, attendance, marks, announcements, holidays, companies, placement drives, and student placement applications through role-based access.

## Features

### Admin
- Admin dashboard
- Manage students
- Manage faculty
- Manage placement cell users
- Create and manage announcements
- Create and manage holidays
- User account creation and password setup through email

### Faculty
- Faculty dashboard
- Manage assigned subjects
- Mark and edit student attendance
- Enter and manage student marks
- View role-based announcements

### Placement Cell
- Placement dashboard
- Manage companies
- Create and manage placement drives
- View student applications
- Update application status
- Publish placement-related announcements

### Student
- Student dashboard
- View attendance by year and month
- View subject-wise marks
- View announcements and holidays
- View available placement drives
- Check placement eligibility
- Apply for eligible placement drives
- Track application status

## User Roles

1. **Admin**
2. **Faculty**
3. **Placement Cell**
4. **Student**

## Technology Stack

### Backend
- Python 3.13
- Django 5.2.8
- Django REST Framework
- SimpleJWT
- Gunicorn

### Database
- MySQL 8.0

### Frontend
- Django HTML Templates
- HTML5
- CSS3
- JavaScript

### Static & Media
- Django static files
- WhiteNoise
- Media uploads

### DevOps
- Docker
- Docker Desktop
- Git & GitHub

### Planned AWS Deployment
- Amazon EC2
- Amazon RDS MySQL
- Amazon ECR
- Nginx
- GitHub Actions
- CloudWatch
- Optional S3 for media storage

> Kubernetes is not required for this project.

## Project Structure

```text
college_portal/
│
├── accounts/
├── academics/
├── placements/
├── notifications/
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── wsgi.py
│   └── asgi.py
│
├── templates/
├── static/
│   ├── css/
│   └── js/
├── media/
├── manage.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
└── README.md
```

## Main Modules

### Accounts
Handles:
- Custom Django user model
- Role-based access
- Authentication
- Password setup flow
- JWT authentication for API access

### Academics
Handles:
- Departments
- Students
- Faculty
- Subjects
- Attendance
- Marks

### Placements
Handles:
- Companies
- Placement drives
- Student applications
- Application status tracking

### Notifications
Handles:
- Announcements
- Holidays
- Audience-based announcements

## Authentication

The project uses Django authentication for the web application.

The REST API uses JWT authentication with:

```text
Authorization: Bearer <access_token>
```

JWT configuration includes:
- Access token lifetime: 60 minutes
- Refresh token lifetime: 1 day

## Environment Variables

Create a `.env` file in the same directory as `manage.py`.

Example:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=college_portal
DB_USER=root
DB_PASSWORD=your-mysql-password
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

### Important

Never commit `.env` to GitHub.

Use `.env.example` with placeholder values instead.

## Local Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd college_portal
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MySQL

Create a MySQL database named:

```text
college_portal
```

Configure the database values in `.env`.

For normal local Django execution:

```env
DB_HOST=127.0.0.1
```

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Docker Setup

The project is containerized using Docker and Gunicorn.

### Build the Docker image

```bash
docker build -t college-portal .
```

### Run the container

When MySQL is running on the Windows host:

```env
DB_HOST=host.docker.internal
```

Then run:

```bash
docker run --env-file .env -p 8000:8000 college-portal
```

Open:

```text
http://127.0.0.1:8000/
```

### Docker Architecture

```text
Browser
   |
   v
Docker Container
   |
   +-- Gunicorn
   |
   +-- Django
   |
   +-- WhiteNoise
   |
   v
MySQL
```

## Static Files

Static files are collected using:

```bash
python manage.py collectstatic --noinput
```

WhiteNoise is used to serve static files when running the Django application with Gunicorn.

## Production Deployment Plan

The planned deployment architecture is:

```text
GitHub
   |
   v
GitHub Actions
   |
   v
Docker Image
   |
   v
Amazon ECR
   |
   v
Amazon EC2
   |
   +--> Nginx
   |
   +--> Gunicorn
   |
   +--> Django
   |
   v
Amazon RDS MySQL
```

Additional production services may include:
- Amazon S3 for media files
- CloudWatch for monitoring and logs
- Route 53 for DNS
- AWS Certificate Manager for HTTPS

## Security Notes

- Keep `.env` out of version control.
- Do not commit database passwords or email credentials.
- Use a strong Django `SECRET_KEY`.
- Set `DEBUG=False` in production.
- Configure `ALLOWED_HOSTS` for the production domain/IP.
- Restrict RDS access to the required application security group.
- Use HTTPS in production.

## API

The project includes Django REST Framework APIs for application data and JWT-based authentication.

API routes are organized under the project/application URL configurations.

Main API modules include:
- Accounts
- Academics
- Placements
- Notifications

## Development Checks

Before committing changes:

```bash
python manage.py check
```

For Docker:

```bash
docker build -t college-portal .
```

## Future Improvements

- GitHub Actions CI/CD pipeline
- AWS EC2 deployment
- AWS RDS integration
- Nginx reverse proxy
- HTTPS with AWS Certificate Manager
- S3-based media storage
- CloudWatch monitoring and centralized logs
- Automated backups
- Improved reporting and analytics

## Project Status

### Completed
- Role-based Django application
- Student management
- Faculty management
- Placement management
- Attendance management
- Marks management
- Announcements and holidays
- Student placement applications
- JWT API authentication
- MySQL integration
- Docker containerization
- Gunicorn
- WhiteNoise static file serving

### In Progress
- AWS deployment
- ECR image publishing
- EC2 deployment
- RDS MySQL production setup
- Nginx configuration
- CI/CD with GitHub Actions

## Author

**Mekala Bhavana**

College Student & Placement Management System  
Built with Django, MySQL, REST APIs, and Docker.
