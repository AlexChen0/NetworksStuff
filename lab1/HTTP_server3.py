from genericpath import isfile
import socket
import sys
import os
import json

def main():
    port = int(sys.argv[1])
    # check port number
    if port < 1024:
        sys.stderr.write("port number not high enough")
        sys.exit(1)
    # create acceptsocket, bind, listen
    accept = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    accept.bind(("", port))
    accept.listen(1)

    while True:
        response = b''
        #accept new connection, read HTTP request
        client, address = accept.accept()
        recvs = client.recv(4096)

        #get response
        parse = recvs.decode("utf-8").split("\r\n")
        #get html
        product = parse[0].split("?")[0]

        error = ''.encode()
        #check if product
        if product.split()[1] != "/product":
            error = 'HTTP/1.1 404 Not Found\r\n'.encode()
            response = response + error
            print(product)
            client.sendall(response)
            client.close()
            continue
        elif len(parse[0].split("?")) == 1:
            error = 'HTTP/1.1 400 Bad Request\r\n'.encode()
            response = response + error
            client.sendall(response)
            client.close()
            continue
        #check for numbers
        inputs = parse[0].split("?")[1].split()[0].split("&")
        numbers = []
        isNumber = True
        for i in inputs:
            #try-except from https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
            try:
                checkNum = i.split("=")[1]
                numbers.append(float(checkNum))
            except:
                isNumber = False
        if not isNumber:
            error = 'HTTP/1.1 400 Bad Request\r\n'.encode()
            response = response + error
            client.sendall(response)
            client.close()
            continue

        product = 1
        for i in numbers:
            product = product * i

        responseNotjson = {
            "operation": "product",
            "operands": numbers,
            "result": product
        }
        #ensure_ascii from https://stackoverflow.com/questions/18990021/why-python-json-dumps-complains-about-ascii-decoding
        responseButjson = json.dumps(responseNotjson, ensure_ascii=False).encode()
        status = 'HTTP/1.1 200 OK\r\n'.encode()
        response = response + status
        length = 'Content-Length: ' + str(len(responseButjson)) + '\r\n'
        length = length.encode()
        type = 'Connection-Type: application/json \r\n\r\n'.encode()
        response = response + length + type + responseButjson
        client.sendall(status)
        client.sendall(length)
        client.sendall(type)
        client.sendall(responseButjson)
        client.close()


if __name__ == "__main__":
    main()
