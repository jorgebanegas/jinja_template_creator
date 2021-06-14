#! /usr/bin/env python
"""
script showing how to create network template configurations using python
"""

from jinja2 import Template

vlan_template_file = "vlans.j2"
switch_config = "switch-config.txt"

# String that will hold final full configuration of all interfaces
interface_configs = ""
vlan_configs = ""
interfaces_configs = ""
vlans = []
card_counter = 1
counter1 = 1
card_list = []
card_list2 = []
card_list3 = []

x = "0"

# open config file to read the list of modules 
def statechange(num1,num2):
    if num1 == num2:
        return True
    else:
        return False

with open("switch-config.txt") as f:
    print("reading config file and parsing vlans")
    lines = f.read().splitlines()
    for num, line in enumerate(lines):
        if line.startswith("interface") and "Vlan" not in line and "FastEthernet1" not in line:
            # GigabitEthernet1/0/1 thru 48	or GigabitEthernet1/0/1-24 and interface TenGigabitEthernet 1/0/25-48
            card_number = line.split('/')[0][-1]
            card_list3.append(card_number)
            if card_number not in card_list2:
                temp = {}
                temp['card_number'] = card_number
                card_list2.append(card_number)
                card_list.append(temp)

# asking user for which set of interfaces for the port conversions
for index,card in enumerate(card_list):
    resp = input("For card #" + card_list[index]["card_number"] + " choose between the two options of interfaces GigabitEthernet1/0/1 thru 48 (1) or GigabitEthernet1/0/1-24 and interface TenGigabitEthernet 1/0/25-48 (2) 1 or 2 : ")
    card_list[index]["option"] = resp

# creating the template
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
            
        
        if line.startswith("interface") and "Vlan" not in line and "FastEthernet1" not in line:
            counter = 1
            counter2 = 1

            card_number = line.split('/')[0][-1]

            if card_number in card_list2:
                index = card_list2.index(card_number)
                if card_list[index]["option"] == "1":
                    # GigabitEthernet1/0/1 thru 48
                    try:
                        if counter1 < 49 and statechange(x,card_number):
                            line = "interface GigabitEthernet" +  str(card_number) + "/0/" + str(counter1)
                        else:
                            counter1 = 1
                            x = card_number
                            line = "interface GigabitEthernet" +  str(card_number) + "/0/" + str(counter1)
                        counter1 += 1
                    except IndexError:
                        continue
                else:
                    try:
                        if statechange(x,card_number) == False:
                            counter1 = 1
                            x = card_number

                        if counter1 < 25:
                            line = "interface GigabitEthernet" +  str(card_number) + "/0/" + str(counter1)
                        if counter1 > 24 and counter1 < 49:
                            line = "interface TenGigabitEthernet" +  str(card_number) + "/0/" + str(counter1)
                        else:
                            x = card_number
                            line = "interface GigabitEthernet" +  str(card_number) + "/0/" + str(counter1)
                        counter1 += 1
                    except IndexError:
                        continue


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
