"""
Server implementation for Information-Theoretic PIR protocol
"""

import os
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from pathlib import Path


class Server:
    """Base server class for PIR protocol"""

    def __init__(self, server_id: int, storage_dir: str = None):
        """Initialize the server with a server ID and storage directory"""
        self.server_id = server_id
        self.storage_dir = storage_dir or f"server{server_id}_storage"
        self.flight_prices = None

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)

        # Load metadata if it exists
        self.metadata_path = Path(self.storage_dir) / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from storage or create if it doesn't exist"""
        if self.metadata_path.exists():
            with open(self.metadata_path, "r") as f:
                return json.load(f)
        return {"last_update": None, "num_flights": 0}

    def _save_metadata(self) -> None:
        """Save metadata to storage"""
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def store_flight_data(self, flight_data: pd.DataFrame) -> None:
        """Store flight data on the server"""
        # Store the flight prices as a vector
        self.flight_prices = flight_data["price"].values

        # Save the flight data to storage
        flight_data.to_csv(f"{self.storage_dir}/flight_data.csv", index=False)

        # Update metadata
        self.metadata["last_update"] = pd.Timestamp.now().isoformat()
        self.metadata["num_flights"] = len(flight_data)
        self._save_metadata()

        print(f"Server {self.server_id}: Stored {len(flight_data)} flight prices")

    def process_query(self, query_vector: List[int]) -> int:
        """
        Process a query vector and return the dot product with flight prices

        For server 1: Returns K·X
        For server 2: Returns (K+E)·X
        """
        if self.flight_prices is None:
            raise ValueError("Flight data not loaded. Call store_flight_data first.")

        # Convert query vector to numpy array
        query_array = np.array(query_vector)

        # Calculate dot product between query vector and flight prices
        # Using direct sum as specified (no XOR)
        result = np.dot(query_array, self.flight_prices)

        return result


class Server1(Server):
    """First server implementation for PIR protocol"""

    def __init__(self):
        super().__init__(server_id=1)

    def process_query(self, query_vector: List[int]) -> int:
        """Process the random vector K and return K·X"""
        return super().process_query(query_vector)


class Server2(Server):
    """Second server implementation for PIR protocol"""

    def __init__(self):
        super().__init__(server_id=2)

    def process_query(self, query_vector: List[int]) -> int:
        """Process the vector K+E and return (K+E)·X"""
        return super().process_query(query_vector)
