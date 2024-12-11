This Project is a part of SWE Assessment **WorkIndia.**

It is a IRCTC like Train Ticket Booking System built entirely with **Django, Postgres** and tested with **Postman**.

Refer [Postman Documentation](https://documenter.getpostman.com/view/38225697/2sAYHwK56F) here.

### Basic Features-

1. **RBAC**-
    1. **Admin** - can perform all operations like adding trains, updating total seats in a train, etc.
    2. **User** - can check availability of trains, seat availability, book seats, get booking details, etc.
2. **Register** a User - An endpoint for registering a user.
3. **Login** User - user to log into his account
4. **Add a New Train** - An endpoint for the admin to create a new train with a source and destination
5. **Get Seat Availability** - An endpoint for the users where they can enter the source and destination and fetch all the trains between that route with their availabilities
6. **Book a Seat** - An endpoint for the users to book a seat on a particular train
7. **Get Specific Booking Details** - Fetch booking details.

### Mandatory Requirements Completed:

1. Protected all the admin API endpoints with an **API key** that will be known only to admin. (Present in the .env file)
2. For booking a seat and getting specific booking details, **Authorization Token** received in the login endpoint. (Through Headers)
3. Prevention of **Race Conditions** - If more than 1 users simultaneously try to book seats, only either one of the users should be able to book. Implemented this using **@transaction.atomic** decorator in django.db module.

### Setup-

1. Create and Activate Virtual Environment (venv preferred). 
```
python -m venv venv
venv\Scripts\activate
```
2. Install dependencies from requirements.txt. ```pip install -r requirements.txt```
3. Setup your Postgres Configuration in settings.py.
```DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'your_db_host',
        'PORT': 'your_db_port',
    }
}
```
4. Makemigrations, Migrate, CreateSuperUser etc.
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
5. Refer More Details in Postman Documentation.

