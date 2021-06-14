
# jinja_template_creator

script that reads a config file then creates a jinja template based on the information from the config file

Contacts:

* Jorge Banegas ( jbanegas@cisco.com )

**Requirements**
- Python3
- Switch config file inside project folder and name it switch-config.txt

**Source Installation**

Create and enter virtual environment

```bash
virtualenv env
source env/bin/activate
```

Install project dependencies

```bash
pip install -r requirements.txt
```

Be sure to include config file inside the project folder and name it switch-config.txt

Run python script

```bash
python config_render.py
```

You should see a newly create new_config.j2 file consisting of the vlan and interfaces configurations.

After the new_config.j2 file is generated. Now we can upload the template over the DNA Center

```python

# converter.py 

#TODO: Setting deploy to False will only create the template in DNAC
# Setting deploy to True will deploy the template to devices specified under the NETWORK variable
deploy = False

#TODO: ENTER THE IP ADDRESS(S) OF DEVICES TO TARGET WITH TEMPLATE DEPLOYMENT
NETWORK = ["192.168.1.1"]
#TODO: ENTER DNAC USERNAME
USERNAME = ""
#TODO: ENTER DNAC PASSWORD
PASSWORD = ""
#ENTER DNAC BASE URL
BASE_URL = ""

#TODO: Enter the DNAC template project name 
TEMPLATE_PROJECT_NAME = "ENTER DNAC PROJECT NAME HERE"

#TODO: Enter Device Family
"""
Examples of device familes:

Routers
Switches and Hubs
Wireless Sensor
Unified AP	
"""
TEMPLATE_DEVICE_FAMILY = "ENTER DEVICE FAMILY HERE"


#TODO: Enter DNAC template name
DNAC_TEMPLATE_NAME = 'TEMPLATE NAME'

#Points to the jinja template file
JINJA_TEMPLATE = 'jinja_template.txt'
#Points to the YAML config file
YAML_TEMPLATE = 'new_config.yaml'

```
After changing the necessary information run the script using:


    $ python converter.py

Once, you log into your DNAC instance, you should be able to see the newly created template under the project folder you declared. 
