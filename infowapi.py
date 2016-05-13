#!/usr/bin/python
#    Program:  Infowapi
#  
#    Date:  Feb. 22, 2016
#
#    Programmer:  Rob Moore
#
#    Purpose:   Add network into IPAM using Infoblox REST API WAPI
#
#    Input:     File with store subnets
#               
#    Output:    None
############################################################################## 
import sys
import json
import requests, base64

ADDRESS='xxx.xxx.xxx.xxx'
PATH='/wapi/v1.0/'
OBJECTTYPE='network'
CONTENTTYPE='application/json'

StoreFile = "/home/af003/files/RetailSubnets4.csv"

def perform_request(usr, pas, fields=''):
    #################################################################
    #  Perform HTTP POST request. Need following:
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

    response= requests.post(url, data=fields, headers=header, verify=False) 
    
    if response.status_code >= 200 and response.status_code < 300:
       success = True
    else:
       success = False 

    return(response, success)


def create_network(subnet,storeno,user,passwd):
    #################################################################################
    #   Create new network under Infoblox
    #
    #   Use JSON type data:
    #      Network = subnet
    #      Comment = Description of Network
    #      Extensible Attributes:  Retail  =  Store number
    #                              WAN Net =  Type of subnet(Store, DC,etc) 
    ###################################################################################
    Dictdata = {'network':subnet,'comment':storeno,'extensible_attributes':{'Retail':storeno,'WAN Net':'Retail'}}
    jsondata = json.dumps(Dictdata)
    (resp,successflag) = perform_request(user, passwd, fields=jsondata)
    if successflag:
        print 'Created succesfully code %s' % resp.status_code
        print (resp.json())
    else:
        print 'Error code: %s' % resp.status_code
        print (resp.json()['text'])


def main():
    
    userid = raw_input("Userid: ")
    password = raw_input("Password: ")
    
    #  Pull in each store from store file
    with open(StoreFile,'r') as Stof:
        listofstores = Stof.read().splitlines(True)
	
    #  Process each store to get store subnets	
    for storeno in listofstores:
        Storeandsubnets = storeno.split(',')
        print("Processing " + Storeandsubnets[1].strip())
        create_network(Storeandsubnets[0].strip(),Storeandsubnets[1].strip(),userid,password)



if __name__ == '__main__':
    sys.exit(main())
