#!/bin/bash

# Script to run the privacy-preserving identification protocol

# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}  PROTOCOLO DE IDENTIFICACIÓN PRESERVANDO PRIVACIDAD ${NC}"
echo -e "${BLUE}===================================================${NC}"

# Create directories if they don't exist
mkdir -p authority_storage
mkdir -p airline_storage
mkdir -p sample_data

# Check if OpenMined PSI is installed
echo -e "${YELLOW}Checking for OpenMined PSI installation...${NC}"
pip list | grep openmined.psi > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}OpenMined PSI not found. Installing...${NC}"
    pip install openmined.psi
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install OpenMined PSI. Please install it manually:${NC}"
        echo -e "${RED}pip install openmined.psi${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}OpenMined PSI is already installed.${NC}"
fi

# Check for matplotlib (needed for benchmarks)
echo -e "${YELLOW}Checking for matplotlib installation...${NC}"
pip list | grep matplotlib > /dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Matplotlib not found. Installing...${NC}"
    pip install matplotlib
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install matplotlib. Benchmarks will not generate plots.${NC}"
    fi
else
    echo -e "${GREEN}Matplotlib is already installed.${NC}"
fi

# Run the test suite
echo -e "\n${YELLOW}Running unit tests...${NC}"
python test_protocol.py
if [ $? -ne 0 ]; then
    echo -e "${RED}Tests failed! Please check the errors above.${NC}"
    exit 1
else
    echo -e "${GREEN}All tests passed successfully!${NC}"
fi

# Run the demo
echo -e "\n${YELLOW}Running demo...${NC}"
python main.py --action demo

# Run a simple benchmark
echo -e "\n${YELLOW}Running a quick benchmark...${NC}"
python main.py --action benchmark --size-pax 1000 --size-poi 100 --size-overlap 10

# Print instructions for further testing
echo -e "\n${BLUE}===================================================${NC}"
echo -e "${GREEN}Protocol implementation successfully tested!${NC}"
echo -e "${BLUE}===================================================${NC}"
echo -e "\nYou can run more tests with the following commands:"
echo -e "\n${YELLOW}1. Run with custom data:${NC}"
echo -e "   python main.py --action search --pax-list sample_data/flight_passengers.txt --poi-list sample_data/persons_of_interest.txt"
echo -e "\n${YELLOW}2. Run full benchmarks:${NC}"
echo -e "   python benchmark.py"
echo -e "\n${YELLOW}3. Run the demo again:${NC}"
echo -e "   python main.py --action demo"
echo -e "\n${BLUE}===================================================${NC}"
