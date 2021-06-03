#! /usr/bin/env python
"""
script showing how to create network configurations by combining data from CSV files with Jinja templates. 
"""

from jinja2 import Template

source_file = "switch-ports.csv"
interface_template_file = "switchport-interface-template.j2"
vlan_template_file = "vlans.j2"
switch_config = "switch-config.txt"

# String that will hold final full configuration of all interfaces
interface_configs = ""
vlan_configs = ""
interfaces_configs = ""
vlans = []

# open config file 
with open("switch-config.txt") as f:
    print("reading config file and parsing vlans")
    lines = f.read().splitlines()
    for num, line in enumerate(lines):
        if line.startswith("vlan"):
            if lines[num+1] == "!":
                continue
            temp = {}
            temp["vlan_num"] = line[5:]
            temp["vlan_name"] = lines[num+1][6:]
            vlans.append(temp)
        
        if line.startswith("interface") and "Vlan" not in line:
            counter = 1
            interfaces_config = ""
            interfaces_config += line + '\n'
            while lines[num+counter] != '!':
                interfaces_config += lines[num+counter] + '\n'
                if "description ap-" in lines[num+counter] or "description ups-" in lines[num+counter] or "description snsr-" in lines[num+counter] :
                    interfaces_config += " logging event link-status \n"
                    interfaces_config += " snmp trap link-status link-status \n"
                    interfaces_config += " power inline auto \n"
                counter = counter + 1

            interfaces_configs += interfaces_config
            interfaces_config += '\n'

# Open up the Jinja template file (as text) and then create a Jinja Template Object 
with open(vlan_template_file) as f:
    vlan_template = Template(f.read(), keep_trailing_newline=True)

    # For each row in the CSV, generate an interface configuration using the jinja template 
    for vlan in vlans:
        vlan_config = vlan_template.render(
            vlan_num = vlan["vlan_num"],
            vlan_name = vlan["vlan_name"] + '\n',

        )

        # Append this interface configuration to the full configuration 
        vlan_configs += vlan_config

# Save the final configuraiton to a file 
with open("new_config.j2", "w") as f:
    f.write(vlan_configs)
    f.write('\n')
    f.write(interfaces_configs)
