/****************************************************
*	SeabreezeCPPTest.cpp
*
*	This is a rewrite of the VisualCppConsoleDemo.cpp
*	file provided with the sample-code in the 
*	SeaBreeze API. The original file is written for 
*	the seabreezewrapper.h, but this is written for
*	SeaBreezeAPI.h
*
*	Tested on Windows 10 and Visual Studio Community
*	2017 by Sam Foucart In Spring 2019
*
*	Ohio University EECS
*	Wojciech Jadwisienczak
*/


#include <iostream>
#include <fstream>
#include <ctime>
#include "api/seabreezeapi/SeaBreezeAPI.h"




int main()
{
	// There are 1000 microseconds per millisecond
	const int MILLISEC_TO_MICROSEC = 1000;

	// errorCode is initialized to 0 and passed by reference to the functions
	int errorCode = 0;

	// deviceID is the id of the first found device
	long deviceID = 0;

	// wrapper is a pointer to a SeaBreezeAPI object
	SeaBreezeAPI * wrapper = SeaBreezeAPI::getInstance();

	// Probing for devices
	// numDevices is the number of attached spectrometers
	unsigned long numDevices = wrapper->probeDevices();
	std::cout << "Probing for devices..." << std::endl
		<< "There are " << numDevices
		<< " devices found" << std::endl;

	numDevices = wrapper->getNumberOfDeviceIDs();

	// ids is a dynamic array that holds device id numbers
	long * ids = new long[numDevices];
	wrapper->getDeviceIDs(ids, numDevices);
	
	std::cout << "Device ID: ";
	for (size_t i = 0; i < numDevices; ++i)
		std::cout << ids[i] << std::endl;
	
	std::cout << "Opening first Device..." << std::endl;
	deviceID = ids[0];

	// Opening the Devices
	wrapper->openDevice(deviceID, &errorCode);
	if (errorCode) 
	{
		std::cerr << "Error: Device failed to open." << std::endl;
		return 1;
	}
	
	// Getting the Device Type
	char deviceName[15];
	wrapper->getDeviceType(deviceID, &errorCode, deviceName, 15);
	std::cout << "Device: " << deviceName << std::endl;
	
	// Getting the Device Features
	long features[1];
	int numFeatures = wrapper->getSpectrometerFeatures(deviceID, &errorCode, features, 1);
	std::cout << "The " << deviceName << " supports the following features: ";
	for (int i = 0; i < numFeatures; ++i)
		std::wcout << features[i] << std::endl;


	// Setting integration time
	int integrationTimeMillisec = 100;
	wrapper->spectrometerSetIntegrationTimeMicros(deviceID, features[0], &errorCode, integrationTimeMillisec*MILLISEC_TO_MICROSEC);
	if (errorCode)
	{
		std::cout << "Error: Problem setting integration time." << std::endl;
	}

	// Getting number of Pixels
	int numPixels = wrapper->spectrometerGetFormattedSpectrumLength(deviceID, features[0], &errorCode);
	if (errorCode)
	{
		std::cerr << "Error: Problem getting spectrum length." << std::endl;
	}
	std::cout << "This spectrometer has " << numPixels << " pixels." << std::endl;


	// Allocate Spectrum
	double * spectrum = new double[numPixels];

	// Set Up Files
	std::ofstream outs;
	std::string filename = "";
	std::string deviceString = deviceName;
	filename = "spectrum-" + deviceString + ".MAT";
	outs.open(filename.c_str());
	if (outs.fail())
	{
		std::cerr << "Error saving file." << std::endl;
	}
	




	// Iterate over Spectra
	std::cout << "The program will now read out the spectra..." << std::endl;
	outs << "# Created by Ohio University Spectrometer" << std::endl
		<< "# name: spectrum" << std::endl
		<< "# type: matrix" << std::endl
		<< "# rows: 1" << std::endl
		<< "# columns: " << numPixels << std::endl;

	char quit = 'y';
	while (quit != 'n' && quit != 'N')
	{
		wrapper->spectrometerGetFormattedSpectrum(deviceID, features[0], &errorCode, spectrum, numPixels);
		if (errorCode)
		{
			std::cerr << "Error: Problem getting spectrum." << std::endl;
		}
		
		for (int i = 0; i < numPixels; ++i)
		{
			outs << " " << spectrum[i];
		}
		
		std::cout << "Get another sample? (Y) or (N)";
		std::cin >> quit;
	}
	

	outs.close();



	delete[] ids;
	delete[] spectrum;

	wrapper->closeDevice(deviceID, &errorCode);
	if (errorCode)
	{
		std::cerr << "Error: Device failed to close properly." << std::endl;
	}



	return 0;
}


