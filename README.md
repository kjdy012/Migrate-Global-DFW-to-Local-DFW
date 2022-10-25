# Migrate-Global-DFW-to-Local-DFW
*** This script would not work if you have a Group membership using a static assignment of a global segment, ports, and other global object since those objects do not exist in LM as local objects. Static membership of another nested global group is supported since this script will change the path of the global group to a local group, which will be created through this script.*** 

This python script pulls a NSX-T Global Manager's DFW policy (Groups, Services, ContextProfile, Policy & Rules), then it creates a single JSON file to run against the Local manager in case of situation where you would like to offboard LM from the GM, but still have the security policy in place for LM. Script does not change anything to the environment. It only uses API calls to get the GM objects.

This json output can be used as a PATCH API call on the LM: ['https://{LM/NSXT_mgr}/policy/api/v1/infra']

This is possible through NSX-T's policy driven API. You can find more information on the NSX hierarchical API here: https://blogs.vmware.com/networkvirtualization/2020/06/navigating-nsxt-policy-apis.html/

I got this idea from Luca Camarda's original blog and python script: https://lucacamarda.wordpress.com/2020/08/20/exporting-the-nsx-t-dfw-configuration-via-the-policy-api/

Please review the code and the JSON output if you are intend to use the json output against the production environment.

Tested in:
- NSX-T 3.2.1
- Python3
