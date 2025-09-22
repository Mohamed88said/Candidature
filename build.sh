#!/bin/bash
echo "Building the application..."
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
echo "Build completed!"