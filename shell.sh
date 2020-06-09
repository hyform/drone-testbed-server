apt-get update
apt-get install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl python3-django
pip3 install gunicorn psycopg2-binary djangorestframework django-cors-headers channels channels_redis
pip3 install --upgrade Django
pip3 install --upgrade ortools
pip3 install bleach
pip3 install grpcio
apt-get install -y postgresql postgresql-contrib
apt-get install -y redis-server
sudo -u postgres psql -f /vagrant/psql-script