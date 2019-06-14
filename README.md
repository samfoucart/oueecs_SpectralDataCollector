# Spectrometer-Data-Collection
This is a test application for data collection from an Ocean Optics USB 2000 spectrometer. The data will be output into a .csv file.

## Project
This project is made for Ohio University’s Program to Aid Career Exploration and is supervised by Wojciech Jadwisienczak. During the Spring 2019 semester, I am in charge of creating an Android application that can be used to collect data from an Ocean Optics USB2000 spectrometer. This is a sample program to test initialization and data collection for the SeaBreeze API. The features from this program will be integrated into the Android application.

## Dependencies
This project is dependent on the SeaBreeze API, and requires the SeaBreeze.dll and full include tree.

## Build
This project is built in Visual Studio Community 2017.

## Running the Application
When the application is run, it probes for devices and opens the first device found. Then it gets the spectral data from the spectrometer and saves it into a .MAT matrix. This file can be imported into MATLAB or an alternative such as GNU Octave.

## Python
The python testSDP.py is an example file that sends numbers back and forth to an app.
