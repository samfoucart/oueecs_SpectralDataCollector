def createJsonFromSample(testMode, errorCode, wavelengths, spectra):
    sendString = "{\n\t\"testMode\": "
    sendString = sendString + str(testMode) + ",\n\t\"errorCode\": "
    sendString = sendString + 0 + ",\n\t\"wavelengths\": ["
    for i in range(len(wavelengths) - 1):
        sendString = sendString + str(wavelengths[i]) + ", "
    
    sendString = sendString + str(wavelengths[len(wavelengths) - 1])
    sendString = sendString + "],\n\t\"sample\": ["
    for i in range(len(wavelengths) - 1):
        sendString = sendString + str(wavelengths[i]) + ", " 

    sendString