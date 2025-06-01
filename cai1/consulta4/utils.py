"""
Utility functions for PIR protocol
"""

import os
import numpy as np
import pandas as pd
from typing import List, Dict, Any
import json
from pathlib import Path


def generate_sample_flight_data(num_flights: int = 20) -> pd.DataFrame:
    """
    Generate sample flight data for testing

    Args:
        num_flights: Number of flights to generate

    Returns:
        DataFrame with flight information including prices
    """
    origins = ["Madrid", "Barcelona", "Valencia", "Bilbao", "Sevilla", "Málaga"]
    destinations = [
        "London",
        "Paris",
        "Berlin",
        "Rome",
        "Amsterdam",
        "Brussels",
        "Lisbon",
        "Vienna",
    ]

    np.random.seed(42)  # For reproducibility

    # Generate random flight data
    data = []
    for i in range(num_flights):
        origin = np.random.choice(origins)
        dest = np.random.choice([d for d in destinations if d])
        flight_id = f"FL{i+100}"

        # Generate a random date in 2025
        month = np.random.randint(1, 13)
        day = np.random.randint(1, 29)
        date = f"2025-{month:02d}-{day:02d}"

        # Generate random price between 50 and 500
        price = np.random.randint(50, 501)

        data.append(
            {
                "flight_id": flight_id,
                "origin": origin,
                "destination": dest,
                "date": date,
                "price": price,
            }
        )

    return pd.DataFrame(data)


def clear_storage_directories():
    """Clear all storage directories for fresh testing"""
    import shutil

    dirs = ["server1_storage", "server2_storage", "client_storage"]
    for dir_path in dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
            print(f"Cleared {dir_path}")
        os.makedirs(dir_path, exist_ok=True)
