import json
import requests

def dict_replace_value(d, old, new):
    x = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = dict_replace_value(v, old, new)
        elif isinstance(v, list):
            v = list_replace_value(v, old, new)
        elif isinstance(v, str):
            v = v.replace(old, new)
        x[k] = v
    return x

def list_replace_value(l, old, new):
    x = []
    for e in l:
        if isinstance(e, list):
            e = list_replace_value(e, old, new)
        elif isinstance(e, dict):
            e = dict_replace_value(e, old, new)
        elif isinstance(e, str):
            e = e.replace(old, new)
        x.append(e)
    return x

#prepare the http connection to NSX Manager
session = requests.Session()
session.verify = False
session.auth = ('admin', 'VMware1!VMware1!')
gm_nsx_mgr = 'https://gm-paris.corp.local'
lm_nsx_mgr = 'https://lm-paris.corp.local'

#collect Services Inventory
services_path = '/global-manager/api/v1/global-infra?filter=Type-Service'
services_json = session.get(gm_nsx_mgr + services_path).json()

#filter the user defined services only and store them in the user_defined_services list
user_defined_services = []

while services_json["children"]:
    childservice = services_json["children"].pop()
    if childservice["Service"]["_system_owned"] == False:
        del childservice["Service"]["children"] #This looks to be needed because the retrieved JSON have unexpected child objects for the Service Objects
        user_defined_services.append(childservice)

#collect Profiles Inventory
profiles_path = '/global-manager/api/v1/global-infra?filter=Type-PolicyContextProfile'
profiles_json = session.get(gm_nsx_mgr + profiles_path).json()

#filter the user defined profiles only and store them in the user_defined_profiles list
user_defined_profiles = []

while profiles_json["children"]:
    childprofile = profiles_json["children"].pop()
    if childprofile["PolicyContextProfile"]["_system_owned"] == False:
        user_defined_profiles.append(childprofile)

#Collect DFW configuration
dfw_path = '/global-manager/api/v1/global-infra?filter=Type-Domain|Group|SecurityPolicy|Rule'
dfw_json = session.get(gm_nsx_mgr + dfw_path).json()

user_defined_policies = []

for x in dfw_json["children"]:
	if x["id"] == "default":
		for y in x["Domain"]["children"]:
			if list(y.keys())[0] == "SecurityPolicy" and y[list(y.keys())[0]]["id"]  == "Default":
				continue
			elif y[(list(y.keys())[0])]["_system_owned"] == False:
				user_defined_policies.append(y)


#Get Local Manger's infra and default domain
lm_infra_path = '/policy/api/v1/infra?filter=Type-Domain'
lm_infra_json = session.get(lm_nsx_mgr + lm_infra_path).json()

# Put the Groups, Rules, and Security policy from global manager default domain to local 
lm_infra_json["children"][0]["Domain"]["children"] = user_defined_policies

#Add User-Defined Services and Profiles to the DFW Configuration
new_infra_children = lm_infra_json["children"] + user_defined_services + user_defined_profiles

lm_infra_json["children"] = new_infra_children

lm_dfw_json = dict_replace_value(lm_infra_json, 'global-infra', 'infra')

#Write the DFW Configuration to a JSON file that can be applied via a PATCH API call to the infra URI: '/policy/api/v1/infra'
with open("lm_dfw.json", "w") as write_file:
    json.dump(lm_dfw_json, write_file, indent = 4)
