import socket
import sys

#sys.stdout.write("main is fuck")
def main():
    #sys.stdout.write("main exists")
    link = sys.argv[1]
    link = link.split('//', 1)
    http = link[0]
    if http == "https":
        sys.stderr.write("Secure http page, error")
        sys.exit(1)
    elif len(http) < 4:
        sys.stderr.write("Input url not http")
        sys.exit(2)

    link = link[1].split('/', 1)
    host = link[0]
    path = link[1]
    if path[-1] == "/":
        path = path[:-1]
    # sys.stdout.write(path + "\n")
    port = 80  # we think LMAO
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    request = "GET /" + path + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
    # print(request)
    sock.sendall(request.encode())
    response = sock.recv(4096).decode("utf-8")
    responseSplit = response.split(' ')
    resCode = int(responseSplit[1])
    # print(resCode)
    if resCode == 200: #ggez
        if response.find("Content-Type: text/html") != -1:
            #we're chilling
            responseSections = response.split("\r\n\r\n")
            sys.stdout.write(responseSections[-1])
            sys.exit(0)
    elif resCode >= 400:
        if response.find("Content-Type: text/html") != -1:
            #we're chilling
            responseSections = response.split("\r\n\r\n")
            sys.stdout.write(responseSections[-1])
            sys.stderr.write("response code >= 400")
            sys.exit(3)
        # print(response) #change to stdout later
    sock.close


if __name__ == "__main__":
    main()