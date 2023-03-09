#!/bin/bash

# Update Python 3 if there is a newer version available
echo "Checking for updates to Python 3..."
brew upgrade python

# Install the required packages using pip
echo "Installing packages with pip..."
pip3 install wmi flask cryptography prettytable

# Ensure that the packages are installed in the latest version of Python 3
echo "Setting Python 3 as the default Python version..."
echo "export PATH=\"/usr/local/opt/python@3.11/bin:\$PATH\"" >> ~/.bash_profile
source ~/.bash_profile

echo "All packages installed!"
