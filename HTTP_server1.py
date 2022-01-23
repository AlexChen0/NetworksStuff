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
    
    #accept new connection, read HTTP request 
    client, address = accept.accept()
    response = client.recv(4096)
    parse = response.decode("utf-8").split("\r\n")
    paths = parse[0].split("/")[1]
    if len(paths.split(".")) < 2:
        sys.stderr.write("404") 
    elif paths.split(".")[1] != "html" or len(paths.split(".")[1] != "htm":
        sys.stderr.write("403")
    elif os.path.isfile(os.getcwd() + paths.split(".")[1]):
        os.path.isfile(os.getcwd() + paths.split(".")[1])
    


if __name__ == "__main__":
    main()