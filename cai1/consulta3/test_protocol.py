import unittest
import os
import random
from authority import Authority
from airline import Airline
from utils import generate_dataset, buscaComunes


class TestPrivacyPreservingProtocol(unittest.TestCase):
    """Test cases for the privacy-preserving identification protocol."""

    def setUp(self):
        """Set up test environment."""
        # Use test-specific storage paths
        self.authority = Authority(storage_path="test_authority_storage")
        self.airline = Airline(storage_path="test_airline_storage")

        # Create test data directories
        os.makedirs(self.authority.storage_path, exist_ok=True)
        os.makedirs(self.airline.storage_path, exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        # Clean up test data
        import shutil

        if os.path.exists(self.authority.storage_path):
            shutil.rmtree(self.authority.storage_path)
        if os.path.exists(self.airline.storage_path):
            shutil.rmtree(self.airline.storage_path)

    def test_basic_intersection(self):
        """Test basic intersection functionality."""
        # Create test data
        poi = {"John Smith", "Maria Rodriguez", "Ahmed Hassan"}
        passengers = {"Sofia Garcia", "John Smith", "Michael Wilson"}
        expected = {"John Smith"}

        # Add data to the authority and airline
        self.authority.add_multiple_persons_of_interest(poi)
        self.airline.add_flight("test-flight", list(passengers))

        # Test using the buscaComunes function
        result = buscaComunes(poi, passengers)
        self.assertEqual(result, expected)

        # Test using the class-based approach
        psi_client = self.authority.create_psi_client()
        class_result = self.airline.find_common_persons("test-flight", psi_client)
        self.assertEqual(class_result, expected)

    def test_empty_intersection(self):
        """Test when there is no intersection."""
        # Create test data
        poi = {"John Smith", "Maria Rodriguez", "Ahmed Hassan"}
        passengers = {"Sofia Garcia", "Michael Wilson", "Emma Johnson"}
        expected = set()

        # Add data to the authority and airline
        self.authority.add_multiple_persons_of_interest(poi)
        self.airline.add_flight("test-flight", list(passengers))

        # Test using the buscaComunes function
        result = buscaComunes(poi, passengers)
        self.assertEqual(result, expected)

        # Test using the class-based approach
        psi_client = self.authority.create_psi_client()
        class_result = self.airline.find_common_persons("test-flight", psi_client)
        self.assertEqual(class_result, expected)

    def test_full_intersection(self):
        """Test when all passengers are persons of interest."""
        # Create test data
        poi = {"John Smith", "Maria Rodriguez", "Ahmed Hassan", "Sofia Garcia"}
        passengers = {"John Smith", "Maria Rodriguez", "Ahmed Hassan"}
        expected = {"John Smith", "Maria Rodriguez", "Ahmed Hassan"}

        # Add data to the authority and airline
        self.authority.add_multiple_persons_of_interest(poi)
        self.airline.add_flight("test-flight", list(passengers))

        # Test using the buscaComunes function
        result = buscaComunes(poi, passengers)
        self.assertEqual(result, expected)

        # Test using the class-based approach
        psi_client = self.authority.create_psi_client()
        class_result = self.airline.find_common_persons("test-flight", psi_client)
        self.assertEqual(class_result, expected)

    def test_large_dataset(self):
        """Test with a larger dataset."""
        # Generate a large dataset with known overlap
        all_names = generate_dataset(1000)
        poi_names = set(random.sample(list(all_names), 100))
        passenger_names = set(random.sample(list(all_names), 200))

        # Ensure some overlap
        overlap_size = 20
        overlap = set(random.sample(list(all_names), overlap_size))
        poi_names.update(overlap)
        passenger_names.update(overlap)

        # Expected result is the overlap
        expected = poi_names.intersection(passenger_names)

        # Add data to the authority and airline
        self.authority.add_multiple_persons_of_interest(poi_names)
        self.airline.add_flight("test-flight", list(passenger_names))

        # Test using the buscaComunes function
        result = buscaComunes(poi_names, passenger_names)
        self.assertEqual(result, expected)

        # Test using the class-based approach
        psi_client = self.authority.create_psi_client()
        class_result = self.airline.find_common_persons("test-flight", psi_client)
        self.assertEqual(class_result, expected)

    def test_loading_from_files(self):
        """Test loading data from files."""
        # Create test files
        poi_file = os.path.join(self.authority.storage_path, "test_poi.txt")
        passengers_file = os.path.join(self.airline.storage_path, "test_passengers.txt")

        poi = ["John Smith", "Maria Rodriguez", "Ahmed Hassan"]
        passengers = ["Sofia Garcia", "John Smith", "Michael Wilson"]
        expected = {"John Smith"}

        # Write test files
        with open(poi_file, "w") as f:
            for name in poi:
                f.write(f"{name}\n")

        with open(passengers_file, "w") as f:
            for name in passengers:
                f.write(f"{name}\n")

        # Load data from files
        self.authority.load_persons_of_interest_from_file(poi_file)
        self.airline.load_passengers_from_file("test-flight", passengers_file)

        # Test using the class-based approach
        psi_client = self.authority.create_psi_client()
        result = self.airline.find_common_persons("test-flight", psi_client)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
