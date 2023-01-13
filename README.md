# Social network "YATUBE"

![Workflow status](https://github.com/Beloborodova-Anastasiia/yatube/actions/workflows/yatube_workflow.yml/badge.svg
)

### Description

Social network "Yatube" is for keeping a diary. Users can create an account, publish notes, subscribe on another author, tag and comment on fovourite notes, add notice to the special groups.

### Technologies

Python 3.7

Django 2.2.19

### Local project run:

Clone a repository and navigate to it on the command line:

```
git clone https://github.com/Beloborodova-Anastasiia/yatube.git
```

```
cd yatube
```

Create and activate virtual environment:

```
for Mac or Linux:
python3 -m venv env
source venv/bin/activate
```
```
for Windows:
python -m venv venv
source venv/Scripts/activate 
```

Install dependencies from requirements.txt file:

```
for Mac or Linux:
python3 -m pip install --upgrade pip
```
```
for Windows:
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Make migrations:

```
cd yatube/

```
```
for Mac or Linux:
python3 manage.py migrate
```
```
for Windows:
python manage.py migrate
```

Create superuser:

```
for Mac or Linux:
python3 manage.py createsuperuser
```
```
for Windows:
python manage.py createsuperuser
```

Run project:

```
for Mac or Linux:
python3 manage.py runserver
```
```
for Windows:
python manage.py runserver
```

Servise is available in local server:

```
http://127.0.0.1:8000/
```

Django admin is available in next link:

```
http://127.0.0.1:8000/admin/
```


### Author

Anastasiia Beloborodova 

anastasiia.beloborodova@gmail.com
