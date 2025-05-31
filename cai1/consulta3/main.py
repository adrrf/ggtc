import os
import argparse
import logging
import random
from authority import Authority
from airline import Airline
from utils import generate_dataset, time_function, generate_benchmark_data, buscaComunes

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Privacy-preserving identification of persons of interest"
    )
    parser.add_argument(
        "--action",
        choices=["search", "benchmark", "demo"],
        default="demo",
        help="Action to perform",
    )
    parser.add_argument(
        "--pax-list",
        help="Path to file containing passenger list",
    )
    parser.add_argument(
        "--poi-list",
        help="Path to file containing persons of interest list",
    )
    parser.add_argument(
        "--flight-id",
        default="demo-flight",
        help="Flight identifier",
    )
    parser.add_argument(
        "--size-pax",
        type=int,
        default=1000,
        help="Size of passenger list for benchmark",
    )
    parser.add_argument(
        "--size-poi",
        type=int,
        default=100,
        help="Size of persons of interest list for benchmark",
    )
    parser.add_argument(
        "--size-overlap",
        type=int,
        default=10,
        help="Size of overlap between lists for benchmark",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    args = parser.parse_args()

    # Set log level based on argument
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # Initialize the authority and airline
    authority = Authority()
    airline = Airline()

    if args.action == "search":
        if not args.pax_list or not args.poi_list:
            logger.error(
                "❌ Error: --pax-list and --poi-list arguments are required for search action"
            )
            return 1

        # Load the data
        logger.info(f"📋 Loading persons of interest from {args.poi_list}...")
        authority.load_persons_of_interest_from_file(args.poi_list)
        logger.info(
            f"✅ Loaded {len(authority.persons_of_interest)} persons of interest"
        )

        logger.info(f"✈️ Loading passengers from {args.pax_list}...")
        airline.load_passengers_from_file(args.flight_id, args.pax_list)
        logger.info(
            f"✅ Loaded {len(airline.get_passengers(args.flight_id))} passengers"
        )

        # Perform the search
        logger.info("🔍 Searching for persons of interest in passenger list...")
        psi_client = authority.create_psi_client()

        result, execution_time = time_function(
            airline.find_common_persons, args.flight_id, psi_client
        )

        # Report results
        logger.info(f"⏱️ Search completed in {execution_time:.4f} seconds")
        logger.info(f"🎯 Found {len(result)} matches")

        if result:
            logger.info("📝 Matches found:")
            for person in result:
                logger.info(f"  - {person}")
        else:
            logger.info("👍 No matches found in passenger list")

    elif args.action == "benchmark":
        logger.info("=== 🚀 PRIVACY-PRESERVING IDENTIFICATION BENCHMARK 🚀 ===")

        # Generate benchmark data
        logger.info("🔢 Generating benchmark data with parameters:")
        logger.info(f"  - Passenger list size: {args.size_pax}")
        logger.info(f"  - Persons of interest list size: {args.size_poi}")
        logger.info(f"  - Expected overlap size: {args.size_overlap}")

        passenger_list, poi_list, expected_overlap = generate_benchmark_data(
            args.size_pax, args.size_poi, args.size_overlap
        )

        # Verify the generated data
        actual_overlap = set(passenger_list).intersection(set(poi_list))
        logger.info(f"✅ Generated data with {len(actual_overlap)} actual overlaps")

        # Convert lists to sets for the benchmark
        passenger_set = set(passenger_list)
        poi_set = set(poi_list)

        # Benchmark our implementation
        logger.info("⏱️ Benchmarking buscaComunes function...")
        result, psi_time = time_function(buscaComunes, poi_set, passenger_set)
        logger.info(f"✅ PSI completed in {psi_time:.4f} seconds")
        logger.info(
            f"🎯 Found {len(result)} matches out of {len(actual_overlap)} expected"
        )

        # Benchmark a naive approach for comparison
        logger.info("⏱️ Benchmarking naive set intersection for comparison...")
        naive_result, naive_time = time_function(
            lambda s1, s2: s1.intersection(s2), poi_set, passenger_set
        )
        logger.info(f"✅ Naive approach completed in {naive_time:.4f} seconds")

        # Compare the results
        logger.info("📊 Performance comparison:")
        logger.info(f"  - PSI approach: {psi_time:.4f} seconds")
        logger.info(f"  - Naive approach: {naive_time:.4f} seconds")
        logger.info(f"  - Ratio (PSI/Naive): {psi_time/naive_time:.2f}x")

        if psi_time > naive_time:
            logger.info(
                "📝 Note: The PSI approach is slower but provides privacy guarantees"
            )
            logger.info("   that the naive approach does not offer.")
        else:
            logger.info(
                "🎉 The PSI approach is faster and provides privacy guarantees!"
            )

    elif args.action == "demo":
        logger.info("=== 🔒 PRIVACY-PRESERVING IDENTIFICATION DEMO 🔒 ===")

        # Generate some sample data
        logger.info("🔢 Generating sample data...")

        # Create a set of 100 passengers with 5 persons of interest
        all_passengers = generate_dataset(100)
        flight_passengers = random.sample(list(all_passengers), 50)

        # Choose 20 persons of interest, with 5 overlap
        overlap_size = 5
        overlap = set(random.sample(flight_passengers, overlap_size))

        persons_of_interest = list(overlap)
        additional_poi = random.sample(
            list(all_passengers - set(flight_passengers)), 15
        )
        persons_of_interest.extend(additional_poi)

        # Save the data
        pax_file = os.path.join(airline.storage_path, "demo_passengers.txt")
        poi_file = os.path.join(authority.storage_path, "demo_poi.txt")

        os.makedirs(airline.storage_path, exist_ok=True)
        os.makedirs(authority.storage_path, exist_ok=True)

        with open(pax_file, "w") as f:
            for passenger in flight_passengers:
                f.write(f"{passenger}\n")

        with open(poi_file, "w") as f:
            for person in persons_of_interest:
                f.write(f"{person}\n")

        logger.info(
            f"✅ Generated {len(flight_passengers)} passengers and {len(persons_of_interest)} persons of interest"
        )
        logger.info(f"✅ There are {len(overlap)} persons of interest on the flight")

        # Load the data
        logger.info("📋 Loading generated data...")
        authority.load_persons_of_interest_from_file(poi_file)
        airline.load_passengers_from_file("demo-flight", pax_file)

        # Demonstrate the PSI protocol
        logger.info("🔍 Performing private search using PSI protocol...")

        # Method 1: Using the buscaComunes function directly
        logger.info("Method 1: Using buscaComunes function")
        psi_result, psi_time = time_function(
            buscaComunes, set(persons_of_interest), set(flight_passengers)
        )
        logger.info(f"⏱️ Search completed in {psi_time:.4f} seconds")
        logger.info(f"🎯 Found {len(psi_result)} matches")
        logger.info("Persons of interest on flight:")
        for person in psi_result:
            logger.info(f"  - {person}")

        # Method 2: Using the class-based approach
        logger.info("\nMethod 2: Using class-based approach")
        psi_client = authority.create_psi_client()
        class_result, class_time = time_function(
            airline.find_common_persons, "demo-flight", psi_client
        )
        logger.info(f"⏱️ Search completed in {class_time:.4f} seconds")
        logger.info(f"🎯 Found {len(class_result)} matches")
        logger.info("Persons of interest on flight:")
        for person in class_result:
            logger.info(f"  - {person}")

        # Verify results match expected overlap
        logger.info("\n🔍 Verifying results...")
        if psi_result == class_result == overlap:
            logger.info("✅ Results match expected overlap!")
        else:
            logger.error("❌ Results do not match expected overlap")
            logger.error(f"Expected: {overlap}")
            logger.error(f"Method 1: {psi_result}")
            logger.error(f"Method 2: {class_result}")

        # Explain privacy benefits
        logger.info("\n🔒 Privacy Benefits:")
        logger.info("1. Only the intersection is revealed to the authority")
        logger.info(
            "2. The airline does not learn about persons of interest not on their flights"
        )
        logger.info(
            "3. The authority does not learn about passengers who are not persons of interest"
        )
        logger.info(
            "4. The cryptographic protocol ensures security even against sophisticated attackers"
        )

        logger.info("\n🚀 Performance considerations:")
        logger.info("1. The PSI protocol is optimized for efficiency")
        logger.info("2. For large datasets, batch processing can be implemented")
        logger.info("3. The protocol scales well with increasing dataset sizes")
        logger.info("4. Can be further optimized for critical scenarios")

    return 0


if __name__ == "__main__":
    exit(main())
