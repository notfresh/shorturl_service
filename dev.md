# Intro
This file is used to describe how to develop and debug the project locally.



# Virutal Environment
In order to use a virutal enviroment, 
in Ubuntu 20, use:
```
apt install python3.8 python3.8-venv python3-venv
python -m venv .venv

```

open virtual enviroment
```
source .venv/bin/activate

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


# debug
```
python manage.py runserver -h 0.0.0.0 
```
# rebuild the images and re-deploy


## Method 1: Use the `--build` Option

When you run the `docker-compose up` command, you can add the `--build` option to force the rebuilding of the service's image.

```sh
docker-compose up --build
```

## Method 2: Use the `docker-compose build` Command

You can also use the `docker-compose build` command to rebuild the images before starting the services.

```sh
docker-compose build
docker-compose up
```

## Method 3: Use the `--force-recreate` Option

If you want to not only rebuild the images but also force the recreation of containers when starting the services, you can use the `--force-recreate` option.

```sh
docker-compose up --build --force-recreate
```

### Method 4: Remove Old Images and Containers

If you want to completely remove old images and containers and then rebuild and start the services, follow these steps:

1. **Stop and remove all containers**:
   ```sh
   docker-compose down
   ```

2. **Remove old images**:
   ```sh
   docker image prune -f
   docker rmi $(docker images -q)
   ```

3. **Rebuild and start the services**:
   ```sh
   docker-compose up --build
   ```
