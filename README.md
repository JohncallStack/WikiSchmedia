# WikiShmedia 
WikiShmedia is a wikipedia searchengine running on 3 Virtual Machines. 

# Requirements
VM1, VM2 and EC2VM must be running in order for the web application to run. The container
mysqlcontainer must be running on VM2 in order to contact the database. The system requirements 
for the application itself are contained within the [requirements.txt](requirements.txt) file which must remain within the project. 
You must install these dependencies in order to run the application.  

# Configuration
VM1 contains the application, VM2 contains the MySQL database and the EC2 VM conducts the wikipedia search if prompted. Once a search is made the
application will check the database on VM2 to see if the search has been cached before. If it has been it will return this result. If it hasn't it will 
contact the EC2 VM to conduct a new search. This search will then be displayed and cached on VM2.
VM1 and VM2 must be on the same network in order for the app to connect to the Database.The container on VM2 must accesible to the app on port 7888, 
so be sure to open up this port on your port forwarding settings for VM2. Also make sure that both VMs can listen on port 22 for SSH.  

# Running the Program
To run the program open up the terminal in the project folder (JSAssignment1) and use the bash command "python3 main.py"
Then open up browser on your local machine and navigate to http://127.0.0.1:8888/ Then simply enter your search.

# Migrating the Project to Another System
In order to migrate the project to another system you will need to edit the main.py file accordingly with the new network settings.
And make sure to setup network settings for the respective VMs accordingly. 