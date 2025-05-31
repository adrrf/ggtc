import os
import sys
import argparse
import logging
from client import Client
from cloud import Cloud

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_test_file(filename, content="This is a test file content"):
    """Create a test file with some content."""
    with open(filename, "w") as f:
        f.write(content)
    return filename


def main():
    parser = argparse.ArgumentParser(description="File integrity verification demo")
    parser.add_argument(
        "--action",
        choices=["upload", "verify", "demo"],
        default="demo",
        help="Action to perform",
    )
    parser.add_argument("--file", help="File to process")
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )
    parser.add_argument(
        "--num-nonces",
        type=int,
        default=5,
        help="Number of predefined nonces to generate",
    )
    parser.add_argument(
        "--num-precalculated-hashes",
        type=int,
        default=10,
        help="Number of precalculated hashes to generate for each file",
    )
    args = parser.parse_args()

    # Set log level based on argument
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    client = Client(
        num_nonces=args.num_nonces,
        num_precalculated_hashes=args.num_precalculated_hashes,
    )

    if args.action == "upload":
        if not args.file:
            logger.error("❌ Error: --file argument is required for upload action")
            return 1

        filename = client.process_file(args.file)
        logger.info(f"✅ File {filename} processed and uploaded to mock cloud ☁️")

    elif args.action == "verify":
        if not args.file:
            logger.error("❌ Error: --file argument is required for verify action")
            return 1

        filename = os.path.basename(args.file)
        result = client.verify_file_integrity(filename)

        if result:
            logger.info(f"🟢 File {filename} integrity verification: SUCCESS ✅")
        else:
            logger.error(f"🔴 File {filename} integrity verification: FAILED ❌")

    elif args.action == "demo":
        logger.info("=== 🗂️ COMPREHENSIVE FILE INTEGRITY VERIFICATION DEMO 🗂️ ===")

        # Case 1: Upload and verify successful case
        logger.info("=== CASE 1: Upload and verify (successful case) 🟢 ===")
        test_file1 = create_test_file(
            "valid_file.txt", "This file will remain untampered"
        )
        logger.info(f"📝 Created test file: {test_file1}")

        filename1 = client.process_file(test_file1)
        logger.info(f"☁️ File {filename1} processed and uploaded to cloud")

        result1 = client.verify_file_integrity(filename1)
        logger.info(
            f"🔍 File integrity verification: {'SUCCESS ✅' if result1 else 'FAILED ❌'}"
        )

        # Case 2: Upload, tamper, and verify (should fail)
        logger.info("=== CASE 2: Upload, tamper, and verify (should fail) 🔴 ===")
        test_file2 = create_test_file(
            "tampered_file.txt", "This file will be tampered with"
        )
        logger.info(f"📝 Created test file: {test_file2}")

        filename2 = client.process_file(test_file2)
        logger.info(f"☁️ File {filename2} processed and uploaded to cloud")

        # Tampering with the file in the cloud
        cloud = Cloud()
        cloud_file_path = os.path.join(cloud.storage_dir, filename2)
        logger.warning(f"⚠️ Tampering with file in cloud storage: {cloud_file_path}")

        with open(cloud_file_path, "ab") as f:
            f.write(b"TAMPERED CONTENT ADDED")

        result2 = client.verify_file_integrity(filename2)
        if not result2:
            logger.info("🔍 File integrity verification after tampering: FAILED ❌")
            logger.info("✓ Successfully detected tampering! 🛡️")
        else:
            logger.error("🔍 File integrity verification after tampering: SUCCESS ✅")
            logger.error("✗ Failed to detect tampering! ⚠️")

        # Case 3: Replay attack - tampered file returns old hash
        # This simulates an attack where a malicious server returns a previously calculated hash
        # rather than computing a new one with the challenge nonce
        logger.info("=== CASE 3: Replay attack - tampered file returns old hash 🔴 ===")
        logger.info(
            "📊 This demonstrates why using different nonces for each verification is critical."
        )
        logger.info(
            "📝 In this attack, the server is modified to ignore the challenge nonces."
        )
        logger.info(
            "📝 Instead, it returns a previously calculated hash - "
            "this would normally let tampered files pass verification."
        )

        test_file3 = create_test_file(
            "replay_attack.txt", "This file will demonstrate a replay attack"
        )
        logger.info(f"📝 Created test file: {test_file3}")

        filename3 = client.process_file(test_file3)
        logger.info(f"☁️ File {filename3} processed and uploaded to cloud")

        # First verification should pass
        logger.info("🔄 Performing first legitimate verification...")
        valid_result = client.verify_file_integrity(filename3)
        logger.info(
            f"🔍 Initial verification: {'SUCCESS ✅' if valid_result else 'FAILED ❌'}"
        )

        # Now tamper with the file in the cloud
        cloud = Cloud()
        cloud_file_path = os.path.join(cloud.storage_dir, filename3)
        logger.warning(f"⚠️ Tampering with file in cloud storage: {cloud_file_path}")
        with open(cloud_file_path, "ab") as f:
            f.write(b"\nTAMPERED CONTENT FOR REPLAY ATTACK")

        # Save the original challenge method
        original_challenge = cloud.challenge

        # Use the built-in malicious challenge method that returns old hashes
        logger.warning(
            "🕵️ Simulating a malicious cloud server that returns old hash values..."
        )

        # Monkey patch the Cloud instance to use the malicious challenge method
        cloud.challenge = cloud.malicious_challenge

        # Now try to verify - should normally fail, but with replay attack might succeed
        logger.info("🔍 Attempting verification with tampered file (replay attack)...")
        replay_result = client.verify_file_integrity(filename3)

        if not replay_result:
            logger.info("🔍 File integrity verification with replay attack: FAILED ❌")
            logger.info("✓ Successfully detected replay attack! 🛡️")
        else:
            logger.error(
                "🔍 File integrity verification with replay attack: SUCCESS ✅"
            )
            logger.error(
                "✗ Failed to detect replay attack! This is a security issue! ⚠️"
            )

        # Restore the original challenge method
        cloud.challenge = original_challenge

        logger.info("=== 🎉 DEMO COMPLETE 🎉 ===")
        logger.info("📋 Summary:")
        logger.info(f"Case 1 (Untampered): {'PASSED 🟢' if result1 else 'FAILED 🔴'}")
        logger.info(
            f"Case 2 (Tampered in cloud): {'PASSED 🟢' if not result2 else 'FAILED 🔴'} (expected failure)"
        )
        logger.info(
            f"Case 3 (Replay attack): {'PASSED 🟢' if not replay_result else 'FAILED 🔴'} (expected failure)"
        )

        logger.info("🧹 Cleaning up test files...")
        for test_file in [test_file1, test_file2, test_file3]:
            try:
                if os.path.exists(test_file):
                    os.remove(test_file)
                    logger.debug(f"Deleted test file: {test_file}")

                # Also clean up files from cloud storage
                cloud_path = os.path.join(
                    cloud.storage_dir, os.path.basename(test_file)
                )
                if os.path.exists(cloud_path):
                    os.remove(cloud_path)
                    logger.debug(f"Deleted cloud file: {cloud_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file {test_file}: {str(e)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
