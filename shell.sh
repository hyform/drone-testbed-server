apt-get update
apt-get install -y python3-pip=20.0.2
apt-get install -y python3-dev=3.8.2
apt-get install -y libpq-dev=12.5
apt-get install -y postgresql=12
apt-get install -y postgresql-contrib=12
apt-get install -y nginx=1.18.0
apt-get install -y curl=7.68.0
apt-get install -y python3-django=2.2.12
apt-get install -y redis-server=5.0.7
pip3 install --upgrade pip
pip3 install gunicorn==20.0.4
pip3 install psycopg2-binary==2.8.6
pip3 install djangorestframework==3.12.2
pip3 install django-cors-headers==3.6.0
pip3 install channels==2.4.0
pip3 install channels_redis==3.2.0
pip3 install Django==3.1.4
pip3 install ortools==8.1.8487
pip3 install bleach==3.2.1
pip3 install grpcio==1.34.0
pip3 install pandas==1.1.5
pip3 install torch==1.5.1+cpu torchvision==0.6.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip3 install tabulate==0.8.7
pip3 install celery==5.0.5
sudo -u postgres psql -f /vagrant/psql-script
sudo mkdir /usr/share/ateams_service
sudo cp -r /vagrant/evaluation /usr/share/ateams_service