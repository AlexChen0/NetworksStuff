from genericpath import isfile
import socket
import sys
import os
import select
import queue

def main():
    port = int(sys.argv[1])
    # check port number
    if port < 1024:
        sys.stderr.write("port number not high enough")
        sys.exit(1)
    # create acceptsocket, bind, listen, non-blocking TCP/IP socket
    #code line 16-39, 62-88 from pymotw.com/3/select
    accept = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    accept.setblocking(0)
    accept.bind(('', port))
    accept.listen(5)
    inputs = [accept]
    OC = []
    message_queues = {}
    while inputs:
        print('waiting for the next event', file=sys.stderr)
        readable, writable, exceptional = select.select(inputs, OC, inputs)
        #handles inputs
        for s in readable:
            if s is accept:
                #readable socket ready to accept connection
                connection, client_address = s.accept()
                print('  connection from', client_address,
                  file=sys.stderr)
                connection.setblocking(0)
                inputs.append(connection)
                message_queues[connection] = queue.Queue()
            else:
                data = s.recv(1024)
                if data:
                    print('  received {!r} from {}'.format(
                        data, s.getpeername()), file=sys.stderr,
                    )

                    response = b''
                    parse = data.decode("utf-8").split("\r\n")
                    empty = False
                    #get html
                    paths = parse[0].split()[1].split("/")[1]
                    if len(paths.split(".")) < 2:
                        error = 'HTTP/1.1 404 Not Found\r\n'.encode()
                        response = response + error
                        empty = True
                        # check if file exists but doesn't end if .html or .htm
                    elif paths.split(".")[1] != "html" and paths.split(".")[1] != "htm":
                        empty = True
                        error = 'HTTP/1.1 403 Forbidden\r\n'.encode()
                        response = response + error
                        # check if file is int directory
                    elif os.path.isfile(os.getcwd() + "\\" + paths):
                        paths = os.getcwd() + "\\" + paths
                        status = 'HTTP/1.1 200 OK\r\n'.encode()
                        response = response + status
                        with open(paths, 'r', encoding='utf-8') as f:
                            text = f.read()
                        text = text.encode()
                        length = 'Content-Length: ' + str(len(text)) + '\r\n'
                        length = length.encode()
                        type = 'Connection-Type: text/html; charset=UTF-8 \r\n\r\n'.encode()
                        response = response + length + type + text
                    else:
                        error = 'HTTP/1.1 404 Not Found\r\n'.encode()
                        response = response + error
                        empty = True

                    message_queues[s].put(response)

                    if empty:
                        # Interpret incorrect result as closed connection
                        print('  closing', client_address, file=sys.stderr)
                        # Stop listening for input on the connection
                        s.sendall(response)
                        exceptional.append(s)

                    if s not in OC:
                        OC.append(s)
                else:
                    # Interpret empty result as closed connection
                    print('  closing', client_address, file=sys.stderr)
                    # Stop listening for input on the connection
                    if s in OC:
                        OC.remove(s)
                    inputs.remove(s)
                    s.close()

                    # Remove message queue
                    del message_queues[s]

        # Handle outputs
        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                # No messages waiting so stop checking
                # for writability.
                print('  ', s.getpeername(), 'queue empty',
                        file=sys.stderr)
                OC.remove(s)
            else:
                print('  sending {!r} to {}'.format(next_msg,
                                                    s.getpeername()),
                        file=sys.stderr)
                s.send(next_msg)

            # Handle "exceptional conditions"
        for s in exceptional:
            print('exception condition on', s.getpeername(),
                    file=sys.stderr)
            # Stop listening for input on the connection
            inputs.remove(s)
            if s in OC:
                OC.remove(s)
            s.close()

            # Remove message queue
            del message_queues[s]


if __name__ == "__main__":
    main()
