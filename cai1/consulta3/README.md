# Privacy-Preserving Protocol for Passenger Screening

This implementation provides a privacy-preserving protocol that allows airlines to check their passenger lists against government watchlists without revealing the identities of all passengers.

## Business Process Overview

The BPMN 2.0 model (available in `docs/diagram.bpmn`) shows the business process flow:

1. The Airline (Customer) selects a hashing algorithm
2. The Airline sends the selected algorithm to the Authority
3. The Authority encrypts its list of wanted persons using the selected algorithm
4. The Airline hashes its passenger data using the same algorithm
5. The Airline sends the hashed passenger data to the Authority
6. The Authority computes the intersection between the two sets
7. Both parties can see only the common elements (wanted persons on the flight)

## Protocol Description

The core of the implementation is the secure set intersection protocol, which follows these steps:

1. **Algorithm Selection**: The airline selects a cryptographic hash function (SHA-256, SHA-512, or BLAKE2b)
2. **Data Preparation**: 
   - The authority has a set of wanted persons IDs: `Set_de_delincuentes`
   - The airline has a set of passenger IDs: `Set_de_pasajeros_vuelo`
3. **Privacy Transformation**:
   - The authority computes `Set_de_delincuentes_Confiden = Hash(Set_de_delincuentes)`
   - The airline computes `Set_de_pasajeros_vuelo_Confiden = Hash(Set_de_pasajeros_vuelo)`
4. **Secure Intersection**:
   - The authority computes `Set_de_Comunes = Set_de_delincuentes_Confiden ∩ Set_de_pasajeros_vuel_Confiden`

The key privacy property is that only the common elements (people who are both wanted and on the flight) are revealed. The identities of other passengers remain confidential.

## Implementation Details

The implementation consists of several Python modules:

- `main.py`: Orchestrates the protocol flow and provides a command-line interface
- `client.py`: Implements the `AirlineClient` class for the airline side of the protocol
- `authority.py`: Implements the `Authority` class for the government authority side
- `utils.py`: Provides common utilities like hashing functions and benchmarking tools

## Data Storage

All data is stored in CSV format for transparency and ease of inspection:

- **Airline data:**
  - `passengers.csv`: Original passenger records
  - `hashed_passengers.csv`: Hashed passenger records
  - `encrypted_passengers.csv`: Encrypted version of the passenger CSV

- **Authority data:**
  - `wanted_persons.csv`: Original wanted persons records
  - `encrypted_wanted.csv`: Hashed wanted persons records
  - `encrypted_wanted_persons.csv`: Encrypted version of the wanted persons CSV
  - `common_elements.csv`: Records of matches found between the two sets

## Performance Optimization

The implementation includes performance benchmarking for different hashing algorithms:

- SHA-256: Fast and widely used cryptographic hash function
- SHA-512: Stronger security but slightly slower
- BLAKE2b: Designed for high performance on modern CPUs

## Usage

Run the demo to see the full protocol in action:

```bash
python main.py --action demo
```

### Benchmarking Options

The application supports two types of benchmarking:

1. **Algorithm Benchmarking** - Compare performance of different hashing algorithms:
```bash
python main.py --benchmark --benchmark-type algorithm
```

2. **User Scaling Benchmarking** - Test how performance scales with different numbers of users:
```bash
python main.py --benchmark --benchmark-type users --user-sizes 1000,5000,10000,50000,100000
```

Sample benchmark results for user scaling (SHA-256):
```
Users: 1,000: 0.000561 seconds (1,781,777.40 users/second)
Users: 5,000: 0.002949 seconds (1,695,490.34 users/second)
Users: 10,000: 0.005825 seconds (1,716,725.61 users/second)
Users: 50,000: 0.027133 seconds (1,842,791.49 users/second)
Users: 100,000: 0.056134 seconds (1,781,451.99 users/second)
```

These results demonstrate linear scaling with the number of users, maintaining a consistent throughput of approximately 1.7-1.8 million users per second, which is critical for high-performance applications in aviation security.

## Security Considerations

This implementation provides:

1. **Privacy Preservation**: Passengers not on the watchlist remain anonymous
2. **Data Minimization**: Only the minimum necessary information is shared
3. **Cryptographic Security**: Uses standard cryptographic hash functions

## Note on Real-World Deployment

In a real-world deployment, additional security measures would be recommended:

1. Secure communication channels (TLS)
2. Salting of hash values to prevent precomputation attacks
3. Key rotation policies
4. Audit logging for compliance purposes
