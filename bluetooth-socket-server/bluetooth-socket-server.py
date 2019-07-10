import bluetooth
import json
import time
import subprocess
import os

# Global Variables
srcPath = "../data-collector/src/test-collector"
hasDark = False
sample = []
wavelengths = []
spectraDark = []
wavelengthsDark = []
spectraReference = []
wavelengthsReference = []
sendString = ""

# Define Server Socket on RFCOMM
serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
serverSocket.bind(("", bluetooth.PORT_ANY))
# Listen on port 1
port = serverSocket.getsockname()[1]
serverSocket.listen(1)
print("listening on port", port)

# Advertise Socket
uuid = "2f3b0104-fcb0-4bcf-8dda-6b06390c3c1a"
bluetooth.advertise_service(serverSocket, "spectral-data-collector", uuid)

# Wait for client to connect
clientSocket, address = serverSocket.accept()
print("Accepted connection from ", address)

# Main Loop
try:
    while True:
        # Read from Json sent from client
        data = clientSocket.recv(1024)
        receivedJson = json.loads(data)
        fileName = time.time()
        testMode = receivedJson['testMode']
        isDark = receivedJson['isDark']
        isReference = receivedJson['isReference']
        isTest = receivedJson['isTest']
        integrationTime = receivedJson['integrationTime']
        collectionMode = receivedJson['collectionMode']

        # Collect and Process data
        if testMode is "dark":
            process = subprocess.Popen([srcPath, "-t", str(integrationTime), "-c", "-o", str(fileName)])
            returnCode = process.wait()
            print(returnCode)
            if returnCode == 0:
                jsonFile = open(str(fileName) + '.json')
                jsonData = json.load(jsonFile)
                del spectraDark[:]
                del spectraDark[:]
                spectraDark = jsonData['spectraCalibration']
                wavelengthsDark = jsonData['wavelengthsCalibration']
                hasDark = True
                sendString = "{\n\t\"testMode\": "
                sendString = sendString + str(testMode) + ",\n\t\"errorCode\": "
                sendString = sendString + 0 + ",\n\t\"wavelengths\": ["
                for i in range(len(wavelengthsDark) - 1):
                    sendString = sendString + str(wavelengthsDark[i]) + ", "
                
                sendString = sendString + str(wavelengthsDark[len(wavelengthsDark) - 1])
                sendString = sendString + "],\n\t\"sample\": ["
                for i in range(len(wavelengthsDark) - 1):
                    sendString = sendString + str(wavelengthsDark[i]) + ", " 
                sendString
                clientSocket.send("{\n\"calibrated")
                os.remove(str(fileName) + '.json')
        
        else:
            print("nocalibration")
            process = subprocess.Popen([srcPath, "-t", str(integrationTime), "-o", str(fileName)])
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
