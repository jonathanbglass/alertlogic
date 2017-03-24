import requests
import logging
import json
import sys, argparse
import csv
from requests.auth import HTTPBasicAuth
"""
    Purpose:    Create a new Cloud Insight Environment
"""
def authenticate(aimurl, username, password):
    aim_req = requests.post(aimurl, auth=(username,password))
    aim_json = aim_req.json()
    aimtoken = aim_json['authentication']['token']
    account_id = aim_json['authentication']['user']['account_id']
    return aimtoken, account_id;

def main():
  aimurl = "https://api.cloudinsight.alertlogic.com/aims/v1/authenticate"
  # /environments/v1/:account_id
  # curl -X POST -d '{"type":"aws", "type_id": "123456789012", "defender_support":true, "defender_location_id":"defender-us-denver", "discover":true, "scan":false}' https://api.cloudinsight.alertlogic.com/environments/v1/account_id
  username = ''
  password = ''
  acct_type = "aws"
  parser = argparse.ArgumentParser(description='Collect username, password, and csv cile.')
  parser.add_argument('-a', '--awsaccount',  required=True, help="AWS Account ID")
  parser.add_argument('-n', '--environmentname',  required=True, help="CI AWS Account Display (aws-AWS_NAME-Account_Number)")
  parser.add_argument('-r', '--rolearn',  required=True, help="AWS Cross Account role ARN")
  parser.add_argument('-e', '--externalid',  required=True, help="AWS Cross Account external ID")
  parser.add_argument('-u', '--username', required=True)
  parser.add_argument('-p', '--password', required=True)
  args = parser.parse_args()
  aimtoken, account_id = authenticate(aimurl, args.username, args.password)
  userapiurl = "https://api.cloudinsight.alertlogic.com/environments/v1/" +account_id 
  headers = {'content-type': 'application/json', 'x-aims-auth-token': aimtoken}
  envname = "aws-" + args.environmentname + "-" + args.awsaccount
  sourcesapiurl = "https://api.cloudinsight.alertlogic.com/sources/v1/" + account_id
  '''
  sample payload:
  {
    "credential": {
      "type": "iam_role",
      "name": "Welly-AWS-Manual credentials",
      "iam_role": {
        "arn": "arn:aws:iam::AWS_ACCOUNT_ID:role/ROLE_NAME_HERE",
        "external_id": "EXTERNAL_ID"
      }   
    }
  }
  '''
  creddata = '{"credential": {"type": "iam_role", "name": "' + envname + \
    '", "iam_role": { "arn": "' + args.rolearn +'", "external_id": "' + \
    args.externalid +'"}}}'
  credapiurl = sourcesapiurl + "/credentials"
  credreq = requests.post(credapiurl, headers=headers, data=creddata)
  cred_json = credreq.json()
  cred_id = cred_json['credential']['id']
  '''
  sample payload:
  {
    "source": {
      "config": {
        "aws": {
          "credential": {
            "id": "ENTER_THE_CREDENTIALS_ID"
          },
          "discover": true,
          "scan": true,
          "account_id": "AWS_ACCOUNT_ID"
          "scope": {
                "include": [
                  {
                    "type": "vpc",
                    "key": "/aws/us-west-1/vpc/VPC_ID"
                  }
                ],
                "exclude": []
           }
        },
        "collection_method": "api",
        "collection_type": "aws"
      },   
      "enabled": true,   
      "name": "Welly-AWS-Manual",
      "product_type": "outcomes",
      "tags": [],
      "type": "environment"   
    }
  }
  '''
  srcapiurl = sourcesapiurl + "/sources"
  acctdata = '{ ' \
    ' "source": { '\
    ' "config": { '\
    ' "aws": { "credential": { "id": "' + cred_id+ '" }, ' \
    ' "discover": true, "scan": true, ' \
    ' "account_id": "' + args.awsaccount + '" ' \
    ' "scope": { "include": [ ' \
    ' { "type": "vpc", "key": "/aws/us-west-1/vpc/VPC_ID" } '\
    '], ' \
    ' "exclude": [] } }, ' \
    ' "collection_method": "api", "collection_type": "aws" }, "enabled": true, '\
    ' "name": "Welly-AWS-Manual", "product_type": "outcomes", "tags": [], '\
    ' "type": "environment" } }'
  print (acctdata)

main()
