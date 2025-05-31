# File Integrity Verification Process

This project implements a file integrity verification process that mocks a cloud storage service.

## Overview

The process implements a secure file integrity verification system with the following components:

1. **Client**: Represents the customer who wants to store files securely
2. **Cloud**: Mocks an unsafe cloud storage service
3. **Utility Functions**: For cryptographic operations (HMAC, nonce generation)

## Process Flow

1. The client generates a set of predefined nonces and computes an HMAC of the file using one of the nonces
2. The client stores the file and hash locally
3. The client uploads the file to the cloud
4. The client can later verify the integrity of the file by:
   - Using the next predefined nonce from the sequence
   - Sending a challenge to the cloud with this nonce
   - Computing the hash locally with the same nonce
   - Comparing the local hash with the one received from the cloud

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

Upload a specific file:

```bash
python main.py --action upload --file path/to/your/file
```

Verify a previously uploaded file:

```bash
python main.py --action verify --file filename
```

## Implementation Details

- **utils.py**: Contains utility functions for cryptographic operations
- **client.py**: Implements the client-side functionality
- **cloud.py**: Mocks the cloud storage service
- **main.py**: Provides a CLI interface to demonstrate the process