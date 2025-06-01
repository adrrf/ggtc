"""
Client implementation for Information-Theoretic PIR protocol
"""

import os
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from pathlib import Path
from colorama import Fore, Style


class Client:
    """Client class for PIR protocol"""

    def __init__(self, storage_dir: str = "client_storage"):
        """Initialize the client with a storage directory"""
        self.storage_dir = storage_dir

        # Create storage directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)

        # Load metadata if it exists
        self.metadata_path = Path(self.storage_dir) / "metadata.json"
        self.metadata = self._load_metadata()

        # Flight data
        self.flight_info = None

    def _load_metadata(self) -> Dict[str, Any]:
        """Load metadata from storage or create if it doesn't exist"""
        if self.metadata_path.exists():
            with open(self.metadata_path, "r") as f:
                return json.load(f)
        return {"last_query": None, "available_flights": []}

    def _save_metadata(self) -> None:
        """Save metadata to storage"""
        with open(self.metadata_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def load_flight_info(self, flight_info: pd.DataFrame) -> None:
        """Load flight information (but not prices)"""
        # Make a copy of the DataFrame to avoid modifying the original
        flight_info_copy = flight_info.copy()
        
        # Save basic flight info to client storage (without prices)
        flight_info_copy.drop(columns=["price"], inplace=True, errors="ignore")
        self.flight_info = flight_info_copy
        flight_info_copy.to_csv(f"{self.storage_dir}/flight_info.csv", index=False)

        # Update metadata
        self.metadata["available_flights"] = flight_info_copy["flight_id"].tolist()
        self._save_metadata()

        print(f"Client: Loaded information for {len(flight_info_copy)} flights")

    def generate_query_vectors(
        self, flight_index: int, num_flights: int
    ) -> Tuple[List[int], List[int]]:
        """
        Generate query vectors for retrieving the price of a specific flight

        Args:
            flight_index: The index of the flight to retrieve
            num_flights: Total number of flights

        Returns:
            Tuple containing:
            - query1: Random vector K for server 1
            - query2: Vector K+E for server 2, where E is the unit vector for flight_index
        """
        # Generate random vector K with values in a reasonable range
        K = np.random.randint(1, 100, size=num_flights).tolist()

        # Create unit vector E with 1 at flight_index and 0 elsewhere
        E = np.zeros(num_flights, dtype=int)
        E[flight_index] = 1

        # Compute K+E for the second server
        K_plus_E = (np.array(K) + E).tolist()

        return K, K_plus_E

    def retrieve_flight_price(self, server1, server2, flight_id: str) -> int:
        """
        Retrieve the price of a specific flight using PIR

        Args:
            server1: The first PIR server
            server2: The second PIR server
            flight_id: The ID of the flight to retrieve the price for

        Returns:
            The price of the requested flight
        """
        if self.flight_info is None:
            raise ValueError(
                "Flight information not loaded. Call load_flight_info first."
            )

        # Find the index of the flight in the flight info
        flight_df = self.flight_info[self.flight_info["flight_id"] == flight_id]
        if flight_df.empty:
            raise ValueError(f"Flight with ID {flight_id} not found")

        flight_index = self.flight_info[
            self.flight_info["flight_id"] == flight_id
        ].index[0]
        num_flights = len(self.flight_info)

        # Generate query vectors
        K, K_plus_E = self.generate_query_vectors(flight_index, num_flights)

        # Send queries to servers
        result1 = server1.process_query(K)  # K·X
        result2 = server2.process_query(K_plus_E)  # (K+E)·X

        # Calculate the price: (K+E)·X - K·X = E·X = price of the requested flight
        price = result2 - result1

        # Update metadata
        self.metadata["last_query"] = pd.Timestamp.now().isoformat()
        self._save_metadata()

        print(
            f"Retrieved price for flight {flight_id} without revealing the flight ID to servers"
        )
        return price

    def display_flight_info(self):
        """Display available flight information"""
        if self.flight_info is None or len(self.flight_info) == 0:
            print("No flight information available")
            return

        print(f"\n{Fore.CYAN}Available Flights:{Style.RESET_ALL}")
        for _, flight in self.flight_info.iterrows():
            flight_str = f"ID: {flight['flight_id']} | From: {flight['origin']} | To: {flight['destination']} | Date: {flight['date']}"
            print(flight_str)
        print("")
