import json
import time
# REMEMBER TO FOLLOW INSTRUCTIONS FOR SUBMISSION TO ADD dnspython, ADD requests, ADD maxminddb, ADD geopy
import dns
import dns.resolver
import dns.reversename
import sys
import os
import ssl
import requests
import socket
import subprocess
import maxminddb
import geopy
from geopy.geocoders import Nominatim

#copy paste python scan.py test_websites.txt test_results.json

#def DingyWorkaround(server, version):
#    result = subprocess.check_output(["openssl", "s_client", version, "-connect", server],
#      timeout=2, stderr=subprocess.STDOUT).decode("utf-8")
#    return the_lines

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
        # session = requests.Session()
        # retry = Retry(connect=3, backoff_factor=0.5)
        # adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        # session.mount('http://', adapter)
        # session.mount('https://', adapter)
        try:
            #print("fetch request")
            respheaders = requests.head('http://' + i)
            #print("get request")
        except:
            #print("fail request")
            respheaders = None
        http_server_val = None
        if respheaders is not None:
            if respheaders.headers.get('server'):
                http_server_val = respheaders.headers['server']
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
        if 'Location' in respheaders.headers:
            if respheaders.headers['Location'][0:5] == "https":
                LocalDict["redirect_to_https"] = True
            else:
                LocalDict["redirect_to_https"] = False
        else:
            LocalDict["redirect_to_https"] = False

        # hsts
        if "Strict-Transport-Security" in respheaders.headers:
            LocalDict["hsts"] = True
        else:
            LocalDict["hsts"] = False

        # # tls_versions
        # # thisSupports = []
        # # handshakeWorked = False
        # # #Bill help ^ we need to use the command that prof gave us to check if the handshake worked or not
        # # # problem is idk how to do that so uhhhh uwu
        # # if(DingyWorkaround(i, "-tls1_3")): # this line def wrong
        # #     thisSupports.append("TLSv1.3")
        # # if (DingyWorkaround("echo | openssl s_client -tls1_2 -connect " + i + ":443")[0]):  # this line def wrong
        # #     thisSupports.append("TLSv1.2")
        # # if (DingyWorkaround("echo | openssl s_client -tls1_1 -connect " + i + ":443")[0]):  # this line def wrong
        # #     thisSupports.append("TLSv1.1")
        # # if (DingyWorkaround("echo | openssl s_client -tls1_0 -connect " + i + ":443")[0]):  # this line def wrong
        # #     thisSupports.append("TLSv1.0")
        # # if (DingyWorkaround("echo | openssl s_client -ssl_2 -connect " + i + ":443")[0]):  # this line def wrong
        # #     thisSupports.append("SSLv2")
        # # if (DingyWorkaround("echo | openssl s_client -ssl_3 -connect " + i + ":443")[0]):  # this line def wrong
        # #     thisSupports.append("SSLv3")
        # # LocalDict["tls_versions"] = thisSupports
        #
        # # root_ca
        # # try:
        # #     ca = DingyWorkaround("echo | openssl s_client -connect" + i + ":443")
        # #     LocalDict["root_ca"] = ca[0]
        # # except:
        # #     LocalDict["root_ca"] = None
        #
        # rdns_names
        rdnsNames = []
        for ip in ipv4s:
            addrs = dns.reversename.from_address(str(ip))
            #print(ip, addrs)
            try:
                rdns = str(dns.resolver.resolve(addrs, "PTR")[0])
                rdnsNames.append(rdns)
            except:
                pass
            #rdnsNames.append(rdns)
        LocalDict["rdns_names"] = rdnsNames

        # rtt_range
        #rtt = stupidrtt(ipv4s)
        #returnable = [min(rtt), max(rtt)]
        #LocalDict["rtt_range"] = returnable
        rtt = []
        for x in ipv4s:
            try:
                rtt.append(ipRTT(str(x), 80, 0.5))
            except:
                try:
                    rtt.append(ipRTT(str(x), 443, 0.5))
                except:
                    try:
                        rtt.append(ipRTT(str(x), 22, 0.5))
                    except:
                        pass
        if len(rtt) > 0:
            returnable = [round(min(rtt)*1000, 0), round(max(rtt)*1000, 0)]
        else:
            returnable = None
        LocalDict["rtt_range"] = returnable
        # geo_locations owo
        # Bill help
        geo_locations = []
        coords = []
        with maxminddb.open_database('GeoLite2-City.mmdb') as reader:
            for ip in ipv4s:
                country = reader.get(str(ip))
                if country is not None:
                    coords.append([country['location']['latitude'], country['location']['longitude']])
                    #geo_locations.append(country)
#code taken from https://www.geeksforgeeks.org/get-the-city-state-and-country-names-from-latitude-and-longitude-using-python/
        # initialize Nominatim API
        geolocator = Nominatim(user_agent="geoapiExercises")
        for coord in coords:
            Latitude = coord[0]
            Longitude = coord[1]
            location = geolocator.reverse(str(Latitude) + "," + str(Longitude))
            address = location.raw['address']

            # traverse the data
            print(address)
            city = address.get('city', '')
            state = address.get('state', '')
            country = address.get('country', '')
            full_location = city + ", " + state + ", "+ country
            print(full_location)
            geo_locations.append(full_location)
        geo_locations = list(set(geo_locations))
        LocalDict["geo_locations"] = geo_locations


        theDictThatBecomesJSONLater[i] = LocalDict
    with open(outputfile, "w") as f:
        json.dump(theDictThatBecomesJSONLater, f, sort_keys=True, indent=4)
    print(outputfile)
    return 0

#code taken from https://www.pstanalytics.com/blog/advanced-analytics/python/program-for-calculating-the-round-trip-time-rtt-in-python-for-data-science/
def RTT(host):
    # Format our parameters into a tuple to be passed to the socket
    t1 = time.time()
    r = requests.get("http://" + host)
    t2 = time.time()
    return t2-t1


def ipRTT(host, port=80, timeout=40):
    # Format our parameters into a tuple to be passed to the socket
    sock_params = (host, port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Set the timeout in the event that the host/port we are pinging doesn't send information back
        sock.settimeout(timeout)
        # Open a TCP Connection
        sock.connect(sock_params)
        # Time prior to sending 1 byte
        t1 = time.time()
        sock.sendall(b'1')
        data = sock.recv(1)
        # Time after receiving 1 byte
        t2 = time.time()
        # RTT
        sock.close()
        return t2-t1
def main():
    f = sys.argv
    scan(f[1], f[2])


main()
