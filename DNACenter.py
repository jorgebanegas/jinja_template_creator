# Copyright (c) {{current_year}} Cisco and/or its affiliates.

# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.0 (the "License"). You may obtain a copy of the
# License at

#                https://developer.cisco.com/docs/licenses

# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.

import requests
import json
from collections import defaultdict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.auth import HTTPBasicAuth
import time
from prettyprinter import pprint
import socket

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class Device (object):
	def __init__( self, device_id, hostname, ip, location, os, serial ):
		self.__device_id = device_id
		self.__hostname = hostname
		self.__ip = ip
		self.__location = location
		if self.__location is None:
			self.__location = 'N/A'

		self.__os_version = os
		self.__serial = serial
		self.commands = {}
		


	def get_device_id(self):
		return self.__device_id

	def get_hostname(self):
		return self.__hostname

	def get_ip(self):
		return self.__ip

	def get_location(self):
		return self.__location

	def get_os_version(self):
		return self.__os_version

	def get_serial(self):
		return self.__serial

	def print_commands(self):
		for line in self.commands:
			print(line)



class DNACenter (object):

	def __init__(self, username, password, base_url, device_ip_addresses):
		#PUBLIC Properties
		self.username = username
		self.password = password
		self.base_url = base_url
		self.device_ip_addresses = device_ip_addresses
		#PRIVATE Properies
		self.__auth_token = self.__get_auth_token()
		self.__devices = {}
		self.__device_ids = []
		self.__get_devices()
		self.__templates = dict()
		#DISABLE REQUESTS WARNINGS
		requests.packages.urllib3.disable_warnings()


	def __get_auth_token(self):
		r = requests.request("POST",'%s/dna/system/api/v1/auth/token'%self.base_url,auth=HTTPBasicAuth(self.username, self.password), verify=False)
		if r.status_code == 200:
			response = r.json()

			return response['Token']

		else:
			raise Exception(r.status_code)


	"""

	PRIVATE CLASS METHODS

	"""

	def __dna_headers(self):
		return {'Content-Type':'application/json', 'x-auth-token': self.__auth_token}



	def __get_command_runner_task(self, task_id):
		while True:
			r = requests.get("%s/dna/intent/api/v1/task/%s"%(self.base_url,task_id), headers=self.__dna_headers(), verify=False)
			response = r.json()


			if r.status_code == 200 or r.status_code == 202:
				progress = r.json()['response']['progress']


			else:
				break

			if "fileId" in progress:  # keep checking for task completion
				break

			

			
		file_id = json.loads(progress)
		file_id = file_id['fileId']
		print("FILE_ID:", file_id)



		return self.__get_cmd_output(file_id)


	def __get_cmd_output(self, file_id):
		while True:
			print("PAUSING PROGRAM FOR 10 SECONDS TO WAIT FOR COMMANDS TO PUSH OUT OF PIPELINE")
			time.sleep(10)
			r = requests.get("%s/dna/intent/api/v1/file/%s"%(self.base_url,file_id), headers=self.__dna_headers(), verify=False)
			try:
				if r.status_code == 200 or r.status_code == 202:
					response = r.json()
					print("RESPONSE LEN: ", len(response))
					print("DEVICES LEN: ", len(self.__devices))
					if len(response) < len(self.__devices):
						continue
					else:
						break
				else:
					print("EXITED WITH STATUS CODE: ", r.status_code)
					break
			except:
				continue
		if r.status_code == 200 or r.status_code == 202:
			response = r.json()
			
			return response
							

				


	def __run_show_command_on_devices(self, list_of_commands):
		"""
		Uses the Cisco DNA Center Command Runner API to run the following commands:
			*NOTE: Command Runner API allows up to 5 commands at once.*

			First Iteration:
				1. show post
				2. show inventory
				3. show power detail
				4. show platform hardware chassis power-supply detail all

			Second Iteration:
				1. show etherchannel summary
				2. show ip dhcp snooping statistics detail


		Retrives the following output from 'show post':
			1. device's (Catalyst Switch) device Uuid
			2. Component tests that were run
			3. Status (Pass/Fail) of the each individual test that was run.

		Retrieves the following output from 'show version | include Serial Number':
			1. The Component Serial Number

		

		Return Value:
			dictionary 

		"""
		chunks = [list_of_commands[x:x+5] for x in range(0, len(list_of_commands), 5)]
		i = 0
		for commands in chunks:

			payload = {
						 "name" : "command set " + str(i),
						 "commands" : commands,
						 "deviceUuids" : self.__device_ids}

			r = requests.request("POST",'%s/api/v1/network-device-poller/cli/read-request'%self.base_url, headers=self.__dna_headers(), data=json.dumps(payload), verify=False)
			response = r.json()


			if r.status_code == 200 or r.status_code == 202:
				i += 1
				yield self.__get_command_runner_task(response['response']['taskId'])

			else:

				
				yield "Error! HTTP %s Response: %s" % (r.status_code, response['response']['message'])




	def __get_devices(self):
		
		for ip_address in self.device_ip_addresses:
			print(ip_address)
			r = requests.request("GET",'%s/api/v1/network-device?managementIpAddress=%s'%(self.base_url,ip_address), headers=self.__dna_headers(), verify=False)
			if r.status_code == 200:
				for device in r.json()['response']:
					self.__device_ids.append(device['id'])
					self.__devices[device['id']] = Device(device['id'], device['hostname'], device['managementIpAddress'], device['location'], device['softwareVersion'], device['serialNumber'])


	def __get_templates(self):
		r = requests.request("GET",'%s/dna/intent/api/v1/template-programmer/template'%(self.base_url), headers=self.__dna_headers(), verify=False, timeout=10)
		if r.status_code == 200:
			for temp in r.json():
				self.__templates[temp['name']] = temp['templateId']
			return True

		else:
			return False

	def __get_template_status(self, deployment_id):
		r = requests.request("GET",'%s/dna/intent/api/v1/template-programmer/template/deploy/status/%s'%(self.base_url,deployment_id), headers=self.__dna_headers(), verify=False, timeout=10)
		if r.status_code == 200 or 202:
			pprint(r.json())
			return(r.json()['devices'][0]['status'])



	def __get_task(self,url):
			r = requests.request("GET",'%s%s'%(self.base_url,url), headers=self.__dna_headers(), verify=False)
			if r.status_code == 200 or 202:
				return r.json()['response']['id']
			else:
				print(r.text)

	def __create_template_data_ip(self,template_name,content, project_name, device_family):

		data = {
				    "author": "Automated Template",
				    "description": "this template was automated",
				    "failurePolicy": "ABORT_ON_ERROR",
				    "name": template_name,
				    "projectName": project_name,
				    "templateContent": content,
				    "softwareType": "IOS-XE",
				    "deviceTypes": [
				        {
				            "productFamily": device_family
				        }
				    ],
				    "templateParams": [],
				    'version':'1',
				}

		pprint(data)
		return data, "%s Automated Template"%template_name



	def __get_template_projects(self, project_name):
		r = requests.request("GET",'%s/dna/intent/api/v1/template-programmer/project'%(self.base_url), headers=self.__dna_headers(), verify=False)
		if r.status_code == 200 or 202:
			for template in r.json():
				if project_name == template['name']:
					return template['id']	
	"""
	
	PUBLIC CLASS METHODS

	"""


	def command_runner(self, commands):
		for data in self.__run_show_command_on_devices(commands):
			for output in data:
				devices = self.__devices
				device = devices[output['deviceUuid']]
				for key,value in output['commandResponses']['SUCCESS'].items():
					device.commands[key] = list()
					for line in output['commandResponses']['SUCCESS'][key].split("\n"):
						device.commands[key].append(line)
				





	def deploy_template(self,template_id):
		#TODO:
		for ID, device in self.__devices.items():
			payload = {
			    "targetInfo": [
			        {
			            "hostName": device.get_hostname(),
			            'type': 'MANAGED_DEVICE_UUID',
			            "id": ID,
			        }
			    ],
			    "templateId": template_id
			}

			print("deploying %s to device %s"%(template_id,device.get_hostname()))
			r = requests.request("POST",'%s/dna/intent/api/v1/template-programmer/template/deploy'%(self.base_url), headers=self.__dna_headers(), verify=False, data=json.dumps(payload), timeout=100)
			if r.status_code == 200 or 202:
				print(r.json())
				if "not deploying" in r.json()['deploymentId']:
					print("Device %s not applicable for deployment of template %s. Hence, not deploying"%(device.get_hostname(), template_id))

				else:
					print("Successfully deployed template %s to %s"%(template_id, device.get_hostname()))
					while True: 
						if "IN_PROGRESS" == self.__get_template_status(r.json()['deploymentId'].partition('Template Deployemnt Id: ')[2]):
							continue
						else:
							break
			else:
				print("Did not deploy template %s to %s"%(template_id, device.get_hostname()))

	def create_template(self,template_name, content, project_name, device_family):
		project_id = self.__get_template_projects(project_name=project_name)
		payload = self.__create_template_data_ip(template_name, content, project_name, device_family)
		r = requests.request("POST",'%s/dna/intent/api/v1/template-programmer/project/%s/template'%(self.base_url,project_id), headers=self.__dna_headers(), verify=False, data=json.dumps(payload[0]))
		print(r.text)
		if r.status_code == 200 or 202:
			return payload[1]
		else:
			print(r.text)
			return False

	def get_devices(self):
		return self.__devices

	def get_templates(self):
		self.__get_templates()
		return self.__templates

	
	def get_template_projects(self, project_name):
		r = requests.request("GET",'%s/dna/intent/api/v1/template-programmer/project'%(self.base_url), headers=self.__dna_headers(), verify=False)
		if r.status_code == 200 or 202:
			return r.json()[0]['templates']
		else:
			print(r.text)
			return False

	def commit_template(self, template_id):
		payload = {
				    "comments": "Auto-Commit",
				    "templateId": template_id
		}
		r = requests.request("POST",'%s/dna/intent/api/v1/template-programmer/template/version'%(self.base_url), headers=self.__dna_headers(), verify=False, data=json.dumps(payload))
		if r.status_code == 200 or 202:
			pprint(r.json())


	def delete_template(self, template_id):
		r = requests.request("DELETE", "%s/dna/intent/api/v1/template-programmer/template/%s"%(self.base_url, template_id), headers=self.__dna_headers(), verify=False)
		pprint(r.text)



