# Privacy-Preserving Expense Processing

This project implements a privacy-preserving system for processing passenger expense data in an untrusted cloud environment.

## Overview

The system uses homomorphic encryption to allow calculations on encrypted data without revealing the actual values:

1. **Airline Client**: Encrypts passenger expense data and sends it to the cloud
2. **Cloud Service**: Performs calculations on encrypted data without knowing actual values
3. **Homomorphic Properties**: Allows addition operations on encrypted data

## Process Flow

1. The airline generates public and private keys for homomorphic encryption
2. Passenger expense data is encrypted using the public key
3. Encrypted data is stored in the cloud
4. The cloud can perform summation operations on the encrypted data
5. Results are returned to the airline in encrypted form
6. The airline decrypts the results using its private key

## Installation

Ensure you have Python 3.11 or later installed, then run:

```bash
pip install -e .
```

## Usage

Run the demo to see the complete process in action:

```bash
python main.py --action demo
```

Register a new passenger expense:

```bash
python main.py --action register --passenger P001 --year 2023 --expense 1250.75
```

Calculate expenses for a specific year:

```bash
python main.py --action calculate --year 2023
```

Verify the calculation against local data:

```bash
python main.py --action verify --year 2023
```

## Security Considerations

- The homomorphic encryption ensures that raw expense data is never exposed to the cloud
- The airline keeps the private key secure and only shares the public key
- The cloud can only perform permitted operations on encrypted data