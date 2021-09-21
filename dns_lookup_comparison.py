#!/usr/bin/python3
import json
import dns.resolver
import requests
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urljoin
import re
import os
import argparse
import configparser
import dns.resolver
import time

def main():

    pass_int = 1
    fail_counter = 0
    counter = 0

    # defining inputs & argparse
    parser = argparse.ArgumentParser(prog="dns_lookup_comparison.py v2.0", description="The dns_lookup_comparison.py script compares DNS outputs for a given list of domains.\nDomains are retrieved by an API Call during the execution of the script.\nFor each and every domain, the script issues two DNS requests, one with a specified custom DNS server.\nContributors:\nMiko (mswider) as Chief Programmer")
    parser.add_argument("zone", default=None, type=str, help="DNS Zone to be tested")
    parser.add_argument("custom_server_IP", default=None, type=str, help="Custom DNS Server IP address")
    env_edgerc = os.getenv("AKAMAI_EDGERC")
    default_edgerc = env_edgerc if env_edgerc else os.path.join(os.path.expanduser("~"), ".edgerc")
    parser.add_argument("--edgerc_path", help="Full Path to .edgerc File including the filename", default=default_edgerc)
    env_edgerc_section = os.getenv("AKAMAI_EDGERC_SECTION")
    default_edgerc_section = env_edgerc_section if env_edgerc_section else "default"
    parser.add_argument("--section", help="Section Name in .edgerc File", required=False, default=default_edgerc_section)
    parser.add_argument("--switchkey", default="", required=False, help="Account SwitchKey")
    parser.add_argument("--enable_logs", default='False', required=False, help="Enable Logs", choices=['True', 'False'],)
    args = parser.parse_args()

    enable_logs = args.enable_logs
    dns_server = args.custom_server_IP
    section = args.section
    edgerc_path = args.edgerc_path
    switchkey = args.switchkey
    zone = args.zone

    # defining custom resolver
    custom_resolver = dns.resolver.Resolver()
    custom_resolver.nameservers = [dns_server]

    # setting up authentication as in https://github.com/akamai/AkamaiOPEN-edgegrid-python
    try:
        edgerc = EdgeRc(edgerc_path)
        baseurl = 'https://%s' % edgerc.get(section, "host")
    except configparser.NoSectionError:
        print("\nThe path to the .edgerc File or the Section Name provided is not correct. Please review your inuputs.\n")
    else:
        http_request = requests.Session()
        http_request.auth = EdgeGridAuth.from_edgerc(edgerc, section)
        # setting up request headers
        headers = {}
        headers['PAPI-Use-Prefixes'] = "true"
        http_request.headers = headers
        http_response = http_request.get(urljoin(baseurl, "/config-dns/v2/zones/"+zone+"/recordsets?showAll=true&accountSwitchKey="+switchkey))
        http_status_code= http_response.status_code
        http_content= json.loads(http_response.text)
        # Checking the first API call response code to avoid any exceptions further on ...
        if http_status_code == 200:

            record_list = http_content["recordsets"]
            
            #print(record_list)
            for record in record_list:
                time.sleep(1)
                #print(record)
                counter =counter + 1
                try:
                    output1 = (dns.resolver.resolve(record["name"],record["type"], raise_on_no_answer=False))
                    output2 = (custom_resolver.resolve(record["name"],record["type"], raise_on_no_answer=False))
                    
                except dns.exception.Timeout:
                    print("\nTest FAILED for " + str(record["name"]) + " domain, " + str(record["type"]) + " record type, because of DNS Timeout.")
                    pass_int = pass_int*0
                    fail_counter = fail_counter + 1
                
                except dns.rdatatype.UnknownRdatatype:
                    print("\nTest FAILED for " + str(record["name"]) + " domain, " + str(record["type"]) + " record type, because of non standard DNS record type.")
                    pass_int = pass_int*0
                    fail_counter = fail_counter + 1
                
                except dns.resolver.NoNameservers:
                    print("\nTest FAILED for " + str(record["name"]) + " domain, " + str(record["type"]) + " record type, because all nameservers failed to answer the query.")
                    pass_int = pass_int*0
                    fail_counter = fail_counter + 1    
                
                except dns.resolver.NXDOMAIN:
                    print("\nTest FAILED for " + str(record["name"]) + " domain, " + str(record["type"]) + " record type, because of non existent domain.")
                    pass_int = pass_int*0
                    fail_counter = fail_counter + 1
                
                else:
                    if output1.rrset != output2.rrset:
                        pass_int = pass_int*0
                        fail_counter = fail_counter + 1
                        print("\nTest FAILED for " + str(record["name"]) + " domain, " + str(record["type"]) + " record type, while using " + str(dns_server) + " custom DNS server.\n \nRegular Lookup: \n" + str(output1.rrset) +  "\nCustom Lookup: \n" + str(output2.rrset))
                    else:
                        if enable_logs == "True":
                            print("\nTest PASSED for "+ str(record["name"]) + " domain, " + str(record["type"]) + " record type. Both DNS servers returned: \n"+ str(output1.rrset))
            print("\nProcessed all " + str(counter) + " domains.")
            if pass_int == 1:
                print("\nTest PASSED for all domains while using " + str(dns_server) + " custom DNS server. \n")
            else:
                print("\nTest FAILED for " + str(fail_counter) + " domains while using " + str(dns_server) + " custom DNS server. \n")

        else:
            print("\nAPI Call Failure")
            print(http_response.text)

if __name__ == '__main__':
    main()
