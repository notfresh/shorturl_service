# Intro
This file is used to describe how to develop and debug the project locally.



# Virutal Environment
In order to use a virutal enviroment, 
in Ubuntu 20, use:
```
apt install python3.8 python3.8-venv python3-venv
```

open virtual enviroment
```
source venv/bin/activate

# then you can install dependencies 
pip install -r requirements.txt
```

to close virtual enviroment, use 
```
deactivate
```

# db init, upgrade and migrate
when you download the projects, use 
```
python manage.py db upgrade
```
to build tables in the app.sqlite, which is a local db file without running a mysql instance or other db service.


when you change some fields in any table, use 
```
python manage.py db migrate
```
to records these changes.  

