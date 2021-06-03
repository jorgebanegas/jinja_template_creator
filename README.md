
**jinja_template_creator

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

You should see a newly create new_config.j2 file consisting of the vlan and interfaces configurations 
