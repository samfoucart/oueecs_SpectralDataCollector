/****************************************************
*	data-collector.cc
*
*
*   Sam Foucart
*
*   June 2019
*   MIT License
*	Ohio University EECS
*
*****************************************************/


#include <iostream>
#include <fstream>
#include <ctime>
#include <vector>
#include "api/seabreezeapi/SeaBreezeAPI.h"

static void show_usage(std::string name) {
	std::cerr << "Usage: " << name << " <option> ENTRY ... \n" 
			  << "Options: \n"
			  << "\t-t INTEGRATION_TIME\t(Required) Set Integration Time in Milliseconds\n"
			  << "\t-c\t\t\t(Optional) Specify Whether This Is A Calibration Run. Defaults to FALSE\n"
			  << "\t-o FILE_NAME\t\t(Optional) Set Output File Name. Defaults to System Time\n"
			  << std::endl;
}

int main(int argc, char* argv[]) {
	// Show usage if less than 3 arguments entered
	if (argc < 3) {
		show_usage(argv[0]);
		return 1;
	}

	std::string fileName = "";
	std::string integrationTimeString = "";
	bool isCalibration = false;

	// Get filename and integration time from arguments
	for (int i = 1; i < argc; ++i) {
		std::string arg = argv[i];
		if (arg == "-t") {
			if (i + 1 < argc) {
				integrationTimeString = argv[++i];
			} else {
				std::cerr << "-t option requires a number argument." << std::endl;
				return 1;
			}

		} else if (arg == "-o") {
			if (i + 1 < argc) {
				fileName = argv[++i];
			} else {
				std::cerr << "-o option requires an argument" << std::endl;
				return 1;
			}

		} else if (arg == "-c") {
			isCalibration = true;
		}
	}

	if (integrationTimeString == "") {
		std::cerr << "-t option is required" << std::endl;
		return 1;
	}

	int integrationTimeMillisec = std::stoi(integrationTimeString);

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

	numDevices = wrapper->getNumberOfDeviceIDs();

	if (numDevices == 0) {
		std::cerr << "Error: No Devices Found" << std::endl;
		return 2;
	}

	// ids is a dynamic array that holds device id numbers
	long * ids = new long[numDevices];
	wrapper->getDeviceIDs(ids, numDevices);
	
	deviceID = ids[0];

	delete [] ids;

	// Open the Device
	wrapper->openDevice(deviceID, &errorCode);
	if (errorCode) 
	{
		std::cerr << "Error: Device failed to open." << std::endl;
		return 3;
	}
	
	// Get the Device Type
	char deviceName[15];
	wrapper->getDeviceType(deviceID, &errorCode, deviceName, 15);
	
	// Getting the Device Features
	long features[1];
	int numFeatures = wrapper->getSpectrometerFeatures(deviceID, &errorCode, features, 1);

	// Setting integration time
	wrapper->spectrometerSetIntegrationTimeMicros(deviceID, features[0], &errorCode, integrationTimeMillisec*MILLISEC_TO_MICROSEC);
	if (errorCode)
	{
		std::cerr << "Error: Problem setting integration time." << std::endl;
		return 1;
	}

	// Getting number of Pixels
	int numPixels = wrapper->spectrometerGetFormattedSpectrumLength(deviceID, features[0], &errorCode);
	if (errorCode)
	{
		std::cerr << "Error: Problem getting spectrum length." << std::endl;
		return 1;
	}

	// Allocate Spectrum
	double * spectrum = new double[numPixels];
	double * wavelengths = new double[numPixels];

	// Set Up Files
	std::ofstream outs;
	if (fileName == "") {
		fileName = std::to_string(std::time(0)) + ".json";
		
	} else if (fileName.find(".json") == std::string::npos) {
		fileName += ".json";
	}
	
	outs.open(fileName.c_str());
	if (outs.fail())
	{
		std::cerr << "Error saving file." << std::endl;
		delete [] spectrum;
		delete [] wavelengths;
		return 4;
	}
	

	// Create json from spectra
	wrapper->spectrometerGetFormattedSpectrum(deviceID, features[0], &errorCode, spectrum, numPixels);
	if (errorCode)
	{
		std::cerr << "Error: Problem getting spectrum." << std::endl;
		delete [] spectrum;
		delete [] wavelengths;
		outs.close();
		return 5;

	} else {
		outs << "{" << std::endl 
		     << "\"spectra";

		if (isCalibration) {
			outs << "Calibration\"";
		} else {
			outs << "\"";
		}

		outs << ": [" << spectrum[0];
		for (int i = 1; i < numPixels; ++i) {
			outs << ", " << spectrum[i];
		}
		outs << "]";

		wrapper->spectrometerGetWavelengths(deviceID, features[0], &errorCode, wavelengths, numPixels);
		if (errorCode) {
			std::cerr << "Error: Problem getting wavelengths." << std::endl;
			outs << std::endl << "}";
			outs.close();
			delete [] spectrum;
			delete [] wavelengths;
			return 5;
		} else {
			outs << "," << std::endl
				 << "\"wavelengths";
			if (isCalibration) {
				outs << "Calibration\"";
			} else {
				outs << "\"";
			}

			outs << ": [" << wavelengths[0];
			for (int i = 1; i < numPixels; ++i) {
				outs << ", " << wavelengths[i];
			}
			outs << "]" << std::endl << "}";
		}
	}

	outs.close();


	delete[] wavelengths;
	delete[] spectrum;

	wrapper->closeDevice(deviceID, &errorCode);
	if (errorCode)
	{
		std::cerr << "Error: Device failed to close properly." << std::endl;
	}



	return 0;
}


