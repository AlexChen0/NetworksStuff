import socket
import sys

#sys.stdout.write("main is fuck")
def main():
    #sys.stdout.write("main exists")
    link = sys.argv[1]
    #ensure we don't have too many redirects
    redirect = 0
    while redirect < 10:
        link = link.split('//', 1)
        #split off link, get if its http or https
        http = link[0]
        if http == "https:":
            sys.stderr.write("Secure http page, error\n")
            sys.exit(1)
        #ensure it isn't something not http
        elif len(http) < 5:
            sys.stderr.write("Input url not http\n")
            sys.exit(2)
        #split into pieces to deal with individually, see if there's a port too
        if len(link[1].split('/', 1)) == 2:
            link = link[1].split('/', 1)
            host = link[0]
            path = link[1]
            if len(path) != 0 and path[-1] == "/":
                path = path[:-1]
        else:
            link = link[1].split('/', 1)
            host = link[0]
            path = ""
        if len(host.split(":")) == 2:
            host, port = host.split(":")
            port = int(port)
        elif len(host.split(":")) > 2:
            sys.stderr.write("port number exceeds stuff\n")
            sys.exit(4) 
        else:
            port = 80  # we think LMAO

        #got from documentation
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        #sew the request together
        request = "GET /" + path + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"
        sock.sendall(request.encode())
        response = sock.recv(4096).decode("utf-8")
        responseSplit = response.split(' ')
        resCode = int(responseSplit[1])
        if resCode == 200: #ggez
            if response.find("Content-Type: text/html") != -1:
                #we're chilling
                responseSections = response.split("\r\n\r\n")
                sys.stdout.write(responseSections[-1])
                sys.exit(0)
        elif resCode >= 400:
            if response.find("Content-Type: text/html") != -1:
                responseSections = response.split("\r\n\r\n")
                sys.stdout.write(responseSections[-1])
                sys.stderr.write("response code >= 400\n")
                sys.exit(3)
        elif resCode == 301 or resCode == 302:
            if response.find("Location: ") != 1:
                link = response.split("Location: ")[1].split()[0]
                sys.stderr.write("Redirected to: " + link + "\n")
                
            pass
        redirect += 1
    sys.stderr.write("too many redirects\n")
    sys.exit(5)
        # print(response) #change to stdout later
    sock.close


if __name__ == "__main__":
    main()