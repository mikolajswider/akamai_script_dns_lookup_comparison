#!/usr/bin/python3

import json
import dns.resolver
import time

"""
The script compares DNS outputs for a given list of domains.\n
Domains are input in as a text file, in json format.\n
For each and every domain, the script issues two DNS requests, one with no additional parameters, the second one with a specified custom DNS server.\n
Contributors:\n
Miko (mswider@akamai.com) as Chief Programmer\n
\n dns_lookup_comparison.py v1.0
"""

def main():

    print("\nThe script compares DNS outputs for a given list of domains.\nDomains are input as a text file, in json format.\nFor each and every domain, the script issues two DNS requests, one with a specified custom DNS server.\nContributors:\nMiko (mswider@akamai.com) as Chief Programmer\ndns_lookup_comparison.py v1.0")
    pass_int = 1
    fail_counter = 0
    counter = 0
    # defining inputs
    ifile = input("\nProvide the input text file name (without .txt extension): ")
    dns_server = input("\nProvide your custom DNS Server IP address: ")
    log_activation = input("\nDo you want to enable logs? (y/n) ")

    # defining custom resolver
    custom_resolver = dns.resolver.Resolver()
    custom_resolver.nameservers = [dns_server]

    # opening input.txt and output.txt files
    input_file = open(str(ifile)+'.txt','r', encoding='utf-8')
    json_input = json.loads(input_file.readline())
    record_list = json_input["recordsets"]
    #print(record_list)
    for record in record_list:
        time.sleep(1)
        #print(record)
        counter =counter + 1
        try:
            output1 = (dns.resolver.query(record["name"],record["type"], raise_on_no_answer=False))
            output2 = (custom_resolver.query(record["name"],record["type"], raise_on_no_answer=False))
        except dns.exception.Timeout:
           print("\nTest FAILED for " + str(record["name"]) + " because of DNS Timeout.")
           pass_int = pass_int*0
           fail_counter = fail_counter + 1
        else:
            if output1.rrset != output2.rrset:
                pass_int = pass_int*0
                fail_counter = fail_counter + 1
                print("\nTest FAILED for " + str(record["name"]) + " domain while using " + str(dns_server) + " custom DNS server.\n \nRegular Lookup: \n" + str(output1.rrset) +  "\nCustom Lookup: \n" + str(output2.rrset))
            else:
                if log_activation == "y":
                    print("\nTest PASSED for "+ str(record["name"]) + " domain. Both DNS servers returned: \n"+ str(output1.rrset))
    print("\nProcessed all " + str(counter) + " domains.")
    if pass_int == 1:
        print("\nTest PASSED for all domains while using " + str(dns_server) + " custom DNS server. \n")
    else:
        print("\nTest FAILED for " + str(fail_counter) + " domains while using " + str(dns_server) + " custom DNS server. \n")

    # closing input.txt and output.txt files
    input_file.close()

if __name__ == '__main__':
    main()
