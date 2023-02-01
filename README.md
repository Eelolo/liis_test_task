# liis_test_task
An application that provides a RESTful API that allows authors to create articles for users. Users have the opportunity to subscribe to their favorite authors and see their closed articles

### Create Python virtual environment 
```
python3 -m venv venv
```
### Activate it:
```
. venv/bin/activate
```
### To deactivate run:
```
deactivate
```
### Install dependencies:
```
pip install -r requirements.txt
```

### Fill configuration in .env:
```
cp .env-example .env
```
### Run database migration:
```
python manage.py migrate
```
# Usage:
## To create superuser:
```
python manage.py createsuperuser
```
## Run tests:
```
python manage.py test
```
## Run server:
```
python manage.py runserver
```
# Endpoints:
Applications provide basic crud operations for users and articles
## users/
### Allowed methods
```
get, post
```
## users/pk/
### Allowed methods
```
get, patch, destroy
```
## articles/
### Allowed methods
```
get, post
```
## articles/pk/
### Allowed methods
```
get, patch, destroy
```
## users/subscribe/pk/
Endpoint allow to subscribe the author
###  Allowed methods
```
get
```
## users/unsubscribe/pk/
Endpoint allow to unsubscribe the author
### Allowed methods
```
get
```

