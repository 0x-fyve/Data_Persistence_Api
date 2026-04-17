# Django Profile API

This is a simple Django REST API that creates and manages user profiles.  
It also uses external APIs to generate extra data like age, gender, and country.

---

## Features

- Create profile using a name
- Get all profiles
- Get single profile
- Delete profile
- Filters: gender, country, age group
- Uses external APIs for data enrichment

---

## Technologies Used

- Django
- Django REST Framework
- SQLite database
- Requests library

---

## External APIs Used

- https://api.genderize.io
- https://api.agify.io
- https://api.nationalize.io

---

## Setup Instructions

### 1. Install dependencies
```bash
pip install -r requirements.txt