import os
import json
import logging
from pathlib import Path
import utils

logger = logging.getLogger(__name__)


class AirlineClient:
    """
    Represents the Airline entity in the privacy-preserving protocol.
    Responsible for:
    1. Selecting the hashing algorithm
    2. Hashing passenger data
    3. Sharing hashed data with the authority
    """

    def __init__(self):
        # Create storage directories if they don't exist
        self.storage_dir = (
            Path(os.path.dirname(os.path.abspath(__file__))) / "airline_storage"
        )
        self.storage_dir.mkdir(exist_ok=True)

        # Initialize metadata
        self.metadata_file = self.storage_dir / "metadata.json"
        self.passenger_data = set()
        self.hashed_passengers = set()
        self.selected_algorithm = None

        # Load metadata if exists
        self.load_metadata()

    def load_metadata(self):
        """Load metadata from file if it exists."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    metadata = json.load(f)
                    self.selected_algorithm = metadata.get("selected_algorithm")
                logger.debug(
                    f"Loaded metadata, selected algorithm: {self.selected_algorithm}"
                )
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")

    def save_metadata(self):
        """Save metadata to file."""
        metadata = {"selected_algorithm": self.selected_algorithm}

        try:
            with open(self.metadata_file, "w") as f:
                json.dump(metadata, f, indent=2)
            logger.debug("Saved metadata")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def select_hash_algorithm(self, algorithm):
        """
        Select the hashing algorithm to use for privacy-preserving comparison.
        """
        supported_algorithms = ["sha256", "sha512", "blake2b"]
        if algorithm not in supported_algorithms:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. Choose from {supported_algorithms}"
            )

        self.selected_algorithm = algorithm
        self.save_metadata()
        logger.info(f"Selected hashing algorithm: {algorithm}")
        return algorithm

    def get_selected_algorithm(self):
        """Get the currently selected hashing algorithm."""
        return self.selected_algorithm

    def set_passenger_data(self, passenger_data):
        """Set the passenger data for processing."""
        self.passenger_data = set(passenger_data)
        logger.info(f"Set passenger data with {len(self.passenger_data)} records")

    def hash_passenger_data(self):
        """
        Hash the passenger data using the selected algorithm.
        """
        if not self.selected_algorithm:
            raise ValueError("No hashing algorithm selected")

        if not self.passenger_data:
            logger.warning("No passenger data to hash")
            return set()

        logger.info(
            f"Hashing {len(self.passenger_data)} passenger records using {self.selected_algorithm}"
        )

        # Hash each passenger record
        self.hashed_passengers = set()
        for passenger in self.passenger_data:
            # We hash the entire record (first_name,last_name,passport_num)
            hashed_id = utils.hash_data(passenger, self.selected_algorithm)
            self.hashed_passengers.add(hashed_id)

        # Save the hashed passenger data
        self._save_hashed_data()

        logger.info(
            f"Completed hashing of {len(self.hashed_passengers)} passenger records"
        )
        return self.hashed_passengers

    def _save_hashed_data(self):
        """Save the hashed passenger data to a CSV file."""
        # Save original passenger data to CSV
        passengers_file = self.storage_dir / "passengers.csv"
        data_to_save = []
        for passenger in self.passenger_data:
            # Split the passenger data into first name, last name, and passport number
            parts = passenger.split(",")
            if len(parts) == 3:
                data_to_save.append(parts)

        utils.save_to_csv(
            data_to_save,
            passengers_file,
            headers=["first_name", "last_name", "passport_num"],
        )

        # Save hashed passenger data to CSV
        hashed_data_file = self.storage_dir / "hashed_passengers.csv"
        hashed_data_to_save = [[hashed_id] for hashed_id in self.hashed_passengers]
        utils.save_to_csv(hashed_data_to_save, hashed_data_file, headers=["hashed_id"])

        # Create encrypted version of the passengers CSV
        utils.encrypt_csv(
            passengers_file,
            self.storage_dir / "encrypted_passengers.csv",
            algorithm=self.selected_algorithm,
        )

        logger.debug(f"Saved passenger data to CSV files in {self.storage_dir}")

    def _load_hashed_data(self):
        """Load the hashed passenger data from a CSV file."""
        hashed_data_file = self.storage_dir / "hashed_passengers.csv"
        if hashed_data_file.exists():
            try:
                _, data = utils.read_from_csv(hashed_data_file)
                # Extract the first column from each row to create a set of hashed IDs
                self.hashed_passengers = set(row[0] for row in data)
                logger.debug(
                    f"Loaded hashed passenger data, {len(self.hashed_passengers)} records"
                )
                return self.hashed_passengers
            except Exception as e:
                logger.error(f"Error loading hashed passenger data: {e}")
        return set()

    def get_hashed_passengers(self):
        """Get the hashed passenger data."""
        if not self.hashed_passengers:
            return self._load_hashed_data()
        return self.hashed_passengers
