import bluetooth
import json
import time
import subprocess
import os

serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

serverSocket.bind(("", bluetooth.PORT_ANY))
port = serverSocket.getsockname()[1]
serverSocket.listen(1)
print("listening on port", port)

uuid = "2f3b0104-fcb0-4bcf-8dda-6b06390c3c1a"
bluetooth.advertise_service(serverSocket, "spectral-data-collector", uuid)

clientSocket, address = serverSocket.accept()
print("Accepted connection from ", address)

srcPath = "../data-collector/src/"
hasCalibration = False
spectra = []
wavelengths = []
spectraCalibration = []
wavelengthsCalibration = []
spectraUncalibrated = []
wavelengthsUncalibrated = []
sendString = ""

try:
    while True:
        print("startloop")
        data = clientSocket.recv(1024)
        print("received: ", data)
        receivedJson = json.loads(data)
        print("1")
        fileName = time.time()
        print("2")
        isCalibration = receivedJson['isCalibration']
        print("3")
        integrationTime = receivedJson['integrationTime']

        if isCalibration:
            process = subprocess.Popen([srcPath + "test-collector", "-t", str(integrationTime), "-c", "-o", str(fileName)])
            returnCode = process.wait()
            print(returnCode)
            if returnCode == 0:
                jsonFile = open(str(fileName) + '.json')
                print("4")
                jsonData = json.load(jsonFile)
                print("5")
                del spectraCalibration[:]
                del spectraCalibration[:]
                print("6")
                spectraCalibration = jsonData['spectraCalibration']
                wavelengthsCalibration = jsonData['wavelengthsCalibration']
                print("7")
                hasCalibration = True
                clientSocket.send("calibratedw")
                os.remove(str(fileName) + '.json')
        
        else:
            print("nocalibration")
            process = subprocess.Popen([srcPath + "test-collector", "-t", str(integrationTime), "-o", str(fileName)])
            returnCode = process.wait()
            if returnCode == 0:
                jsonFile = open(str(fileName) + '.json')
                jsonData = json.load(jsonFile)
                del spectraUncalibrated[:]
                del wavelengthsUncalibrated[:]
                spectraUncalibrated = jsonData['spectra']
                wavelengthsUncalibrated = jsonData['wavelengths']
                if hasCalibration:
                    sendString = ""
                    for j in range(1, len(spectraUncalibrated)):
                        sendString = sendString + str(float(spectraUncalibrated[j]) - float(spectraCalibration[j])) + " "

                    sendString = sendString + "s "

                    for j in range(1, len(wavelengthsUncalibrated)):
                        sendString = sendString + str(wavelengthsUncalibrated[j]) + " "

                    sendString = sendString + "w "
                
                else:
                    sendString = ""
                    for j in range(0, len(spectraUncalibrated)):
                        sendString = sendString + str(spectraUncalibrated[j]) + " "

                    sendString = sendString + "s "

                    for j in range(0, len(wavelengthsUncalibrated)):
                        sendString = sendString + str(wavelengthsUncalibrated[j]) + " "

                    sendString = sendString + "w "

                os.remove(str(fileName) + '.json')
                print(sendString)
                clientSocket.send(sendString)



    
except IOError:
    print("IOERROR")
    pass

clientSocket.close()
serverSocket.close()
