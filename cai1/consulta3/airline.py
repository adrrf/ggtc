import os
import json
import openmined.psi as psi


class Airline:
    """
    Represents the airline with confidential passenger lists.
    This class manages the airline's data and performs PSI operations.
    """

    def __init__(self, storage_path="airline_storage"):
        """Initialize the Airline with storage path."""
        self.storage_path = storage_path
        self.metadata = {}
        self.flight_passengers = {}

        # Create storage directory if it doesn't exist
        os.makedirs(storage_path, exist_ok=True)

        # Load metadata if it exists
        metadata_path = os.path.join(storage_path, "metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)

        # Load flight passengers if they exist
        flights_path = os.path.join(storage_path, "flights.json")
        if os.path.exists(flights_path):
            with open(flights_path, "r") as f:
                self.flight_passengers = json.load(f)

    def _save_metadata(self):
        """Save metadata to storage."""
        metadata_path = os.path.join(self.storage_path, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(self.metadata, f)

    def _save_flight_passengers(self):
        """Save flight passengers to storage."""
        flights_path = os.path.join(self.storage_path, "flights.json")
        with open(flights_path, "w") as f:
            json.dump(self.flight_passengers, f)

    def add_flight(self, flight_id, passenger_names):
        """
        Add a flight with a list of passenger names.

        Args:
            flight_id (str): The identifier of the flight.
            passenger_names (list): List of passenger names on the flight.
        """
        self.flight_passengers[flight_id] = passenger_names
        self._save_flight_passengers()
        return True

    def load_passengers_from_file(self, flight_id, file_path):
        """
        Load passengers for a flight from a file.

        Args:
            flight_id (str): The identifier of the flight.
            file_path (str): Path to the file containing passenger names, one per line.
        """
        with open(file_path, "r") as f:
            names = [line.strip() for line in f.readlines()]
        return self.add_flight(flight_id, names)

    def create_psi_server(self, reveal_intersection=True):
        """
        Create a PSI server for the airline.

        Args:
            reveal_intersection (bool): Whether to reveal the intersection to the client.
                                       Set to True for the authority to learn the intersection.

        Returns:
            A PSI server configured for the airline.
        """
        return psi.server.CreateWithNewKey(reveal_intersection)

    def get_passengers(self, flight_id):
        """
        Get the list of passengers for a specific flight.

        Args:
            flight_id (str): The identifier of the flight.

        Returns:
            list: The list of passenger names.
        """
        return self.flight_passengers.get(flight_id, [])

    def find_common_persons(self, flight_id, authority_psi_client):
        """
        Find persons of interest in the passenger list of a specific flight using PSI.

        Args:
            flight_id (str): The identifier of the flight.
            authority_psi_client: The PSI client from the authority.

        Returns:
            set: The set of persons that appear in both the persons of interest and passenger list.
        """
        passenger_list = self.get_passengers(flight_id)

        # Create a PSI server
        psi_server = self.create_psi_server()

        # Get the PSI request from the authority
        request = authority_psi_client.CreateRequest(passenger_list)

        # Process the request
        psi_server.ProcessRequest(request, passenger_list)

        # Get the intersection
        response = psi_server.GetResponse()
        intersection = authority_psi_client.GetIntersection(response)

        # Convert indices to actual names
        common_persons = {passenger_list[i] for i in intersection}

        return common_persons
