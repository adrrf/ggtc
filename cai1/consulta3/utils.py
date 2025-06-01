import hashlib
import time
import logging
import csv
import random
from pathlib import Path

logger = logging.getLogger(__name__)


def hash_data(data, algorithm="sha256"):
    """
    Hash the given data using the specified algorithm.

    Args:
        data (str): The data to hash
        algorithm (str): The hashing algorithm to use

    Returns:
        str: The hexadecimal digest of the hash
    """
    if not isinstance(data, str):
        data = str(data)

    data_bytes = data.encode("utf-8")

    if algorithm == "sha256":
        hash_obj = hashlib.sha256(data_bytes)
    elif algorithm == "sha512":
        hash_obj = hashlib.sha512(data_bytes)
    elif algorithm == "blake2b":
        hash_obj = hashlib.blake2b(data_bytes)
    else:
        raise ValueError(f"Unsupported hashing algorithm: {algorithm}")

    return hash_obj.hexdigest()


def save_to_csv(data, filepath, headers=None, mode="w"):
    """
    Save data to a CSV file.

    Args:
        data (list): List of data rows to save
        filepath (str or Path): Path to the CSV file
        headers (list, optional): List of column headers
        mode (str, optional): File open mode ('w' for write, 'a' for append)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, mode, newline="") as f:
            writer = csv.writer(f)
            if headers and mode == "w":
                writer.writerow(headers)
            writer.writerows(data)

        logger.debug(f"Saved data to CSV file: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving data to CSV: {e}")
        return False


def read_from_csv(filepath, has_headers=True):
    """
    Read data from a CSV file.

    Args:
        filepath (str or Path): Path to the CSV file
        has_headers (bool, optional): Whether the CSV has header row

    Returns:
        tuple: (headers, data) if has_headers=True, else (None, data)
    """
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            logger.warning(f"CSV file not found: {filepath}")
            return (None, []) if has_headers else ([],)

        with open(filepath, "r", newline="") as f:
            reader = csv.reader(f)
            if has_headers:
                headers = next(reader)
                data = list(reader)
                return headers, data
            else:
                data = list(reader)
                return data
    except Exception as e:
        logger.error(f"Error reading from CSV: {e}")
        return (None, []) if has_headers else ([],)


def encrypt_csv(input_file, output_file, algorithm="sha256", columns_to_encrypt=None):
    """
    Read a CSV file, encrypt specified columns, and write to a new CSV file.

    Args:
        input_file (str or Path): Path to the input CSV file
        output_file (str or Path): Path to the output CSV file
        algorithm (str): Hashing algorithm to use
        columns_to_encrypt (list, optional): List of column indices to encrypt.
                                           If None, encrypts all columns.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        headers, data = read_from_csv(input_file)
        if not headers or not data:
            return False

        encrypted_data = []
        for row in data:
            new_row = row.copy()
            # Encrypt specified columns or all if none specified
            for idx, value in enumerate(row):
                if columns_to_encrypt is None or idx in columns_to_encrypt:
                    new_row[idx] = hash_data(value, algorithm)
            encrypted_data.append(new_row)

        return save_to_csv(encrypted_data, output_file, headers)
    except Exception as e:
        logger.error(f"Error encrypting CSV: {e}")
        return False


def benchmark_hash_algorithm(algorithm, data_size=1000):
    """
    Benchmark a hash algorithm's performance.

    Args:
        algorithm (str): The hashing algorithm to benchmark
        data_size (int): The number of items to hash

    Returns:
        float: Time taken in seconds
    """
    # Generate random data
    data = [f"Data{i}" for i in range(data_size)]

    # Measure hashing time
    start_time = time.time()
    for item in data:
        hash_data(item, algorithm)
    end_time = time.time()

    elapsed = end_time - start_time
    hashes_per_second = data_size / elapsed

    logger.info(f"Algorithm {algorithm}: {elapsed:.6f} seconds for {data_size} items")
    logger.info(f"Performance: {hashes_per_second:.2f} hashes/second")

    return elapsed


def benchmark_user_scale(algorithm="sha256", user_sizes=None):
    """
    Benchmark protocol performance with different numbers of users.

    Args:
        algorithm (str): The hashing algorithm to use
        user_sizes (list, optional): List of user counts to benchmark.
            Defaults to [100, 500, 1000, 5000, 10000]

    Returns:
        dict: Dictionary mapping user counts to elapsed times
    """
    if user_sizes is None:
        user_sizes = [100, 500, 1000, 5000, 10000]

    results = {}

    logger.info(f"Benchmarking protocol performance with the {algorithm} algorithm")
    logger.info(f"Testing different user scale factors: {user_sizes}")

    for size in user_sizes:
        # Generate random data with the specified size
        data = [
            f"User{i},LastName{i%100},P{random.randint(100000, 999999)}"
            for i in range(size)
        ]

        # Measure hashing time
        start_time = time.time()
        hashed_data = set()
        for item in data:
            hashed_id = hash_data(item, algorithm)
            hashed_data.add(hashed_id)
        end_time = time.time()

        elapsed = end_time - start_time
        hashes_per_second = size / elapsed

        logger.info(
            f"Users: {size:,}: {elapsed:.6f} seconds ({hashes_per_second:.2f} users/second)"
        )
        results[size] = elapsed

    # Print summary
    logger.info("\nBenchmark Results:")
    for size, elapsed in sorted(results.items()):
        logger.info(f"{size:,} users: {elapsed:.6f} seconds")

    return results


def compare_algorithms(data_size=1000):
    """
    Compare the performance of different hashing algorithms.

    Args:
        data_size (int): The number of items to hash

    Returns:
        dict: Dictionary mapping algorithm names to elapsed times
    """
    algorithms = ["sha256", "sha512", "blake2b"]
    results = {}

    logger.info(f"Benchmarking hash algorithms with {data_size} items...")

    for algorithm in algorithms:
        elapsed = benchmark_hash_algorithm(algorithm, data_size)
        results[algorithm] = elapsed

    # Print summary
    logger.info("\nBenchmark Results:")
    for algorithm, elapsed in sorted(results.items(), key=lambda x: x[1]):
        logger.info(f"{algorithm}: {elapsed:.6f} seconds")

    return results
