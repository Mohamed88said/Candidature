#!/bin/bash
echo "Building the application..."
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
echo "Build completed!"

# Vérifier que Redis est accessible
python -c "
import redis
import os
r = redis.from_url(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
try:
    r.ping()
    print('✅ Redis est accessible')
except:
    print('❌ Redis n est pas accessible')
"