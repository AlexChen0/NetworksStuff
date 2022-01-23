from genericpath import isfile
import socket
import sys
import os
def main():
    port = int(sys.argv[1])
    #check port number
    if port < 1024:
        sys.stderr.write("port number not high enough")
        sys.exit(1)
    #create acceptsocket, bind, listen
    accept = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    accept.bind(("", port))
    accept.listen()
    
    while True:
        response = b''
        #accept new connection, read HTTP request 
        client, address = accept.accept()
        recvs = client.recv(4096)

        #get response
        parse = recvs.decode("utf-8").split("\r\n")
        #get html
        paths = parse[0].split("/")[1]
        #check if file exists
        if len(paths.split(".")) < 2:
            error = 'HTTP/1.1 404 Not Found\r\n'.encode()
            response = response + error
        #check if file exists but doesn't end if .html or .htm
        elif paths.split(".")[1] != "html" or paths.split(".")[1] != "htm":
            error = 'HTTP/1.1 403 Forbidden\r\n'.encode()
            response = response + error
        #check if file is int directory
        elif os.path.isfile(os.getcwd() + paths.split(".")[1]):
            status = 'HTTP/1.1 200 OK\r\n'
            
    


if __name__ == "__main__":
    main()