import json
import time
import subprocess
import os

srcPath = "../../data-collector/src/"
fileName = time.time()
integrationTime = 5
isCalibration = True
#spectra = []
#wavelengths = []
spectraCalibration = []
wavelengthsCalibration = []
spectraUncalibrated = []
wavelengthsUncalibrated = []
sendString = ""

for i in range(1,3):
    print(i)
    if isCalibration:
        process = subprocess.Popen([srcPath + "test-collector", "-t", str(integrationTime), "-c", "-o", str(fileName)])
        returnCode = process.wait()
        if returnCode == 0:
            jsonFile = open(str(fileName) + '.json')
            print(jsonFile)
            jsonData = json.load(jsonFile)
            del spectraCalibration[:]
            del wavelengthsCalibration[:]
            spectraCalibration = jsonData['spectraCalibration']
            wavelengthsCalibration = jsonData['wavelengthsCalibration']
            hasCallibration = True
            isCalibration = False
            os.remove(str(fileName) + '.json')

    else:
        process = subprocess.Popen([srcPath + "test-collector", "-t", str(integrationTime), "-o", str(fileName)])
        returnCode = process.wait()
        if returnCode == 0:
            jsonFile = open(str(fileName) + '.json')
            print(jsonFile)
            jsonData = json.load(jsonFile)
            del spectraUncalibrated[:]
            del wavelengthsUncalibrated[:]
            spectraUncalibrated = jsonData['spectra']
            wavelengthsUncalibrated = jsonData['wavelengths']
            os.remove(str(fileName) + '.json')
            if hasCallibration:
                #del spectra[:]
                #del wavelengths[:]
                sendString = ""
                for j in range(1, len(spectraUncalibrated)):
                    print(j)
                    print(spectraUncalibrated[j], " - ", spectraCalibration[j])
                    sendString = sendString + str(float(spectraUncalibrated[j]) - float(spectraCalibration[j])) + " "
                
                sendString = sendString + "s "

                for j in range(1, len(wavelengthsUncalibrated)):
                    print(j)
                    print(wavelengthsUncalibrated[j], " + ", wavelengthsCalibration[j], " / 2")
                    
                    sendString = sendString + str((float(wavelengthsUncalibrated[j]) + float(wavelengthsCalibration[j])) / 2.0) + " "
                
                sendString = sendString + "w "

print(sendString)