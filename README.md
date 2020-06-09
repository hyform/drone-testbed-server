//-------- Installation --------------------------------------------------   
Install Vagrant  (https://www.vagrantup.com/)  
  
From the Command Prompt, navigate to the root directory of this reporitory (where this document is located) and run  
vagrant up --provision  
  
//--------- Running HyForm -----------------------------------------------  
From the same Command Prompt location run  
vagrant ssh  
  
This will put you into the virtual machine. From there run  
cd /vagrant/design  
python3 manage.py runserver 0:8000  
  
Then in your browser go to  
http://localhost:8081/  
and you should see the site  
  

  
//-------- Starting Django -------------------------------------------------  
  
From root folder (with "Vagrantfile")  
  
(windows)	vagrant ssh  
(linux)		cd /vagrant/design  
(linux)		python3 manage.py runserver 0:8000  
(browser)	http://localhost:8081/  
  
  
  
  
//-------- Stopping Django --------------------------------------------------  
  
(linux)		ctrl-c  
  
  
  
//-------- Creating Django admin user ---------------------------------------  
  
(windows)	vagrant ssh  
(linux)		cd /vagrant  
(linux)		python3 manage.py createsuperuser  
-- enter account info --  
(linux)		python3 manage.py runserver 0:8000  
  
In browser go to  
http://localhost:8081/admin  
  
  
//-------- Logout and close VM ----------------------------------------------  
  
(linux)		logout  
(windows)	vagrant halt  