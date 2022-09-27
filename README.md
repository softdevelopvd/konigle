# Update configure .env
    .env
# Setup django app
    // virtualenv backend_env
    // source backend_env/bin/activate
    // pip3 install -r requirements.txt
    // python3 manage.py migrate
    // python3 manage.py runserver
# Run celery worker
    // celery -A konigle worker -l info --logfile=celery.log --detach
# Run celery beat on regular schedule
    // celery -A konigle.celery beat