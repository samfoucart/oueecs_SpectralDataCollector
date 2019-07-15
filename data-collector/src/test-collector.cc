/****************************************************
*	test-collector.cc
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
#include <math.h>

static void show_usage(std::string name) {
	std::cerr << "Usage: " << name << " <option> ENTRY ... \n" 
			  << "Options: \n"
			  << "\t-t INTEGRATION_TIME\t(Required) Set Integration Time in Milliseconds\n"
			  << "\t-c\t\t(Optional) Specify Whether This Is A Calibration Run. Defaults to FALSE\n"
			  << "\t-o FILE_NAME\t(Optional) Set Output File Name. Defaults to System Time\n"
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
		}
	}

	if (integrationTimeString == "") {
		std::cerr << "-t option is required" << std::endl;
		return 1;
	}

	int integrationTimeMillisec = std::stoi(integrationTimeString);

	// Allocate Spectrum
	double * spectrum = new double[2048];
	double * wavelengths = new double[2048];

    // Generate Numbers for testing
    for (int i = 0; i < 2048; ++i) {
        spectrum[i] = 24 + (((21.694 * sin(.7*i / 25)) - (12 * cos(.7*i / 25))) * exp(-.5 * i / integrationTimeMillisec));
    }

    for (int i = 0; i < 2048; ++i) {
        wavelengths[i] = static_cast<double>(i / 2);
    }



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
    outs << "{" << std::endl 
            << "\"spectra";

    
	outs << "\"";
    

    outs << ": [" << spectrum[0];
    for (int i = 1; i < 2048; ++i) {
        outs << ", " << spectrum[i];
    }
    outs << "]";

    outs << "," << std::endl
            << "\"wavelengths";
    
	outs << "\"";
    

    outs << ": [" << wavelengths[0];
    for (int i = 1; i < 2048; ++i) {
        outs << ", " << wavelengths[i];
    }
    outs << "]" << std::endl << "}";

	outs.close();


	delete[] wavelengths;
	delete[] spectrum;

	return 0;
}