# Drone Testbed - Server
This is the server for the HyForm drone design testbed. It pairs with a Unity interface available here: https://github.com/hyform/drone-testbed-unity

## Quick Setup Guide
### Installation 
Install Vagrant  (https://www.vagrantup.com/)  
  
From the Command Prompt, navigate to the root directory of this reporitory (where this document is located) and run  
vagrant up --provision  
  
### Running HyForm
From the same Command Prompt location run  
vagrant ssh  
  
This will put you into the virtual machine. From there run  
cd /vagrant/design  
python3 manage.py runserver 0:8000  
  
Then in your browser go to  
http://localhost:8081/  
and you should see the site  
  
### Starting Django 
From root folder (with "Vagrantfile")  
  
(windows)	vagrant ssh  
(linux)		cd /vagrant/design  
(linux)		python3 manage.py runserver 0:8000  
(browser)	http://localhost:8081/  
  
  
  
  
### Stopping Django 
  
(linux)		ctrl-c  
  
  
  
### Creating Django admin user 
  
(windows)	vagrant ssh  
(linux)		cd /vagrant  
(linux)		python3 manage.py createsuperuser  
-- enter account info --  
(linux)		python3 manage.py runserver 0:8000  
  
In browser go to  
http://localhost:8081/admin  
  
  
### Logout and close VM

(linux)		logout  
(windows)	vagrant halt  


## Citing HyForm™
If you use HyForm in your own research, please cite it using this paper:

B. Song, N.F. Soria Zurita, G. Zhang, G. Stump, C. Balon, S.W. Miller, M. Yukish, J. Cagan, and C. McComb (2020). "Toward Hybrid Teams: A Platform To Understand Human-Computer Collaboration During the Design of Complex Engineered Systems." Proceedings of the Design Society: DESIGN Conference, 1, 1551-1560. [doi:10.1017/dsd.2020.68](https://doi.org/10.1017/dsd.2020.68)

## Funding
This material is based upon work supported by the Defense Advanced Research Projects Agency through cooperative agreement N66001-17-1-4064. Any opinions, findings, and conclusions or recommendations expressed in this repository are those of the contributors and do not necessarily reflect the views of the sponsors.
