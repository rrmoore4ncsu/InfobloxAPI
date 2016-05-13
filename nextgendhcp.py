#!/usr/bin/python
#    Program:  NextGenDHCP
#  
#    Date:  Feb. 22, 2016
#
#    Programmer:  Rob Moore
#
#    Purpose:   Load DHCP Scopes for NextGen stores into Infoblox
#
#    Input:     None
#               
#    Output:    None
############################################################################## 

import sys
import json
import requests, base64

ADDRESS='xxx.xxx.xxx.xxx'
PATH='/wapi/v1.0/'
CONTENTTYPE='application/json'
outputFile = "/home/af003/files/infoout.txt"


def perform_request(usr, pas, object_type, fields=''):
    #################################################################
    #  Perform HTTP POST request. Need following:
    #
    #     URL = https://172.20.87.30/wapi/v1.0/"type of ojbect"
    #     Data =  JSON type data for Infoblox fields
    #     Headers =  Authorization =  Basic encoded userid:password
    #                Content-type  =  application/json
    ###################################################################  
    url = "https://" + ADDRESS + PATH + object_type
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


def create_network(storeno,subnet,netmask,vlan,user,passwd,of):
###################################################################################################
# Function:     create_network
#
# Purpose:      Create network in DHCP
#
# Variables:    Dictdata          Dictionary type data with subnet, store number, and ext. attributes
#               jsondata          JSON formatted data for above 
#               network           subnet + mask
#               octets            octet values in IP address
#               router            IP address of router
#               AlwaysTrue        Boolean value that is always true
#               APopt             Boolean flag to indicate that we need AP option for WLC
#               VOIPopt           Boolean flag to indicate that we need VOIP option for Call Managers
#               resp              Response from REST API call
#               successflag       Boolean to see if API call was successful
#                  
#
# Parameters:   storeno           Store number
#               subnet            Store subnet to add
#               netmask           Store subnet netmask
#               vlan              vlan name
#               passwd            password for Infoblox
#               of                Output File
#
# Return Value: None
#####################################################################################################

    # Get address of router and CIDR value of network
    octets = subnet.split(".")
    octets[3] = str(int(octets[3]) + 1)
    router = '.'.join(octets)
    network = subnet + "/" + str(netmask)
	
    AlwaysTrue = True
    APopt = False
    VOIPopt = False
	
    if vlan == 'Store Management':
       APopt = True



    #  Generate DHCP options to send to WAPI    
    Dictdata = {'network':network, \
	        'comment':storeno + ' ' + vlan, \
                'extensible_attributes':{'Retail':storeno,'WAN Net':'Retail'}, \
                'members': [{'_struct': 'dhcpmember','ipv4addr':'172.20.62.9','name':'retbloxmem0200c.hannaford.com'}, \
                            {'_struct': 'dhcpmember','ipv4addr':'10.200.162.140','name':'retbloxmem9073b.hannaford.com'}], \
                'options':[{'name':'routers','use_option':AlwaysTrue,'value':router,'vendor_class':'DHCP'}, \
                           {'name':'domain-name','use_option':AlwaysTrue,'value':'delhaize.com','vendor_class':'DHCP'}, \
                           {'name':'dhcp-lease-time','use_option':AlwaysTrue,'value':'604800','vendor_class':'DHCP'}, \
                           {'name':'domain-name-servers','use_option':AlwaysTrue,'value':'10.36.13.4,10.36.13.6','vendor_class':'DHCP'}]}

    #  Add adhoc DHCP options				    
    if (vlan == 'Store Wireless VOIP') or (vlan == 'Store Wired VOIP'):
        Dictdata['options'].extend([{'num':150,'value':'10.37.15.55,10.37.15.123','vendor_class':'DHCP'}])
    if vlan == 'Store Management':
        Dictdata['options'].extend([{'num':241,'value':'10.36.0.165','vendor_class':'Cisco-AP-2600'}])
		
    #  Format as JSON structure and call WAPI 
    jsondata = json.dumps(Dictdata)
    (resp,successflag) = perform_request(user,passwd,object_type='network',fields=jsondata)     
    if successflag:
        print 'Created succesfully code %s' % resp.status_code
        print (resp.json())
        of.write (resp.json())
        of.write ("Network created successfully with code: " + str(resp.status_code) + "\n")
    else:
        print 'Error code: %s' % resp.status_code
        print (resp.json()['text'])
        of.write (resp.json()['text'])
        of.write ("Error in creating network. Code: " + str(resp.status_code) + "\n")
    return()
    

