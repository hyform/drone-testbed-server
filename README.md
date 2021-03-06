# Drone Testbed - Server
This is the server for the HyForm™ drone design testbed. It pairs with a Unity interface available here: https://github.com/hyform/drone-testbed-unity

## Quick Setup Guide
### Starting Notes
These instructions are for setting up a Linux virtual machine on Windows. For clarity, some commands are preceded by what environment you type them in  
```
(windows) This command is entered on a Windows command line  
(linux) This command is entered in the Linux vm  
(browser) This address is entered in a browser, usually from your Windows machine  
```
  

### Installation 
Install Virtualbox  (https://www.virtualbox.org/)  
Install Vagrant  (https://www.vagrantup.com/)  
  
From a Windows Command Prompt, navigate to the root directory of the distribution (where this document is located) and run  
```
vagrant up --provision --provider=virtualbox
```    
  

### Running HyForm™ for the first time
From the same Command Prompt location run  
```
vagrant ssh  
```
  
This will put you into the virtual machine. From there run  
```
cd /vagrant/design  
python3 manage.py migrate  
python3 manage.py runserver 0:8000  
```  

Then in your browser go to  
```
http://localhost:8081/  
```
and you should see the site  
  
An initial set of users and passwords is included in the file initial-users.txt  
Log in with the Experimenter and create a new Session to get started  
  

### Starting Django 
From root folder (with "Vagrantfile")  
Note: commands run from a windows command prompt are marked with (windows), those run from the vagrant virtual machine are marked with (linux) and browser links are (browser)  
  
```
(windows)	vagrant ssh  
(linux)		cd /vagrant/design  
(linux)		python3 manage.py runserver 0:8000  
(browser)	http://localhost:8081/  
```  


### Stopping Django 
```  
(linux)		ctrl-c  
```  
  
  
### Creating Django admin user 
```  
(windows)	vagrant ssh  
(linux)		cd /vagrant/design  
(linux)		python3 manage.py createsuperuser  
-- enter account info --  
(linux)		python3 manage.py runserver 0:8000  
```  
In browser go to  
```
http://localhost:8081/admin  
```  
  

### Logout and close VM
```
(linux)		logout  
(windows)	vagrant halt  
```


## Using HyForm™
In the initial-users.txt file of the distribution you will find the basic user accounts included with the system. The two types included are Experimenters and regular Users (also called Players). Initially, only an Experimenter can log into the site. The Players can only log in when there is an active session running that they have access to. When an Experimenter logs into the site, they are presented with the Experimenter interface. Here, they can create and manage sessions which the players participate in.  
  
To get started, log in as the Experimenter and create a session. Once you start a session, the users in the team associated with that session can log in.  
Note that each session is tied to a team, and only one session for a team can be active at once.  
  

## Citing HyForm™
If you use HyForm in your own research, please cite it using this paper:

> B. Song, N.F. Soria Zurita, G. Zhang, G. Stump, C. Balon, S.W. Miller, M. Yukish, J. Cagan, and C. McComb (2020). "Toward Hybrid Teams: A Platform To Understand Human-Computer Collaboration During the Design of Complex Engineered Systems." Proceedings of the Design Society: DESIGN Conference, 1, 1551-1560. [doi:10.1017/dsd.2020.68](https://doi.org/10.1017/dsd.2020.68)
  

## Funding
This material is based upon work supported by the Defense Advanced Research Projects Agency through cooperative agreement N66001-17-1-4064. Any opinions, findings, and conclusions or recommendations expressed in this repository are those of the contributors and do not necessarily reflect the views of the sponsors.
