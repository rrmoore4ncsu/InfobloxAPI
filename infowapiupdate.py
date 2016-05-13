#!/usr/bin/python
#    Program:  Infowapiupdate
#  
#    Date:  Feb. 22, 2016
#
#    Programmer:  Rob Moore
#
#    Purpose:   Update extensible attributes of a record in IPAM using Infoblox REST API WAPI
#
#    Input:     File with store subnets
#               
#    Output:    None
############################################################################## 
import sys
import json
import requests, base64

ADDRESS='172.20.87.30'
PATH='/wapi/v1.0/'
OBJECTTYPE='network'
CONTENTTYPE='application/json'

StoreFile = "/home/af003/files/RetailSubnets4.csv"

def get_request(usr, pas, fields=''):
    #################################################################
    #  Perform HTTP GET request. Need following:
    #
    #     URL = https://172.20.87.30/wapi/v1.0/network
    #     Data =  JSON type data for Infoblox fields
    #     Headers =  Authorization =  Basic encoded userid:password
    #                Content-type  =  application/json
    ###################################################################  
    url = "https://" + ADDRESS + PATH + OBJECTTYPE
    usrpass = usr + ":" + pas
    B64val = base64.b64encode(usrpass)
    authheader = "Basic " + B64val
    header = {"Authorization":authheader,"Content-type":CONTENTTYPE}

    response= requests.get(url, data=fields, headers=header, verify=False) 
    
    if response.status_code >= 200 and response.status_code < 300:
       success = True
    else:
       success = False 

    return(response, success)

def put_request(usr, pas, getdata, fields=''):
    #################################################################
    #  Perform HTTP PUT request. Need following:
    #
    #     URL = https://172.20.87.30/wapi/v1.0/"data from get"
    #     Data =  JSON type data for Infoblox fields
    #     Headers =  Authorization =  Basic encoded userid:password
    #                Content-type  =  application/json
    ###################################################################  
    url = "https://" + ADDRESS + PATH + getdata
    usrpass = usr + ":" + pas
    B64val = base64.b64encode(usrpass)
    authheader = "Basic " + B64val
    header = {"Authorization":authheader,"Content-type":CONTENTTYPE}

    response= requests.put(url, data=fields, headers=header, verify=False) 
    
    if response.status_code >= 200 and response.status_code < 300:
       success = True
    else:
       success = False 

    return(response, success)


def  update_network(subnet,storeno,user,passwd):
     #  First get record to update
    Dictdata = {'network':subnet}
    jsondata = json.dumps(Dictdata)
    (resp,successflag) = get_request(user,passwd,fields=jsondata)
    if successflag:
        print 'GET succesful code %s' % resp.status_code
        print (resp.json())
        requestdata = resp.json()[0]['_ref']
        print(requestdata)
    else:
        print 'GET Error message: %s' % resp.status_code
        print (resp.json()['text'])

    # Second, put record with updates
    Dictdata = {'extensible_attributes':{'Retail':'Winston-Salem','WAN Net':'Winston Data Center'},'comment':storeno}
    jsondata = json.dumps(Dictdata)
    (resp,successflag) = put_request(user,passwd,requestdata,fields=jsondata)
    if successflag:
        print 'PUT succesful code %s' % resp.status_code
        print (resp.json())
    else:
        print 'PUT Error message: %s' % resp.status_code
        print (resp.json()['text'])


def main():

    #  Prompt for userid and password
    userid = raw_input("Userid: ")
    password = raw_input("Password: ")
    
    #  Pull in each store from store file
    with open(StoreFile,'r') as Stof:
        listofstores = Stof.read().splitlines(True)
	
    #  Process each store to get store subnets	
    for storeno in listofstores:
        Storeandsubnets = storeno.split(',')
        print("Processing " + Storeandsubnets[1].strip())
        update_network(Storeandsubnets[0].strip(),Storeandsubnets[1].strip(),userid,password)



if __name__ == '__main__':
    sys.exit(main())
