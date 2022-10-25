# Migrate-Global-DFW-to-Local-DFW

This python script pulls Global Manager's DFW policy (Groups, Services, ContextProfile, Policy & Rules). Then it creates a single JSON file for a Local manager in case of situation where you would like to offboard a LM from the GM, but still have the security policy in place for the LM.

I got this idea from Luca Camarda's original blog and python script: https://lucacamarda.wordpress.com/2020/08/20/exporting-the-nsx-t-dfw-configuration-via-the-policy-api/

Please review the code and the JSON output if you are intend to use the json output against the production environment.

Tested in:
- NSX-T 3.2.1
- Python3

*** This script would not work if you have a Group membership using a static assignment of a global segment, ports, and other global object since those objects do not exist in LM as local objects. Static membership of another nested global group is supported since this script will change the path of the global group to a local group, which will be created through this script.*** 