def create_range(storeno,srange,erange,desc,user,passwd,of):
###################################################################################################
# Function:     create_range
#
# Purpose:      Create DHCP Range with options
#
# Variables:    Dictdata          Dictionary type data with start range, end range, comments, failover associations
#               jsondata          JSON formatted data for above 
#               resp              Response from REST API call
#               successflag       Boolean to see if API call was successful
#                  
#
# Parameters:   storeno           Store number
#               srange            Start of DHCP range
#               erange            End of DHCP range
#               desc              vlan description
#               user              userid for Infoblox
#               passwd            password for Infoblox
#               of                Output File
#
# Return Value: None
##################################################################################################### 
 
    #  Generate range options to send to WAPI 
    Dictdata =  {'start_addr':srange,  \
                 'end_addr':erange, \
                 'comment':storeno + ' ' + desc, \
                 'server_association_type':'FAILOVER',  \
                 'failover_association': 'RetScarborough-RetPortland'}
    
    #  Format as JSON structure and call WAPI
    jsondata = json.dumps(Dictdata)
    (resp, successflag) = perform_request(user,passwd,object_type='range',fields=jsondata,)
    if successflag:
        print 'Created succesfully code %s' % resp.status_code
        print (resp.json())
        of.write (resp.json())
        of.write ("Range created successfully with code: " + str(resp.status_code) + "\n")
    else:
        print 'Error code: %s' % resp.status_code
        print (resp.json()['text'])
        of.write (resp.json()['text'])
        of.write ("Error in creating range. Code: " + str(resp.status_code) + "\n")
    return()
	
	
def main():

    userid    = raw_input("Userid: ")
    password  = raw_input("Password: ")
    Store     = raw_input("Store #: ")
    StoreBase = raw_input("Store subnet: ")
    
    octetlist = StoreBase.split(".")
    outf = open(outputFile,'w')
	
    # Monitoring VLAN
    mask = 25
    Storesubnet = StoreBase
    vlanname = 'Store Monitoring'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)

    # Store VLAN
    octetlist[3] = "128"
    Storesubnet = '.'.join(octetlist)
    mask = 25
    vlanname = 'Store Stores'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)
	 
    # Store VLAN Range
    octetlist[3] = "150"
    startrange = '.'.join(octetlist)
    octetlist[3] = "190"	
    endrange = '.'.join(octetlist)
    create_range(Store,startrange,endrange,'HHU',userid,password,outf)
	
    # PCI VLAN
    octetlist[3] = "0"
    octetlist[2] = str(int(octetlist[2]) + 1)
    Storesubnet = '.'.join(octetlist)
    mask = 25
    vlanname = 'Store PCI'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)
	
    # Corporate Services VLAN
    octetlist[3] = "128"
    Storesubnet = '.'.join(octetlist)
    mask = 25
    vlanname = 'Store Corporate Services'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)
	
    # Corporate Services Range
    octetlist[3] = "245"
    startrange = '.'.join(octetlist)
    octetlist[3] = "254"	
    endrange = '.'.join(octetlist)
    create_range(Store,startrange,endrange,'Laptops',userid,password,outf)

    # Management VLAN
    octetlist[3] = "0"
    octetlist[2] = str(int(octetlist[2]) + 1)
    Storesubnet = '.'.join(octetlist)
    mask = 26
    vlanname = 'Store Management'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)
	
    # Management Range
    octetlist[3] = "33"
    startrange = '.'.join(octetlist)
    octetlist[3] = "62"	
    endrange = '.'.join(octetlist)
    create_range(Store,startrange,endrange,'APs',userid,password,outf)
	
    # Wireless VOIP VLAN
    octetlist[3] = "64"
    Storesubnet = '.'.join(octetlist)
    mask = 26
    vlanname = 'Store Wireless VOIP'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)
	
    # Wireless VOIP Range
    octetlist[3] = "67"
    startrange = '.'.join(octetlist)
    octetlist[3] = "90"	
    endrange = '.'.join(octetlist)
    create_range(Store,startrange,endrange,'Wireless Voice',userid,password,outf)
	
    # Wired VOIP VLAN
    octetlist[3] = "128"
    Storesubnet = '.'.join(octetlist)
    mask = 27
    vlanname = 'Store Wired VOIP'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)
	
    # Wired VOIP Range
    octetlist[3] = "131"
    startrange = '.'.join(octetlist)
    octetlist[3] = "158"	
    endrange = '.'.join(octetlist)
    create_range(Store,startrange,endrange,'Wired Voice',userid,password,outf)
	
    # Vendor VLAN
    octetlist[3] = "160"
    Storesubnet = '.'.join(octetlist)
    mask = 27
    vlanname = 'Store Vendor'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)

    # Pharmacy VLAN
    octetlist[3] = "192"
    Storesubnet = '.'.join(octetlist)
    mask = 27
    vlanname = 'Store Pharmacy'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)

    # Legacy Wireless VLAN
    octetlist[3] = "224"
    Storesubnet = '.'.join(octetlist)
    mask = 27
    vlanname = 'Store Wireless Legacy'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)

    # Untrusted VLAN
    octetlist[3] = "224"
    octetlist[2] = str(int(octetlist[2]) + 1)
    Storesubnet = '.'.join(octetlist)
    mask = 28
    vlanname = 'Store Untrusted'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)

    # WAAS VLAN
    octetlist[3] = "240"
    Storesubnet = '.'.join(octetlist)
    mask = 29
    vlanname = 'Store WAAS'
    create_network(Store,Storesubnet,mask,vlanname,userid,password,outf)
	
    outf.close() 

if __name__ == '__main__':
    sys.exit(main())
