import os
import json
import openmined.psi as psi


class Authority:
    """
    Represents the authority with a confidential list of persons of interest.
    This class manages the authority's data and performs PSI operations.
    """

    def __init__(self, storage_path="authority_storage"):
        """Initialize the Authority with storage path."""
        self.storage_path = storage_path
        self.metadata = {}
        self.persons_of_interest = set()

        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)

        # Load metadata if it exists
        metadata_path = os.path.join(storage_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)

        # Load persons of interest if they exist
        poi_path = os.path.join(storage_path, "persons_of_interest.json")
        if os.path.exists(poi_path):
            with open(poi_path, "r") as f:
                self.persons_of_interest = set(json.load(f))

    def _save_metadata(self):
        """Save metadata to storage."""
        metadata_path = os.path.join(self.storage_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(self.metadata, f)

    def _save_persons_of_interest(self):
        """Save persons of interest to storage."""
        poi_path = os.path.join(self.storage_path, "persons_of_interest.json")
        with open(poi_path, "w") as f:
            json.dump(list(self.persons_of_interest), f)

    def add_person_of_interest(self, person_name):
        """
        Add a person of interest to the authority's database.

        Args:
            person_name (str): The name of the person of interest.
        """
        self.persons_of_interest.add(person_name)
        self._save_persons_of_interest()
        return True

    def add_multiple_persons_of_interest(self, person_names):
        """
        Add multiple persons of interest to the authority's database.

        Args:
            person_names (list): A list of names of persons of interest.
        """
        self.persons_of_interest.update(person_names)
        self._save_persons_of_interest()
        return True

    def load_persons_of_interest_from_file(self, file_path):
        """
        Load persons of interest from a file.

        Args:
            file_path (str): Path to the file containing persons of interest, one per line.
        """
        with open(file_path, "r") as f:
            names = [line.strip() for line in f.readlines()]
        return self.add_multiple_persons_of_interest(names)

    def create_psi_client(self, reveal_intersection=True):
        """
        Create a PSI client for the authority.

        Args:
            reveal_intersection (bool): Whether to reveal the intersection to the client.
                                        Set to True for the authority to learn the intersection.

        Returns:
            A PSI client configured for the authority.
        """
        return psi.client.CreateWithNewKey(reveal_intersection)

    def find_common_persons(self, passenger_list, psi_client=None):
        """
        Find persons of interest in a passenger list using PSI.

        Args:
            passenger_list (list): List of passenger names.
            psi_client (psi.client): A PSI client. If None, a new one will be created.

        Returns:
            set: The set of persons that appear in both the persons of interest and passenger list.
        """
        if psi_client is None:
            psi_client = self.create_psi_client()

        # Convert sets to lists for PSI
        poi_list = list(self.persons_of_interest)

        # Create request from passenger_list
        request = psi_client.CreateRequest(passenger_list)

        # Process the request with our persons of interest
        server_setup = psi.server.CreateWithNewKey(reveal_intersection=True)
        server_setup.ProcessRequest(request, poi_list)

        # Get the intersection
        intersection = psi_client.GetIntersection(server_setup.GetResponse())

        # Convert indices to actual names
        common_persons = {passenger_list[i] for i in intersection}

        return common_persons
