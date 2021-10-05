
# M-Scan  
A flask python based project for static analysis of office documents. Currently aiming to generate infographic diagrams 
from macro code and it's file structure. Currently it's under development. There any multiple updates and changes 
planned. Currently project has some basic tools loaded for office document analysis. Few points are listed below;

## Extraction of macro code  
Currently project is enable to extract macro form office document and displaying results on web UI.  
  
## Visualization of macro content  
Allot of malicious document contains macro code. In this project we'll try to achive some visualization and flow  
diagram of macro code.  
- Currently project is visualizing internal defined function function within vba code.   
- We'll expend the scope and visualize the flow of macro code instead of functions.   
     
## Office document file system structure visualization 
Project is enabled to show office document internal directory structure in web UI. This helps to view sources and files 
added into office document.
- Extraction of file system structure is in progress

Currently this project is displaying results on web UI.
  
## How to deploy   
This project is built on python 3.6.

    apt-get install p7zip-full libfuzzy-dev libpulse-dev  (sudo if required)
    git clone https://github.com/Grandayyyy/M-Scan.git
    cd M-Scan
    pip3 install requirements.txt (sudo if required)
    python3 app.py
 
 If any issue/ failure appeared during installation of project, please report.
 
 - To enable virustotal support please add virustotal public api api in  [config.ini](./config/config.ini)

    virustotal_api_key = ""
