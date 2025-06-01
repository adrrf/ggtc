import os
import json
import logging
from pathlib import Path
import utils

logger = logging.getLogger(__name__)


class Authority:
    """
    Represents the Authority entity in the privacy-preserving protocol.
    Responsible for:
    1. Receiving the hashing algorithm selection
    2. Encrypting the wanted persons list
    3. Finding common elements between the lists
    """

    def __init__(self):
        # Create storage directories if they don't exist
        self.storage_dir = (
            Path(os.path.dirname(os.path.abspath(__file__))) / "authority_storage"
        )
        self.storage_dir.mkdir(exist_ok=True)

        # Initialize metadata
        self.metadata_file = self.storage_dir / "metadata.json"
        self.wanted_persons = set()
        self.encrypted_wanted = set()
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

    def receive_algorithm_selection(self, algorithm):
        """
        Receive the selected hashing algorithm from the airline.
        """
        supported_algorithms = ["sha256", "sha512", "blake2b"]
        if algorithm not in supported_algorithms:
            raise ValueError(
                f"Unsupported algorithm: {algorithm}. Choose from {supported_algorithms}"
            )

        self.selected_algorithm = algorithm
        self.save_metadata()
        logger.info(f"Received hashing algorithm selection: {algorithm}")
        return algorithm

    def set_wanted_persons_data(self, wanted_persons):
        """Set the wanted persons data for processing."""
        self.wanted_persons = set(wanted_persons)
        logger.info(f"Set wanted persons data with {len(self.wanted_persons)} records")

    def encrypt_wanted_persons_list(self):
        """
        Encrypt (hash) the wanted persons list using the selected algorithm.
        """
        if not self.selected_algorithm:
            raise ValueError("No hashing algorithm selected")

        if not self.wanted_persons:
            logger.warning("No wanted persons data to encrypt")
            return set()

        logger.info(
            f"Encrypting {len(self.wanted_persons)} wanted persons records using {self.selected_algorithm}"
        )

        # Hash each wanted person record
        self.encrypted_wanted = set()
        for person in self.wanted_persons:
            # We hash the entire record (first_name,last_name,id_number)
            encrypted_id = utils.hash_data(person, self.selected_algorithm)
            self.encrypted_wanted.add(encrypted_id)

        # Save the encrypted wanted persons data
        self._save_encrypted_data()

        logger.info(
            f"Completed encryption of {len(self.encrypted_wanted)} wanted persons records"
        )
        return self.encrypted_wanted

    def _save_encrypted_data(self):
        """Save the encrypted wanted persons data to CSV files."""
        # Save original wanted persons data to CSV
        wanted_persons_file = self.storage_dir / "wanted_persons.csv"
        data_to_save = []
        for person in self.wanted_persons:
            # Split the person data into first name, last name, and ID
            parts = person.split(",")
            if len(parts) == 3:
                data_to_save.append(parts)

        utils.save_to_csv(
            data_to_save,
            wanted_persons_file,
            headers=["first_name", "last_name", "id_number"],
        )

        # Save encrypted wanted persons data to CSV
        encrypted_data_file = self.storage_dir / "encrypted_wanted.csv"
        encrypted_data_to_save = [
            [encrypted_id] for encrypted_id in self.encrypted_wanted
        ]
        utils.save_to_csv(
            encrypted_data_to_save, encrypted_data_file, headers=["encrypted_id"]
        )

        # Create encrypted version of the wanted persons CSV
        utils.encrypt_csv(
            wanted_persons_file,
            self.storage_dir / "encrypted_wanted_persons.csv",
            algorithm=self.selected_algorithm,
        )

        logger.debug(f"Saved wanted persons data to CSV files in {self.storage_dir}")

    def _load_encrypted_data(self):
        """Load the encrypted wanted persons data from a CSV file."""
        encrypted_data_file = self.storage_dir / "encrypted_wanted.csv"
        if encrypted_data_file.exists():
            try:
                _, data = utils.read_from_csv(encrypted_data_file)
                # Extract the first column from each row to create a set of encrypted IDs
                self.encrypted_wanted = set(row[0] for row in data)
                logger.debug(
                    f"Loaded encrypted wanted persons data, {len(self.encrypted_wanted)} records"
                )
                return self.encrypted_wanted
            except Exception as e:
                logger.error(f"Error loading encrypted wanted persons data: {e}")
        return set()

    def get_encrypted_wanted(self):
        """Get the encrypted wanted persons data."""
        if not self.encrypted_wanted:
            return self._load_encrypted_data()
        return self.encrypted_wanted

    def find_common_elements(self, hashed_passengers):
        """
        Find common elements between the encrypted wanted persons list and
        the hashed passenger list.

        This is the core privacy-preserving function that finds the intersection
        without revealing the original data.
        """
        if not self.encrypted_wanted:
            self._load_encrypted_data()

        if not self.encrypted_wanted:
            logger.warning("No encrypted wanted persons data available")
            return set()

        if not hashed_passengers:
            logger.warning("No hashed passenger data provided")
            return set()

        # Find the intersection between the two sets
        common_elements = self.encrypted_wanted.intersection(hashed_passengers)
        logger.info(f"Found {len(common_elements)} common elements")

        # Save the results
        self._save_common_elements(common_elements)

        return common_elements

    def _save_common_elements(self, common_elements):
        """Save the common elements to a CSV file."""
        common_elements_file = self.storage_dir / "common_elements.csv"
        common_elements_to_save = [[element] for element in common_elements]
        utils.save_to_csv(
            common_elements_to_save, common_elements_file, headers=["common_id"]
        )
        logger.debug(f"Saved common elements to {common_elements_file}")
