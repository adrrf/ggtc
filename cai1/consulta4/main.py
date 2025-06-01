import os
import sys
import argparse
import logging
import random
import time
import numpy as np
import pandas as pd
from pathlib import Path

from server import Server1, Server2
from client import Client
from utils import generate_sample_flight_data, clear_storage_directories

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


def setup_system(num_flights=20, clear=False):
    """Set up the system with sample flight data"""
    if clear:
        clear_storage_directories()

    logger.info(f"Generating sample flight data with {num_flights} flights...")
    flight_data = generate_sample_flight_data(num_flights)

    # Initialize servers
    server1 = Server1()
    server2 = Server2()

    # Store flight data on servers
    logger.info("Storing flight data on servers...")
    server1.store_flight_data(flight_data)
    server2.store_flight_data(flight_data)

    # Display sample of the flight data before loading into client
    logger.info("\nSample flight data:")
    logger.info(
        flight_data[["flight_id", "origin", "destination", "date", "price"]]
        .head()
        .to_string()
    )
    
    # Initialize client and load flight info (without prices)
    client = Client()
    client.load_flight_info(flight_data.copy())

    logger.info(
        "✅ Setup complete! System is ready for privacy-preserving flight price retrieval."
    )
    logger.info("\nActual prices (only known to the servers):")
    try:
        logger.info(flight_data[["flight_id", "price"]].head().to_string())
    except KeyError:
        logger.info("Price information not available in the DataFrame")

    return True


def query_flight_price(flight_id):
    """Query the price of a specific flight without revealing which flight"""
    # Initialize servers and client
    server1 = Server1()
    server2 = Server2()
    client = Client()

    # Load flight data for the servers
    flight_data_path1 = Path(server1.storage_dir) / "flight_data.csv"
    flight_data_path2 = Path(server2.storage_dir) / "flight_data.csv"

    if not flight_data_path1.exists() or not flight_data_path2.exists():
        logger.error(
            "❌ Error: Flight data not found on servers. Run 'setup' command first."
        )
        return None

    # Load flight data
    server1.flight_prices = pd.read_csv(flight_data_path1)["price"].values
    server2.flight_prices = pd.read_csv(flight_data_path2)["price"].values

    # Load client flight info
    client_flight_info_path = Path(client.storage_dir) / "flight_info.csv"
    if not client_flight_info_path.exists():
        logger.error(
            "❌ Error: Flight information not found on client. Run 'setup' command first."
        )
        return None

    client.flight_info = pd.read_csv(client_flight_info_path)

    # Check if the flight ID exists
    if flight_id not in client.flight_info["flight_id"].values:
        logger.error(
            f"❌ Error: Flight ID '{flight_id}' not found in available flights."
        )
        return None

    try:
        # Retrieve the price using PIR
        logger.info(
            f"Retrieving price for flight {flight_id} using privacy-preserving protocol..."
        )

        # Now retrieve using PIR
        start_time = time.time()
        retrieved_price = client.retrieve_flight_price(server1, server2, flight_id)
        query_time = time.time() - start_time

        logger.info(f"✅ Price retrieved successfully in {query_time*1000:.2f} ms")
        logger.info(f"Flight ID: {flight_id}")
        logger.info(f"Retrieved Price: {retrieved_price}€")

        # For verification only, get the actual price from server1
        actual_price = pd.read_csv(flight_data_path1)
        actual_price = actual_price[actual_price["flight_id"] == flight_id][
            "price"
        ].iloc[0]

        # Verify that the retrieved price matches the actual price
        if retrieved_price == actual_price:
            logger.info(f"✅ Verification: Retrieved price matches the actual price")
        else:
            logger.error(
                f"❌ Verification: Retrieved price does not match the actual price"
            )
            logger.error(f"Actual price: {actual_price}€")

        return retrieved_price

    except Exception as e:
        logger.error(f"❌ Error retrieving price: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Privacy-Preserving Flight Price Retrieval System"
    )
    parser.add_argument(
        "--action",
        choices=["setup", "query", "demo"],
        default="demo",
        help="Action to perform",
    )
    parser.add_argument("--flight-id", help="Flight ID to query price for")
    parser.add_argument(
        "--num-flights", type=int, default=20, help="Number of flights to generate"
    )
    parser.add_argument(
        "--clear", action="store_true", help="Clear storage directories before setup"
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

    if args.action == "setup":
        setup_system(num_flights=args.num_flights, clear=args.clear)

    elif args.action == "query":
        if not args.flight_id:
            logger.error("❌ Error: --flight-id argument is required for query action")
            return 1

        price = query_flight_price(args.flight_id)
        if price is not None:
            logger.info(f"✅ Flight price retrieved: {price}€")
        else:
            logger.error("❌ Failed to retrieve flight price")

    elif args.action == "demo":
        logger.info("=== 🔒 PRIVACY-PRESERVING FLIGHT PRICE RETRIEVAL DEMO 🔒 ===")

        # Setup with sample flight data
        logger.info("=== Setting up the system with sample flight data ===")
        setup_system(num_flights=20, clear=True)

        # Initialize components
        server1 = Server1()
        server2 = Server2()
        client = Client()

        # Load data from storage
        flight_data_path = Path(server1.storage_dir) / "flight_data.csv"
        flight_data = pd.read_csv(flight_data_path)

        # Load data into client and servers
        server1.flight_prices = flight_data["price"].values
        server2.flight_prices = flight_data["price"].values
        client.flight_info = pd.read_csv(Path(client.storage_dir) / "flight_info.csv")

        # Demonstrate querying for different flights
        logger.info("=== Demonstrating privacy-preserving flight price queries ===")

        # Pick 3 random flights to query
        random_flights = flight_data["flight_id"].sample(3).tolist()

        for flight_id in random_flights:
            logger.info(f"\nQuerying price for flight {flight_id}...")

            # Get actual price for verification (this would normally not be visible to client)
            actual_price = flight_data[flight_data["flight_id"] == flight_id][
                "price"
            ].iloc[0]

            # Perform the PIR query
            start_time = time.time()
            retrieved_price = client.retrieve_flight_price(server1, server2, flight_id)
            query_time = time.time() - start_time

            logger.info(f"✅ Price retrieved in {query_time*1000:.2f} ms")
            logger.info(f"   Flight ID: {flight_id}")
            logger.info(f"   Retrieved Price: {retrieved_price}€")

            # Verify the result
            if retrieved_price == actual_price:
                logger.info(f"   Verification: Retrieved price matches actual price ✓")
                logger.info(f"   Actual price: {actual_price}€")
            else:
                logger.error(
                    f"   Verification: Retrieved price does not match actual price ✗"
                )
                logger.error(f"   Actual price: {actual_price}€")

        logger.info("\n=== 🎉 DEMO COMPLETE 🎉 ===")

        # Clean up data if needed
        data_dirs = (
            []
        )  # Uncomment to clean up: ["server1_storage", "server2_storage", "client_storage"]

        for dir_name in data_dirs:
            if os.path.exists(dir_name):
                logger.info(f"Cleaning up {dir_name}...")
                # Option 1: Remove the entire directory
                # import shutil
                # shutil.rmtree(dir_name)
                # os.makedirs(dir_name, exist_ok=True)

                # Option 2: Just remove files but keep the directory
                for filename in os.listdir(dir_name):
                    file_path = os.path.join(dir_name, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
