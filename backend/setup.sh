#!/bin/bash

# Step 0: Check if wget is installed, if not, install it
if ! command -v wget &> /dev/null
then
    echo "wget could not be found, installing wget..."
    apt-get update && apt-get install -y --no-install-recommends wget
    echo "wget installed successfully."
else
    echo "wget is already installed."
fi

# Step 1: Install the latest CUDA Toolkit for Debian 11 (Bullseye)
echo "Installing CUDA Toolkit 12.6..."

# Download the CUDA keyring package
wget https://developer.download.nvidia.com/compute/cuda/repos/debian11/x86_64/cuda-keyring_1.1-1_all.deb

# Install the keyring package
dpkg -i cuda-keyring_1.1-1_all.deb

# Add the 'contrib' repository to sources list (optional but recommended)
add-apt-repository contrib

# Update the package list
apt-get update

# Install the CUDA Toolkit 12.6
apt-get -y install cuda-toolkit-12-6

echo "CUDA Toolkit 12.6 installed successfully."

echo "Configuring environment variables for CUDA..."

echo 'export PATH="/usr/local/cuda-12.6/bin${PATH:+:${PATH}}"' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH="/usr/local/cuda-12.6/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"' >> ~/.bashrc
echo 'export CUDA_HOME="/usr/local/cuda-12.6"' >> ~/.bashrc

source ~/.bashrc

echo "Environment variables for CUDA configured successfully."

echo "Installing gcc and g++..."

apt-get -y install gcc g++ 

echo "gcc and g++ installed successfully."

echo "Installing Python development headers..."

apt-get -y install python3-dev git


echo "Python development headers installed successfully."

echo "Setup completed successfully!"
