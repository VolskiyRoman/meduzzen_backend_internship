# Meduzzen_backend_internship

# My Django Application

## Getting Started

This Django program is designed for Meduzzen internships. Follow these steps to launch it.

### Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed (with `pip`)
- Django installed (use `pip install django`)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/VolskiyRoman/meduzzen_backend_internship
   cd /meduzzen_backend_internship

2. Install Docker

   (https://www.docker.com/get-started)

3. Build the Docker image:
   
   ```bash
   docker build -t my-django-app .
   
4. Run the Docker container:

   ```bash
   docker run -p 8000:8000 my-django-app

5. Run the unit tests inside the Docker container:

   ```bash
   python manage.py test
