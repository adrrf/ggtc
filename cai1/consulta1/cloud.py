import os
from utils import compute_hmac


class Cloud:
    def __init__(self, storage_dir="cloud_storage"):
        """Initialize the cloud with a storage directory."""
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self.stored_challenges = {}  # For simulating replay attacks

    def upload_file(self, filename, content):
        """
        Simulate uploading a file to the cloud.
        """
        filepath = os.path.join(self.storage_dir, filename)
        with open(filepath, "wb") as f:
            f.write(content)
        return True

    def challenge(self, filename, nonce):
        """
        Respond to an integrity challenge by:
        1. Retrieving the file
        2. Computing the HMAC with the provided nonce
        3. Returning the hash
        """
        filepath = os.path.join(self.storage_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File {filename} not found in cloud storage")

        with open(filepath, "rb") as f:
            file_content = f.read()

        # Store this challenge response for potential replay attacks
        response = compute_hmac(file_content, nonce)
        self.stored_challenges[filename] = {"nonce": nonce, "response": response}

        # Compute HMAC using the challenge nonce
        return response

    def malicious_challenge(self, filename, nonce):
        """
        A malicious version of challenge that always returns a previously computed hash
        regardless of the new nonce. This simulates a replay attack.
        """
        if filename in self.stored_challenges:
            # Return a previously calculated hash, ignoring the new nonce
            return self.stored_challenges[filename]["response"]
        else:
            # If we haven't seen this file before, compute normally but store for future
            return self.challenge(filename, nonce)
