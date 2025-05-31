import os
import pickle


class Cloud:
    def __init__(self, storage_dir="cloud_storage"):
        """Initialize the cloud with a storage directory."""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.data_file = os.path.join(storage_dir, "encrypted_data.txt")
        self.pickle_file = os.path.join(storage_dir, "encrypted_objects.pickle")
        self._encrypted_objects = {}  # In-memory storage for encrypted objects
        self.data = self._load_data()
        self._load_encrypted_objects()

    def _load_data(self):
        """Load data from text file if it exists."""
        data_dict = {}
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r") as f:
                    lines = f.read().strip().split("\n")
                    for line in lines:
                        if not line.strip():
                            continue
                        parts = line.split(":")
                        if len(parts) >= 3:
                            year = parts[0].strip()
                            passenger_id = parts[1].strip()

                            if year not in data_dict:
                                data_dict[year] = {}
                            # Just store the reference, actual objects will be loaded separately
                            data_dict[year][passenger_id] = f"{year}:{passenger_id}"
            except Exception as e:
                print(f"Error loading data: {e}")
        return data_dict

    def _load_encrypted_objects(self):
        """Load encrypted objects from pickle file."""
        if os.path.exists(self.pickle_file):
            try:
                with open(self.pickle_file, "rb") as f:
                    self._encrypted_objects = pickle.load(f)
            except Exception as e:
                print(f"Error loading encrypted objects: {e}")

    def _save_data(self):
        """Save data to file in text format."""
        try:
            # Save references to text file
            with open(self.data_file, "w") as f:
                for year, passengers in self.data.items():
                    for passenger_id in passengers.keys():
                        f.write(
                            f"{year}:{passenger_id}:{id(self._encrypted_objects.get(f'{year}:{passenger_id}'))}\n"
                        )

            # Save actual encrypted objects to pickle file
            with open(self.pickle_file, "wb") as f:
                pickle.dump(self._encrypted_objects, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    def store_encrypted_expense(self, passenger_id, year, encrypted_expense):
        """
        Store an encrypted expense in the cloud.
        """
        if year not in self.data:
            self.data[year] = {}

        # Create a reference key
        key = f"{year}:{passenger_id}"

        # Store the reference in the data dictionary
        self.data[year][passenger_id] = key

        # Store the actual encrypted object in our in-memory dictionary
        self._encrypted_objects[key] = encrypted_expense

        # Save both to disk
        self._save_data()
        return True

    def calculate_expenses_sum(self, year):
        """
        Calculate the sum of encrypted expenses for a specific year.
        This is the homomorphic operation that works on encrypted data.
        """
        if year not in self.data or not self.data[year]:
            return None

        # Get all passenger IDs for this year
        passenger_ids = list(self.data[year].keys())

        # Get the first encrypted expense
        first_key = f"{year}:{passenger_ids[0]}"
        encrypted_sum = self._encrypted_objects.get(first_key)

        if encrypted_sum is None:
            print(f"Warning: Could not find encrypted expense for {first_key}")
            return None

        # Add the remaining expenses
        for passenger_id in passenger_ids[1:]:
            key = f"{year}:{passenger_id}"
            encrypted_expense = self._encrypted_objects.get(key)

            if encrypted_expense is None:
                print(f"Warning: Could not find encrypted expense for {key}")
                continue

            encrypted_sum += encrypted_expense

        return encrypted_sum

    def sumaGastos(self, Gastos_Acumulados_Confiden, Gasto_de_Vuelo_Confiden):
        """
        Implementation of the sumaGastos function as specified in the requirements.
        This function adds encrypted expenses without knowing their actual values.
        """
        return Gastos_Acumulados_Confiden + Gasto_de_Vuelo_Confiden
