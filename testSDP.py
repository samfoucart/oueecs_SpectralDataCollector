import bluetooth

server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )

server_sock.bind(("", bluetooth.PORT_ANY ))
port = server_sock.getsockname()[1]
server_sock.listen(1)
print "listening on port %d" % port

uuid = "2f3b0104-fcb0-4bcf-8dda-6b06390c3c1a"
bluetooth.advertise_service( server_sock, "FooBar Service", uuid )

client_sock,address = server_sock.accept()
print "Accepted connection from ",address

try:
    while True:
        data = client_sock.recv(1024)
        print "received [%s]" % data
        data = str(int(data) * 2)
        print "now sending [%s]" % data
        client_sock.send(data)
except IOError:
    pass
        
client_sock.close()
server_sock.close()
