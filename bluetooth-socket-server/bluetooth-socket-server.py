import bluetooth # pylint: disable
import json
import time
import subprocess
import os
from SpectralData import SpectralData

# Global Variables
srcPath = "../data-collector/build/data-collector"
dirPath = os.path.dirname(os.path.realpath(__file__))
spectralData = SpectralData()
sendString = ""

while True:
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
            integrationTime = receivedJson['integrationTime']
            boxcarWidth = receivedJson['boxcarWidth']
            scansToAverage = receivedJson['scansToAverage']

            # Open data-collector as subprocess
            # To add boxcarWidth and scansToAverage, add "-b", str(boxcarWidth),
            # to the following
            process = subprocess.Popen([dirPath + '/' + srcPath, "-t", str(integrationTime), "-o", str(fileName)])
            returnCode = process.wait()
            print(returnCode)
            if returnCode == 0:
                # Read File made by data-collector
                jsonFile = open(str(fileName) + '.json')
                jsonData = json.load(jsonFile)

                # Collect and Process data
                if testMode == "Background":
                    tmpSpectra = jsonData['spectra']
                    tmpWavelengths = jsonData['wavelengths']
                    spectralData.setDark(tmpSpectra, tmpWavelengths)
                    sendString = SpectralData.createJson(testMode, returnCode, spectralData.darkSpectra, spectralData.darkWavelengths)

                    clientSocket.send(sendString)
                    os.remove(str(fileName) + '.json')

                
                elif testMode == "Reference":
                    tmpSpectra = jsonData['spectra']
                    tmpWavelengths = jsonData['wavelengths']
                    spectralData.setReference(tmpSpectra, tmpWavelengths)
                    if spectralData.hasBackground:
                        spectralData.subtractBackground()
                    sendString = SpectralData.createJson(testMode, returnCode,
                        spectralData.referenceSpectra, spectralData.referenceWavelengths)
                    clientSocket.send(sendString)
                    os.remove(str(fileName) + '.json')
                    
                else:
                    spectralData.setSample(jsonData['spectra'], jsonData['wavelengths'])
                    #spectralData.calculateGraph(testMode)
                    sendString = SpectralData.createJson(testMode, returnCode,
                        spectralData.sampleSpectra, spectralData.sampleWavelengths)

                    clientSocket.send(sendString)
                    os.remove(str(fileName) + '.json')
                    
            else:
                clientSocket.send("{\n\"errorCode\": " + str(returnCode) + "\n}")


    except IOError:
        print("IOERROR")
        pass

    clientSocket.close()
    serverSocket.close()
