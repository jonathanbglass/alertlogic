import requests
import psycopg2
import logging
import json
import sys, argparse
import csv
from requests.auth import HTTPBasicAuth

"""
    Purpose:   Collect information from Threat Manager
"""

def connect_to_db():
        try: 
            conn = psycopg2.connect("dbname='db' user='dbwrite' "
                                    "host='dbhostname'")
            cur = conn.cursor()
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        except psycopg2.OperationalError as e:
            print ('Database Connection error\n{0}').format(e)
        return cur;

def hit_api(apiurl,headers,username,password,verbose):
        if (verbose):
            print(apiurl)
	r = requests.get(apiurl, auth=(username,password),headers=headers)
        if (r.status_code == 200):
            r_json = r.json()
        else:
            print("Error Code: " + str(r.status_code))
            sys.exit()
        return r_json['total_count'];

def main():
	parser = argparse.ArgumentParser(description='Collect username - User Key from console.alertlogic.net.')
	parser.add_argument('-a', '--listappliances',  required=False, help="list all appliances", action="store_true")
	parser.add_argument('-b', '--listpolicies',  required=False, help="list all policies", action="store_true")
	parser.add_argument('-c', '--listprotectedhosts',  required=False, help="list all protected hosts", action="store_true")
	parser.add_argument('-d', '--listhosts',  required=False, help="list all hosts", action="store_true")
	parser.add_argument('-o', '--outputcsv',  required=False, help="output as csv", action="store_true")
	parser.add_argument('-v', '--verbose',  required=False, help="enable debugging", action="store_true")
	parser.add_argument('-u', '--username', required=True)
	args = parser.parse_args()
	username = ''
	password = ''
	baseurl = "https://publicapi.alertlogic.com"
        if (args.verbose):
            try:
                import http.client as http_client
            except ImportError:
                import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            req_log = logging.getLogger("requests.packages.urllib3")
            req_log.setLevel(logging.DEBUG)
            req_log.propagate = True
        # Collect our Customer ID, which is required in most API calls
	getheaders = {'Accept': 'application/json'}
	postheaders = {'content-type': 'application/json'}
	password = ''
        custapiurl = "https://api.alertlogic.com/api/user/v1"
        if (args.verbose):
            print(custapiurl)
	r = requests.get(custapiurl, auth=(args.username,password),headers=getheaders)
        if (args.verbose):
            print(r.content)
            print(r.headers)
            print(r.text)
            print(r.status_code)
        if (r.status_code == 200):
            r_json = r.json()
            customerid = r_json[0]['customer_id']
            if (args.verbose): 
                print("Customer ID: " + str(customerid))
        else:
            print("Error Code: " + str(r.status_code))
            sys.exit()

        # Get a list of child accounts
        custapiurl = "https://api.alertlogic.com/api/customer/v1/" + str(customerid)
        if (args.verbose):
            print(custapiurl)
	r = requests.get(custapiurl, auth=(args.username,password),headers=getheaders)
        if (args.verbose):
            print(r.content)
            print(r.headers)
            print(r.text)
        if (r.status_code == 200):
            r_json = r.json()
            child_chain = r_json['child_chain']
            if (args.verbose): 
                print("Child Account Chain: \n\n")
                print(child_chain)
        else:
            print("Error Code: " + str(r.status_code))
            sys.exit()
        if (args.outputcsv):
            print ("AlertLogic_Customer_ID,customer_name,TM_Appliance_Count,TM_Policies_Count,TM_Protected_Hosts_Count,TM_Hosts_Count")
        else:
            # if the Prepared Statement exists, ignore the error
            cur = connect_to_db()
            try: 
                cur.execute("PREPARE overviewplan AS INSERT INTO al_overview "
                            " (al_account_id, account_name, tm_appliance_count, "
                            " tm_policies_count, tm_protected_hosts_count, "
                            " tm_hosts_count, insert_ts) "
                            " VALUES ($1, $2, $3, $4, $5, $6, $7)")
            except psycopg2.ProgrammingError as e: 
                pass
        for c in child_chain:
            # for each child account, collect metrics
            url="https://publicapi.alertlogic.com/api/tm/v1/"
            apiurl=url + str(c['customer_id']) + "/appliances"
            appcount = hit_api(apiurl,getheaders,args.username,password,args.verbose)
            apiurl=url + str(c['customer_id']) + "/policies"
            policiescount = hit_api(apiurl,getheaders,args.username,password,args.verbose)
            apiurl=url + str(c['customer_id']) + "/protectedhosts"
            phostscount = hit_api(apiurl,getheaders,args.username,password,args.verbose)
            apiurl=url + str(c['customer_id']) + "/hosts"
            hostscount = hit_api(apiurl,getheaders,args.username,password,args.verbose)
            if (args.outputcsv):
                print (str(c['customer_id'])+",\""+c['customer_name']+"\","
                    +str(appcount)+","+str(policiescount)+","
                    +str(phostscount)+","+str(hostscount))
            else:
                cur.execute("EXECUTE overviewplan (%s, %s, %s, %s, %s, %s, %s) ",
                        (c['customer_id'], c['customer_name'], appcount, policiescount,
                            phostscount, hostscount, "now()"))
        cur.close()
        sys.exit()

main()
