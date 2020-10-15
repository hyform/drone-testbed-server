apt-get update
apt-get install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl python3-django
apt-get install -y redis-server
pip3 install --upgrade pip
pip3 install gunicorn psycopg2-binary djangorestframework django-cors-headers channels channels_redis
pip3 install --upgrade Django
pip3 install --upgrade ortools
pip3 install bleach
pip3 install grpcio
pip3 install pandas
pip3 install torch==1.5.1+cpu torchvision==0.6.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip3 install tabulate
pip3 install celery
sudo -u postgres psql -f /vagrant/psql-script
sudo mkdir /usr/share/ateams_service
sudo cp -r /vagrant/evaluation /usr/share/ateams_service