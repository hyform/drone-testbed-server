sudo rm /vagrant/celery/celery
sudo rm /vagrant/celery/celery.conf
sudo rm /vagrant/celery/celery.service

sudo tr -d '\r' < /vagrant/celery/celery-w > /vagrant/celery/celery
sudo tr -d '\r' < /vagrant/celery/celery-w.conf > /vagrant/celery/celery.conf
sudo tr -d '\r' < /vagrant/celery/celery-w.service > /vagrant/celery/celery.service

sudo cp /vagrant/celery/celery /etc/conf.d/celery
sudo cp /vagrant/celery/celery.conf /etc/tmpfiles.d/celery.conf
sudo cp /vagrant/celery/celery.service /etc/systemd/system/celery.service

sudo systemd-tmpfiles --create

sudo systemctl disable celery.service
sudo systemctl daemon-reload
sudo systemctl enable celery.service