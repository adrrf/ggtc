# Privacy-Preserving Flight Price Retrieval

This project implements a privacy-preserving protocol for retrieving flight prices without revealing which flight the client is interested in. It uses an Information-Theoretic Private Information Retrieval (IT-PIR) approach based on the work of Chor et al. (1995).

## Overview

The protocol allows airline customers to query flight prices without revealing to the airline's servers which specific flight they are interested in. This ensures that the airline cannot track customers' search patterns or build profiles based on the flights they are looking up.

### Key Features

- **Perfect Privacy**: The protocol guarantees that individual servers cannot determine which flight a client is querying
- **Non-Collusion Assumption**: The privacy guarantee holds as long as the two servers do not collude
- **Efficient Implementation**: Optimized for flight price retrieval with minimal overhead
- **Practical Deployment**: Easy to set up and integrate with existing airline systems

## Technical Approach

The implementation uses an Information-Theoretic PIR protocol with the following components:

1. **Two Non-Colluding Servers**: Both servers hold identical copies of the flight price database
2. **Split Query Mechanism**: 
   - Client generates a random vector K
   - For server 1, client sends K
   - For server 2, client sends K+E (where E is a unit vector with 1 at the position of the desired flight)
3. **Response Combination**: 
   - Server 1 returns K·X (dot product of K with flight prices X)
   - Server 2 returns (K+E)·X
   - Client computes (K+E)·X - K·X = E·X = price of the desired flight

This approach ensures that neither server can determine which flight the client is interested in, providing perfect privacy as long as the servers do not collude.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd consulta4

# Install dependencies using uv
uv pip install -e .
```

## Usage

The system provides a command-line interface for interacting with the PIR protocol:

### Set up the system with sample data:

```bash
python main.py setup --num-flights 20
```

### Query a flight price:

```bash
python main.py query FL100
```

### Evaluate the protocol's performance:

```bash
python main.py evaluate
```

### View the privacy policy statement:

```bash
python main.py privacy-policy
```

## Project Structure

- `client.py`: Implementation of the client-side PIR protocol
- `server.py`: Implementation of the server-side PIR protocol with two server variants
- `utils.py`: Utility functions for data generation and evaluation
- `main.py`: CLI interface for interacting with the system

## Privacy Analysis

The Information-Theoretic PIR protocol provides perfect privacy against individual servers as long as they do not collude. The privacy level is determined by the database size:

- With more flights in the database, the uncertainty about which flight a client is interested in increases
- The probability of a server guessing the correct flight is 1/N, where N is the number of flights
- This protocol ensures that each server learns nothing about which flight the client is querying

## Evaluation Results

The protocol has been evaluated for different database sizes, measuring:

- Setup time
- Query time
- Communication overhead
- Privacy level

See the `evaluate` command for detailed results.

## Privacy Policy Statement

The project includes a sample privacy policy statement that airlines can adapt for their websites to inform customers about the privacy-preserving flight price retrieval system.

## References

- Chor, B., Goldreich, O., Kushilevitz, E., & Sudan, M. (1995). Private information retrieval. In Proceedings of the 36th Annual Symposium on Foundations of Computer Science (pp. 41-50).
