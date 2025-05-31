import os
import json
import pickle
import sys
import logging
from utils import generate_keys, encrypt_value, decrypt_value

# Configure logger
logger = logging.getLogger(__name__)

# Add the current directory to the path to ensure modules can be found
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


class AirlineClient:
    def __init__(self, storage_dir="airline_storage"):
        """Initialize the airline client with a storage directory."""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        self.keys_file = os.path.join(storage_dir, "keys.pickle")
        self.metadata = self._load_metadata()
        self.public_key, self.private_key = self._load_or_generate_keys()

    def _load_metadata(self):
        """Load metadata from file if it exists."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {"passengers": {}, "aggregated_data": {}}

    def _save_metadata(self):
        """Save metadata to file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, default=str)

    def _load_or_generate_keys(self):
        """Load existing keys or generate new ones if they don't exist."""
        if os.path.exists(self.keys_file):
            with open(self.keys_file, "rb") as f:
                keys_data = pickle.load(f)
                return keys_data["public_key"], keys_data["private_key"]
        else:
            public_key, private_key = generate_keys()
            with open(self.keys_file, "wb") as f:
                pickle.dump({"public_key": public_key, "private_key": private_key}, f)
            return public_key, private_key

    def register_passenger_expense(self, passenger_id, year, expense):
        """
        Register a new expense for a passenger.
        1. Encrypt the expense amount
        2. Store metadata locally
        3. Upload encrypted expense to the cloud
        """
        # Encrypt the expense amount
        encrypted_expense = encrypt_value(self.public_key, expense)

        # Initialize passenger data if not exists
        if passenger_id not in self.metadata["passengers"]:
            self.metadata["passengers"][passenger_id] = {}

        # Store metadata locally
        self.metadata["passengers"][passenger_id][year] = {
            "encrypted_expense": str(encrypted_expense),
            "original_expense": expense,  # For verification purposes only
        }
        self._save_metadata()

        # Import cloud module here to avoid circular imports
        from cloud import Cloud

        cloud = Cloud()
        cloud.store_encrypted_expense(passenger_id, year, encrypted_expense)

        return True

    def request_sum_calculation(self, year):
        """
        Request the cloud to calculate the sum of expenses for a specific year
        """
        # Import cloud module here to avoid circular imports
        from cloud import Cloud

        cloud = Cloud()

        try:
            # Request cloud to perform the calculation
            encrypted_sum = cloud.calculate_expenses_sum(year)

            if encrypted_sum is not None:
                try:
                    # Decrypt the result
                    total_sum = decrypt_value(self.private_key, encrypted_sum)

                    # Store the result
                    if "yearly_sums" not in self.metadata["aggregated_data"]:
                        self.metadata["aggregated_data"]["yearly_sums"] = {}

                    self.metadata["aggregated_data"]["yearly_sums"][year] = total_sum
                    self._save_metadata()

                    return total_sum
                except Exception as e:
                    logger.error(f"Error decrypting sum: {e}")
                    return None
            else:
                logger.warning("Encrypted sum is None")
                return None
        except Exception as e:
            logger.error(f"Error requesting sum calculation: {e}")
            return None

    def verify_calculation(self, year):
        """
        Verify that the cloud's calculation matches our local calculation.
        This is for demonstration purposes.
        """
        if (
            "yearly_sums" not in self.metadata["aggregated_data"]
            or year not in self.metadata["aggregated_data"]["yearly_sums"]
        ):
            return False, "No calculation exists for this year"

        cloud_result = self.metadata["aggregated_data"]["yearly_sums"][year]

        # Calculate locally
        local_sum = 0
        for passenger_id, years in self.metadata["passengers"].items():
            if year in years:
                local_sum += years[year]["original_expense"]

        # Use a small epsilon for floating-point comparison
        epsilon = 0.001  # Increased for better floating point tolerance
        is_equal = abs(cloud_result - local_sum) < epsilon

        return is_equal, {
            "cloud_result": cloud_result,
            "local_result": local_sum,
        }
