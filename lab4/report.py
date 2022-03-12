import texttable
# ADD texttable
import json
import sys
from collections import Counter

def makeReport(targetfile, outputfile):
    with open(targetfile) as file:
        data = json.load(file)
    print(type(data))
    keys = data.keys()
    dict_keys = list(data.keys())
    table = texttable.Texttable()
    table.set_deco(texttable.Texttable.HEADER)
    table.set_cols_dtype(['t',  # website
                          'a',  # scan_time
                          'a',  # ipv4_addresses
                          'a',  # ipv6_addresses
                          'a',  # http_server
                          'a',  # insecure_http
                          'a',  # redirect_to_https
                          'a',  # hsts
                          'a',  # rdns_names
                          'a',  # rtt_range
                          'a',  # geo_locations
                           ])
    table.set_cols_align(["l", "l", "l", "l", "l", "l", "l", "l", "l", "l", "l"])
    table.set_max_width(0)
    table.add_rows([["Website", "scan_time", "ipv4_addresses", "ipv6_addresses", "http_server",
                     "insecure_http", "redirect_to_https", "hsts", "rdns_names", "rtt_range", "geo_locations"]])
    web_server = []
    plain_http = 0
    https = 0
    hsts = 0
    ipv6 = 0
    minRTT = []
    indexes = []
    for i in keys:
        table.add_row([i, data[i]["scan_time"], data[i]["ipv4_addresses"], data[i]["ipv6_addresses"], data[i]["http_server"],
                       data[i]["insecure_http"], data[i]["redirect_to_https"], data[i]["hsts"], data[i]["rdns_names"], data[i]["rtt_range"], data[i]["geo_locations"]])
        web_server.append(data[i]["http_server"])
        plain_http += data[i]["insecure_http"]
        https += data[i]["redirect_to_https"]
        hsts += data[i]["hsts"]
        if len(data[i]["ipv6_addresses"]) != 0:
            ipv6 += 1
        if data[i]["rtt_range"] is not None:
            minRTT.append(data[i]["rtt_range"][0])
        else:
            minRTT.append(999)

    for i in range(len(minRTT)):
        indexes.append([minRTT[i], i])
    indexes.sort()
    sort_index = []

    for x in indexes:
        sort_index.append(x[1])


    result = [item for items, c in Counter(web_server).most_common()
              for item in [items] * c]
    no_dups = []
    [no_dups.append(x) for x in result if x not in no_dups]
    webtable = texttable.Texttable()
    webtable.set_cols_align(["l", "l"])
    webtable.set_cols_valign(["a", "a"])
    webtable.add_row(["Web Server", "Frequency"])
    for i in no_dups:
        webtable.add_row([i, web_server.count(i)])

    percentagetable = texttable.Texttable()
    percentagetable.set_cols_align(["l", "l"])
    percentagetable.set_cols_valign(["a", "a"])
    percentagetable.add_row(["Domain", "Percentage"])
    percentagetable.add_row(["plain http", plain_http / len(keys) * 100])
    percentagetable.add_row(["https redirect", https / len(keys) * 100])
    percentagetable.add_row(["hsts", hsts / len(keys) * 100])
    percentagetable.add_row(["ipv6", ipv6 / len(keys) * 100])

    RTTTable = texttable.Texttable()
    RTTTable.set_cols_align(["l", "l"])
    RTTTable.set_cols_valign(["a", "a"])
    RTTTable.add_row(["Domain", "RTT Range"])
    for i in sort_index:
        RTTTable.add_row([dict_keys[i], data[dict_keys[i]]["rtt_range"]])

    text_file = open(outputfile, "w", encoding="utf-8")
    text_file.write(table.draw())
    text_file.write(webtable.draw())
    text_file.write(percentagetable.draw())
    text_file.write(RTTTable.draw())

    text_file.close()
    return 0

def main():
    f = sys.argv
    makeReport(f[1], f[2])


main()