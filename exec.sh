#! /bin/bash

if [ "$1" == "shell" ]; then
    echo -e "Opening shell ..."
    docker-compose run web python manage.py shell

elif [ "$1" == "makemigrations" ]; then
    echo -e "Making migrations ..."
    docker-compose run web python manage.py makemigrations

elif [ "$1" == "migrate" ]; then
    echo -e "Migrating ..."
    docker-compose run web python manage.py migrate

elif [ "$1" == "up" ]; then
    echo -e "Starting ..."
    docker-compose up

elif [ "$1" == "down" ]; then
    echo -e "Shutting down ..."
    docker-compose down

else
    echo -e "This command is not supported"
fi