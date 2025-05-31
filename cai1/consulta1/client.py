import os
import json
from utils import generate_nonce, compute_hmac, compare_digests


class Client:
    def __init__(
        self, storage_dir="client_storage", num_nonces=5, num_precalculated_hashes=10
    ):
        """Initialize the client with a storage directory and generate predefined nonces."""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.metadata_file = os.path.join(storage_dir, "metadata.json")
        self.metadata = self._load_metadata()

        # Generate predefined nonces for challenges
        self.nonces = [generate_nonce() for _ in range(num_nonces)]
        self.current_nonce_index = 0

        # Number of precalculated hashes to generate for each file
        self.num_precalculated_hashes = num_precalculated_hashes

    def _load_metadata(self):
        """Load metadata from file if it exists."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        """Save metadata to file."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f)

    def get_next_nonce(self):
        """Get the next predefined nonce in the sequence."""
        nonce = self.nonces[self.current_nonce_index]
        self.current_nonce_index = (self.current_nonce_index + 1) % len(self.nonces)
        return nonce

    def process_file(self, filepath):
        """
        Process a file according to the integrity verification process.
        1. Generate a nonce
        2. Compute HMAC of the file using the nonce
        3. Store the file and hash locally
        4. Precalculate additional hashes with different nonces
        5. Upload the file to the cloud (mock)
        """
        filename = os.path.basename(filepath)

        # 1. Read the file content
        with open(filepath, "rb") as f:
            file_content = f.read()

        # 2. Generate a nonce
        nonce = self.get_next_nonce()

        # 3. Compute HMAC of the file using the nonce
        file_hash = compute_hmac(file_content, nonce)

        # 4. Store the file locally
        local_filepath = os.path.join(self.storage_dir, filename)
        with open(local_filepath, "wb") as f:
            f.write(file_content)

        # 5. Precalculate additional hashes with different nonces
        precalculated_hashes = {}
        for _ in range(self.num_precalculated_hashes):
            precalc_nonce = generate_nonce()
            precalc_hash = compute_hmac(file_content, precalc_nonce)
            precalculated_hashes[precalc_nonce.hex()] = precalc_hash.hex()

        # 6. Store metadata (including hash, nonce, and precalculated hashes)
        self.metadata[filename] = {
            "original_path": filepath,
            "local_path": local_filepath,
            "nonce": nonce.hex(),
            "hash": file_hash.hex(),
            "precalculated_hashes": precalculated_hashes,
            "used_hashes": [],  # Track which precalculated hashes have been used
        }
        self._save_metadata()

        # 7. "Upload" to cloud (mock by calling the cloud module)
        from cloud import Cloud

        cloud = Cloud()
        cloud.upload_file(filename, file_content)

        return filename

    def verify_file_integrity(self, filename):
        """
        Verify the integrity of a file by:
        1. Checking if we have a precalculated hash to use
        2. If yes, use that hash instead of computing a new one
        3. If no, generate a new nonce for the challenge and compute the hash
        4. Comparing the local hash with the one received from the cloud
        """
        import logging

        logger = logging.getLogger(__name__)

        if filename not in self.metadata:
            raise ValueError(f"File {filename} not found in metadata")

        file_metadata = self.metadata[filename]
        from cloud import Cloud

        cloud = Cloud()

        # Check if we have unused precalculated hashes
        precalculated = file_metadata.get("precalculated_hashes", {})
        used_hashes = file_metadata.get("used_hashes", [])

        # Find an unused precalculated hash
        available_nonces = [n for n in precalculated.keys() if n not in used_hashes]

        if available_nonces:
            # 1. Use a precalculated hash
            challenge_nonce_hex = available_nonces[0]
            challenge_nonce = bytes.fromhex(challenge_nonce_hex)
            local_hash_hex = precalculated[challenge_nonce_hex]
            local_hash = bytes.fromhex(local_hash_hex)

            # Mark this hash as used
            used_hashes.append(challenge_nonce_hex)
            file_metadata["used_hashes"] = used_hashes
            self._save_metadata()

            # Log that we're using a precalculated hash
            remaining = len(available_nonces) - 1
            logger.info(
                f"🔄 Using precalculated hash for {filename}. {remaining} unused hashes remaining."
            )

            # Send the challenge to the cloud
            cloud_hash = cloud.challenge(filename, challenge_nonce)

            # Compare the hashes
            return compare_digests(local_hash, cloud_hash)
        else:
            # 2. No precalculated hashes available, generate a new nonce
            logger.info(
                f"⚠️ No precalculated hashes available for {filename}. Computing new hash."
            )

            challenge_nonce = self.get_next_nonce()

            # Send the challenge to the cloud
            cloud_hash = cloud.challenge(filename, challenge_nonce)

            # Compute the hash locally
            local_filepath = file_metadata["local_path"]
            with open(local_filepath, "rb") as f:
                file_content = f.read()

            local_hash = compute_hmac(file_content, challenge_nonce)

            # Compare the hashes
            return compare_digests(local_hash, cloud_hash)
