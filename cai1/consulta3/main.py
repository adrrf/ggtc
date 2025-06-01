import os
import sys
import argparse
import logging
import random
import utils
from client import AirlineClient
from authority import Authority

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Add the current directory to the path to ensure modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


def generate_sample_data():
    """Generate sample data for testing."""
    # Generate some common first and last names
    first_names = [
        "John",
        "Maria",
        "Ahmed",
        "Sarah",
        "Michael",
        "Sophia",
        "Wei",
        "Elena",
        "Carlos",
        "Priya",
    ]
    last_names = [
        "Smith",
        "Garcia",
        "Chen",
        "Patel",
        "Kim",
        "Nguyen",
        "Rodriguez",
        "Muller",
        "Kowalski",
        "Tanaka",
    ]

    # Generate a set of passenger records with names and passport numbers
    passengers = []
    for _ in range(100):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        passport_num = f"P{random.randint(100000, 999999)}"
        passengers.append(f"{first_name},{last_name},{passport_num}")

    # Generate a smaller set of persons of interest (wanted individuals)
    wanted_persons = []
    for _ in range(20):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        passport_num = f"P{random.randint(100000, 999999)}"
        wanted_persons.append(f"{first_name},{last_name},{passport_num}")

    # Ensure some overlap between passengers and wanted persons for testing
    overlap_count = random.randint(2, 5)
    for i in range(overlap_count):
        if i < len(wanted_persons):
            passengers[i] = wanted_persons[i]

    return set(passengers), set(wanted_persons)


def main():
    parser = argparse.ArgumentParser(
        description="Privacy-preserving passenger screening protocol"
    )
    parser.add_argument(
        "--action",
        choices=["prepare", "hash", "compare", "demo"],
        default="demo",
        help="Action to perform",
    )
    parser.add_argument(
        "--algorithm",
        choices=["sha256", "sha512", "blake2b"],
        default="sha256",
        help="Hash algorithm to use",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run performance benchmarks",
    )
    parser.add_argument(
        "--benchmark-type",
        choices=["algorithm", "users"],
        default="users",
        help="Type of benchmark to run: algorithm or users scaling",
    )
    parser.add_argument(
        "--user-sizes",
        type=str,
        default="100,500,1000,5000,10000",
        help="Comma-separated list of user counts for benchmarking (e.g., '100,500,1000')",
    )
    args = parser.parse_args()

    # Set log level based on argument
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Initialize client (airline) and authority
    airline = AirlineClient()
    authority = Authority()

    if args.action == "prepare":
        # Prepare for a new protocol run
        logger.info("Preparing for a new protocol run...")
        algorithm = args.algorithm
        airline.select_hash_algorithm(algorithm)
        logger.info(f"Airline selected {algorithm} algorithm")
        authority.receive_algorithm_selection(algorithm)
        logger.info("Authority received algorithm selection")

    elif args.action == "hash":
        # Hash passenger data
        logger.info("Hashing passenger data...")
        algorithm = airline.get_selected_algorithm()
        if not algorithm:
            logger.error("No algorithm selected. Run 'prepare' action first.")
            return

        airline.hash_passenger_data()
        logger.info("Airline hashed passenger data")

        authority.encrypt_wanted_persons_list()
        logger.info("Authority encrypted wanted persons list")

    elif args.action == "compare":
        # Compare hashed data to find matches
        logger.info("Comparing hashed data...")
        hashed_passengers = airline.get_hashed_passengers()
        encrypted_wanted = authority.get_encrypted_wanted()

        if not hashed_passengers or not encrypted_wanted:
            logger.error("Missing hashed data. Run 'hash' action first.")
            return

        common_elements = authority.find_common_elements(hashed_passengers)

        if common_elements:
            logger.info(f"Found {len(common_elements)} matches in passenger list")
            logger.info(f"Matches: {common_elements}")
        else:
            logger.info("No matches found in passenger list")

    elif args.action == "demo" or args.benchmark:
        # Run the full protocol as a demo
        logger.info("Running privacy-preserving passenger screening demo")

        if args.benchmark:
            if args.benchmark_type == "algorithm":
                # Test multiple algorithms for performance comparison
                logger.info("Benchmarking different hashing algorithms")
                algorithms = ["sha256", "sha512", "blake2b"]
                for algorithm in algorithms:
                    logger.info(f"\n=== Testing {algorithm} algorithm ===")
                    run_protocol_demo(airline, authority, algorithm)
            else:
                # Benchmark with different user scales
                logger.info(
                    "Benchmarking protocol performance with different user counts"
                )
                user_sizes = [int(size) for size in args.user_sizes.split(",")]
                utils.benchmark_user_scale(args.algorithm, user_sizes)
        else:
            # Run with the selected algorithm
            run_protocol_demo(airline, authority, args.algorithm)


def run_protocol_demo(airline, authority, algorithm):
    import time

    # Generate sample data
    passengers, wanted_persons = generate_sample_data()

    # Set the data in the airline and authority
    airline.set_passenger_data(passengers)
    authority.set_wanted_persons_data(wanted_persons)

    # Record actual intersection for verification
    actual_intersection = passengers.intersection(wanted_persons)
    logger.info(f"Actual intersection size: {len(actual_intersection)}")

    # Step 1: Select and share the hashing algorithm
    start_time = time.time()
    airline.select_hash_algorithm(algorithm)
    authority.receive_algorithm_selection(algorithm)

    # Step 2: Hash/encrypt the data
    airline.hash_passenger_data()
    authority.encrypt_wanted_persons_list()

    # Step 3: Find common elements (intersection)
    hashed_passengers = airline.get_hashed_passengers()

    common_elements = authority.find_common_elements(hashed_passengers)
    end_time = time.time()

    # Verify results
    logger.info(f"Protocol execution time: {end_time - start_time:.6f} seconds")
    logger.info(f"Found {len(common_elements)} potential matches")

    # Validate correctness
    if len(common_elements) == len(actual_intersection):
        logger.info("Correct number of matches found ✅")
    else:
        logger.error(f"Incorrect match count! Expected {len(actual_intersection)}")


if __name__ == "__main__":
    main()
