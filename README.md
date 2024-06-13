markdown
Code kopieren
# Videoflix

Videoflix is a Django-based web application for uploading and streaming videos in various resolutions. It allows users to register, log in, and manage their video content. The application supports video transcoding to multiple resolutions and thumbnail extraction using FFmpeg.

## Features
- User registration, login, and authentication
- Video upload and transcoding to different resolutions (480p, 720p, 1080p)
- Thumbnail extraction from uploaded videos
- Video streaming in different resolutions
- Password reset functionality
- Email activation for new users
- RESTful API for user and video management

## Requirements
- Python 3.10+
- Django 5.0.4
- PostgreSQL
- Redis
- FFmpeg
- Node.js (for frontend development)

## Setup Instructions

### Backend Setup
Clone the repository
```bash
git clone https://github.com/yourusername/videoflix.git
cd videoflix
Create a virtual environment and activate it

bash
Code kopieren
python -m venv env
source env/bin/activate # On Windows use `env\Scripts\activate`
Install the dependencies

bash
Code kopieren
pip install -r requirements.txt
Set up PostgreSQL database

Create a new PostgreSQL database and user.
Update the DATABASES setting in videoflix/settings.py with your database credentials.
Run database migrations

bash
Code kopieren
python manage.py migrate
Create a superuser

bash
Code kopieren
python manage.py createsuperuser
Set up Redis

Install Redis and start the Redis server.
Set up FFmpeg

Install FFmpeg and ensure it is available in your system's PATH.
Configure email settings

Update the email settings in videoflix/settings.py with your email service credentials.
Collect static files

bash
Code kopieren
python manage.py collectstatic
Run the development server

bash
Code kopieren
python manage.py runserver
Frontend Setup
Navigate to the frontend directory

bash
Code kopieren
cd frontend
Install the dependencies

bash
Code kopieren
npm install
Run the development server

bash
Code kopieren
npm start
Running Workers for Video Processing
Start the Redis worker

bash
Code kopieren
python manage.py rqworker
Running Tests
Run backend tests

bash
Code kopieren
python manage.py test
Run frontend tests

bash
Code kopieren
npm test
Project Structure
markdown
Code kopieren
videoflix/
├── backend/
│   ├── videoflix/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tests.py
│   ├── videos/
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── tasks.py
│   │   ├── views.py
│   │   ├── signals.py
│   │   ├── tests.py
│   ├── manage.py
│   ├── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.js
│   │   ├── index.js
│   │   ├── components/
│   │   ├── services/
│   ├── package.json
├── README.md
Deployment
To deploy the application, you can use any cloud service provider like AWS, Heroku, or DigitalOcean. Ensure you set the environment variables and configure the necessary services like PostgreSQL and Redis on your server.

Nginx Configuration
Here is an example Nginx configuration for serving the Django application:

nginx
Code kopieren
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/project/staticfiles/;
    }

    location /media/ {
        alias /path/to/your/project/media/;
    }

    error_log /var/log/nginx/videoflix_error.log;
    access_log /var/log/nginx/videoflix_access.log;
}
Supervisor Configuration
Here is an example Supervisor configuration for running the Gunicorn server and Redis worker:

ini
Code kopieren
[program:videoflix-gunicorn]
command=/path/to/your/env/bin/gunicorn videoflix.wsgi:application --bind 127.0.0.1:8000 --workers 3
directory=/path/to/your/project
user=youruser
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/videoflix_gunicorn.log
stderr_logfile=/var/log/supervisor/videoflix_gunicorn_err.log

[program:videoflix-worker]
command=/path/to/your/env/bin/python /path/to/your/project/manage.py rqworker
directory=/path/to/your/project
user=youruser
autostart=true
autorestart=true
stdout_logfile=/var/log/supervisor/videoflix_worker.log
stderr_logfile=/var/log/supervisor/videoflix_worker_err.log
Contributing
Contributions are welcome! Please fork the repository and create a pull request with your changes.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Contact
For any questions or support, please contact sefa_guer@hotmail.de

vbnet
Code kopieren

This README provides a comprehensive guide to setting up, running, and contributing to the Videoflix project. Feel free to customize it further based on your project's specific requirements and configurations.