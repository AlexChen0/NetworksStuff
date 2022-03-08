import json
import time
# REMEMBER TO FOLLOW INSTRUCTIONS FOR SUBMISSION TO ADD dnspython, ADD requests
import dns
import dns.resolver
import dns.reversename
import sys
import os
import ssl
import requests
import socket

def DingyWorkaround(cmd_to_run):
    '''Returns a bytearray of command output'''
    os.system(cmd_to_run + " > OwO.uwu")
    temp_file = open("OwO.uwu", "r")
    the_lines = temp_file.readlines()
    os.remove("OwO.uwu")
    return the_lines

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
        respheaders = dict(requests.get(i).headers)
        http_server_val = None
        if respheaders.has_key("Server"):
            http_server_val = respheaders["Server"]
        LocalDict["http_server"] = http_server_val

        # insecure_http
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((i, 80))
            s.shutdown(2)
            LocalDict["insecure_http"] = True
        except:
            LocalDict["insecure_http"] = False

        # redirect_to_https
        if "Connection" in respheaders and respheaders["Connection"] == "upgrade" and "Upgrade" in respheaders:
            LocalDict["redirect_to_https"] = True
        else:
            LocalDict["redirect_to_https"] = False

        # hsts
        if "Strict-Transport-Security" in respheaders:
            LocalDict["hsts"] = True
        else:
            LocalDict["hsts"] = False

        # tls_versions
        thisSupports = []
        handshakeWorked = False
        #Bill help ^ we need to use the command that prof gave us to check if the handshake worked or not
        # problem is idk how to do that so uhhhh uwu
        if(DingyWorkaround("echo | openssl s_client -tls1_3 -connect " + i + ":443")[0]): # this line def wrong
            thisSupports.append("TLSv1.3")
        if (DingyWorkaround("echo | openssl s_client -tls1_2 -connect " + i + ":443")[0]):  # this line def wrong
            thisSupports.append("TLSv1.2")
        if (DingyWorkaround("echo | openssl s_client -tls1_1 -connect " + i + ":443")[0]):  # this line def wrong
            thisSupports.append("TLSv1.1")
        if (DingyWorkaround("echo | openssl s_client -tls1_0 -connect " + i + ":443")[0]):  # this line def wrong
            thisSupports.append("TLSv1.0")
        if (DingyWorkaround("echo | openssl s_client -ssl_2 -connect " + i + ":443")[0]):  # this line def wrong
            thisSupports.append("SSLv2")
        if (DingyWorkaround("echo | openssl s_client -ssl_3 -connect " + i + ":443")[0]):  # this line def wrong
            thisSupports.append("SSLv3")
        LocalDict["tls_versions"] = thisSupports

        # root_ca
        try:
            ca = DingyWorkaround("echo | openssl s_client -connect" + i + ":443")
            LocalDict["root_ca"] = ca[0]
        except:
            LocalDict["root_ca"] = None

        # rdns_names
        rdnsNames = []
        for ip in ipv4s:
            rdnsNames.append(str(dns.resolver.resolve(str(dns.reversename.from_address(ip))), "PTR")[0])
        LocalDict["rdns_names"] = rdnsNames

        # rtt_range
        rtt = stupidrtt(ipv4s)
        returnable = [min(rtt), max(rtt)]
        LocalDict["rtt_range"] = returnable

        # geo_locations owo
        # Bill help

        theDictThatBecomesJSONLater[i] = LocalDict
    print(theDictThatBecomesJSONLater)
    theJsonObject = json.dumps(theDictThatBecomesJSONLater)
    with open(outputfile, "w") as f:
        json.dump(theJsonObject, f, sort_keys=True, indent=4)
    return 0

def stupidrtt(iplst):
    rttlist = []
    for ipman in iplst:

        for portman in [80, 22, 443]:
            infolines = DingyWorkaround("sh -c \"time echo -e '\x1dclose\x0d' | telnet " + ipman + " " + portman + "\"")
            worked = False
            for l in infolines:
                if "real" in l:
                    # parse integer out, look at lab4 rtt section
                    # Bill help
                    worked = True
            if worked:
                break
    # convert to ms
    # Bill help
    return rttlist

def main():
    f = sys.argv
    scan(f[1], f[2])


main()
