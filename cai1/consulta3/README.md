# Privacy-Preserving Identification System

This project implements a privacy-preserving system for identifying persons of interest in airline passenger lists without compromising the privacy of regular passengers.

## Overview

The system uses Private Set Intersection (PSI) protocols to securely match persons of interest against passenger lists without revealing identities of those who are not matches:

1. **Authority**: Holds a confidential list of persons of interest (wanted individuals, etc.)
2. **Airline**: Holds confidential passenger manifests
3. **PSI Protocol**: Allows identification of common elements without revealing the entire sets

## Process Flow

1. Authority encrypts their confidential list of persons of interest
2. Airline encrypts their confidential passenger list
3. The PSI protocol identifies common elements between the two sets without revealing other entries
4. Only matches (persons of interest who are passengers) are identified
5. Regular passengers' identities remain confidential

## Installation

Ensure you have Python 3.11 or later installed, then run:

```bash
pip install -e .
```

Or install the dependencies directly:

```bash
pip install openmined.psi
```

## Usage

Run the demo to see the complete process in action:

```bash
python main.py --action demo
```

Search for persons of interest in a passenger list:

```bash
python main.py --action search --pax-list passengers.txt --poi-list persons_of_interest.txt
```

Run benchmarks to evaluate performance:

```bash
python main.py --action benchmark --size-pax 10000 --size-poi 1000
```

## Security Considerations

- The PSI protocol ensures that only the intersection is revealed
- No information about non-matching individuals is exposed
- The implementation uses cryptographically secure techniques
- Performance optimizations are implemented for critical scenarios
