import os
import sys
import argparse
import logging
import random
from client import AirlineClient


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

# Import after path setup


def main():
    parser = argparse.ArgumentParser(
        description="Privacy-preserving expense processing demo"
    )
    parser.add_argument(
        "--action",
        choices=["register", "calculate", "verify", "demo"],
        default="demo",
        help="Action to perform",
    )
    parser.add_argument("--passenger", help="Passenger ID")
    parser.add_argument("--year", help="Year for the expense")
    parser.add_argument("--expense", type=float, help="Expense amount")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    args = parser.parse_args()

    # Set log level based on argument
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    client = AirlineClient()

    if args.action == "register":
        if not args.passenger or not args.year or args.expense is None:
            logger.error(
                "❌ Error: --passenger, --year, and --expense arguments are required for register action"
            )
            return 1

        result = client.register_passenger_expense(
            args.passenger, args.year, args.expense
        )
        if result:
            logger.info(
                f"✅ Expense of {args.expense} registered for passenger {args.passenger} in year {args.year}"
            )
        else:
            logger.error("❌ Failed to register expense")

    elif args.action == "calculate":
        if not args.year:
            logger.error("❌ Error: --year argument is required for calculate action")
            return 1

        total = client.request_sum_calculation(args.year)
        if total is not None:
            logger.info(f"✅ Total expenses for year {args.year}: {total}")
        else:
            logger.error(f"❌ Failed to calculate expenses for year {args.year}")

    elif args.action == "verify":
        if not args.year:
            logger.error("❌ Error: --year argument is required for verify action")
            return 1

        result, details = client.verify_calculation(args.year)
        if result:
            logger.info(f"✅ Verification for year {args.year} successful!")
            if isinstance(details, dict):
                cloud_result = details.get("cloud_result")
                local_result = details.get("local_result")
                logger.info(
                    f"Cloud result: {cloud_result}, Local result: {local_result}"
                )
                # Log the difference for debugging
                diff = (
                    abs(cloud_result - local_result)
                    if cloud_result is not None and local_result is not None
                    else None
                )
                logger.info(
                    f"Difference: {diff:.10f}"
                    if diff is not None
                    else "Difference: N/A"
                )
        else:
            logger.error(f"❌ Verification for year {args.year} failed!")
            if isinstance(details, dict):
                cloud_result = details.get("cloud_result")
                local_result = details.get("local_result")
                logger.error(
                    f"Cloud result: {cloud_result}, Local result: {local_result}"
                )
                # Log the difference for debugging
                diff = (
                    abs(cloud_result - local_result)
                    if cloud_result is not None and local_result is not None
                    else None
                )
                logger.error(
                    f"Difference: {diff:.10f}"
                    if diff is not None
                    else "Difference: N/A"
                )
            else:
                logger.error(f"Error: {details}")

    elif args.action == "demo":
        logger.info("=== 🔒 PRIVACY-PRESERVING EXPENSE TRACKING DEMO 🔒 ===")

        # Generate some sample data
        years = ["2022", "2023", "2024"]
        passengers = ["P001", "P002", "P003", "P004", "P005"]

        # Register expenses for each passenger
        logger.info("=== Registering passenger expenses ===")
        expected_totals = {year: 0.0 for year in years}

        for year in years:
            for passenger in passengers:
                # Generate a random expense between $100 and $2000
                expense = round(random.uniform(100, 2000), 2)
                expected_totals[year] += expense

                logger.info(
                    f"Registering expense of ${expense:.2f} for passenger {passenger} in year {year}"
                )
                client.register_passenger_expense(passenger, year, expense)

        # Calculate and verify expenses for each year
        logger.info("=== Calculating and verifying yearly expenses ===")

        for year in years:
            # Request cloud calculation
            logger.info(f"Requesting sum calculation for year {year}...")
            total = client.request_sum_calculation(year)
            if total is not None:
                logger.info(f"Total expenses for {year} (from cloud): ${total:.2f}")
            else:
                logger.error(f"Failed to calculate total expenses for {year}")

            # Verify calculation
            result, details = client.verify_calculation(year)
            if result:
                logger.info(f"✅ Verification for year {year} successful!")
                if isinstance(details, dict):
                    cloud_result = details.get("cloud_result")
                    local_result = details.get("local_result")
                    expected = expected_totals[year]
                    logger.info(f"   Cloud result: ${cloud_result:.2f}")
                    logger.info(f"   Local result: ${local_result:.2f}")
                    logger.info(f"   Expected result: ${expected:.2f}")
                    # Log the difference for debugging
                    diff = abs(cloud_result - local_result)
                    logger.info(f"   Difference: {diff:.10f}")
            else:
                logger.error(f"❌ Verification for year {year} failed!")
                if isinstance(details, dict):
                    cloud_result = details.get("cloud_result")
                    local_result = details.get("local_result")
                    expected = expected_totals[year]
                    logger.error(f"   Cloud result: ${cloud_result:.2f}")
                    logger.error(f"   Local result: ${local_result:.2f}")
                    logger.error(f"   Expected result: ${expected:.2f}")
                    # Log the difference for debugging
                    diff = abs(cloud_result - local_result)
                    logger.error(f"   Difference: {diff:.10f}")
                else:
                    logger.error(f"   Error: {details}")

        logger.info("=== 🎉 DEMO COMPLETE 🎉 ===")
        data_dirs = []
        # data_dirs = ["airline_storage", "cloud_storage"]

        for dir_name in data_dirs:
            if os.path.exists(dir_name):
                print(f"Cleaning up {dir_name}...")
                # Option 1: Remove the entire directory
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
