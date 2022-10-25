import json
import requests

#prepare the http connection to Global NSX Manager
session = requests.Session()
session.verify = False
session.auth = ('admin', 'VMware1!VMware1!')
gm_nsx_mgr = 'https://gm-paris.corp.local'

#collect Services and ContextProfile Inventory
svcNprofile_path = '/global-manager/api/v1/global-infra?type_filter=Service;PolicyContextProfile'
svcNprofile_json = session.get(gm_nsx_mgr + svcNprofile_path).json()

#filter the user defined services only and store them in the user_defined_svcNprofile list
user_defined_svcNprofile = []

while svcNprofile_json["children"]:
    childsvcNprofile = svcNprofile_json["children"].pop()
    if childsvcNprofile[(list(childsvcNprofile.keys())[0])]["_system_owned"] == False:
        user_defined_svcNprofile.append(childsvcNprofile)

#Collect Groups and DFW Security Policies in Global Manager
dfw_path = '/global-manager/api/v1/global-infra?type_filter=Group;SecurityPolicy'
dfw_json = session.get(gm_nsx_mgr + dfw_path).json()

#filter the user defined policies and groups and store them in the user_defined_policies
#global DFW default policy is NOT a system defined policy, instead it is user 'admin' created policy
#because both Groups and Security Policies are under Domain's children list, if and elif is used to filter theDefault policy
user_defined_policies = []

for x in dfw_json["children"][0]["Domain"]["children"]:
	if list(x.keys())[0] == "SecurityPolicy" and x[list(x.keys())[0]]["id"]  == "Default":
		continue
	elif x[(list(x.keys())[0])]["_system_owned"] == False:
		user_defined_policies.append(x)

#create a new json for Local Manager with user defined policies + services + profiles
new_infra = {
	"resource_type": "Infra",
	"children": [
		{
			"resource_type": "ChildDomain",
			"Domain": {
				"resource_type": "Domain",
				"id": "default",
				"children": user_defined_policies
			}
		}
	]
}

new_infra["children"] += user_defined_svcNprofile

#because the objects pulled from global manager has a path 'global-infra', we are replacing it to 'infra' in their path
new_infra = json.loads(json.dumps(new_infra).replace('global-infra', 'infra'))

#Write the DFW Configuration to a JSON file that can be applied via a PATCH API call to the infra URI: '/policy/api/v1/infra'
with open("lm_dfw.json", "w") as write_file:
    json.dump(new_infra, write_file, indent = 4)
