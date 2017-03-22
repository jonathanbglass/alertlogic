import requests
import logging
import json
import sys, argparse
import csv
from requests.auth import HTTPBasicAuth
"""
    Purpose:    Generate the list of Cloud Insight Environments
"""
def list_environments(headers, account_id):
    # collect list of environments
    apiurl = "https://api.cloudinsight.alertlogic.com/assets/v1/" +account_id + "/environments"
    r = requests.get(apiurl, headers=headers)
    r_json = r.json()
    for e in r_json['assets']: 
        if ("Defender" in e[0]['environment_name']):
            pass
        elif (e[0]['native_account_id']):
            print(e[0]['native_account_id'],e[0]['environment_name'],e[0]['environment_id'])
        elif (e[0]['account_id']):
            print(e[0]['account_id'],e[0]['environment_name'],e[0]['environment_id'])
    return;

def authenticate(aimurl, username, password):
    aim_req = requests.post(aimurl, auth=(username,password))
    aim_json = aim_req.json()
    aimtoken = aim_json['authentication']['token']
    account_id = aim_json['authentication']['user']['account_id']
    return aimtoken, account_id;

def main():
    aimurl = "https://api.cloudinsight.alertlogic.com/aims/v1/authenticate"
    username = ''
    password = ''
    parser = argparse.ArgumentParser(description='Collect username, password, and csv cile.')
    parser.add_argument('-l', '--listroles',  required=False, help="shows roles and their UUIDs", action="store_true")
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    #parser.add_argument('-c', '--csvfile',  required=True, help="CSV Fields/Headers: name, email, role_id")
    args = parser.parse_args()
    aimtoken, account_id = authenticate(aimurl, args.username, args.password)
    userapiurl = "https://api.cloudinsight.alertlogic.com/aims/v1/" +account_id + "/users"
    headers = {'content-type': 'application/json', 'x-aims-auth-token': aimtoken}
    if (args.listroles):
        print("Please copy the UUID of the role you want to assign, and place it in the 3rd field of the CSV file\n")
        list_roles(headers,account_id)
        sys.exit()
    list_environments(headers,account_id)

main()
