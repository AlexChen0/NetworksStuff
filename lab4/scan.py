import json
import time
# REMEMBER TO FOLLOW INSTRUCTIONS FOR SUBMISSION TO ADD dnspython
import dns
import dns.resolver
import sys
import os


# part 1 Scanner Framework
def scan(targetfile, outputfile):
    theDictThatBecomesJSONLater = {}
    with open(targetfile) as f:
        # note: lines is a list of strings
        # sours https://www.pythontutorial.net/python-basics/python-read-text-file/
        lines = f.readlines()
    for i in range(len(lines) - 1):
        lines[i] = lines[i][:len(lines[i]) - 1]
    #print(lines)
    for i in lines:
        LocalDict = {}
        # do the thing and put into json
        # scan_time
        LocalDict["scan_time"] = time.time()
        # ipv4 addresses
        ipv4s = dns.resolver.resolve(i, 'A')
        textipv4 = []
        for ip in ipv4s:
            textipv4.append(ip.to_text())
        #print(textipv4)
        LocalDict["ipv4_addresses"] = textipv4
        # ipv6 addresses
        try:
            ipv6s = dns.resolver.resolve(i, 'AAAA')
            textipv6 = []
            for ip in ipv6s:
                textipv6.append(ip.to_text())
            LocalDict["ipv6_addresses"] = textipv6

        except:
            LocalDict["ipv6_addresses"] = []
        # http_server
        # insecure_http
        # redirect_to_https
        # hsts
        # tls_versions
        # root_ca
        # rdns_names
        # rtt_range
        # geo_locations owo
        theDictThatBecomesJSONLater[i] = LocalDict
    print(theDictThatBecomesJSONLater)
    theJsonObject = json.dumps(theDictThatBecomesJSONLater)
    with open(outputfile, "w") as f:
        json.dump(theJsonObject, f, sort_keys=True, indent=4)
    return 0


def main():
    f = sys.argv
    scan(f[1], f[2])


main()
