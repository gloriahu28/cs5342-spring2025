"""Test script for policy proposal labeler"""

import argparse
import os
import json

from atproto import Client
from dotenv import load_dotenv

from pylabel import PolicyProposalLabeler

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PW = os.getenv("PW")

def main():
    """
    Main function for the test script
    """
    client = Client()
    client.login(USERNAME, PW)

    parser = argparse.ArgumentParser()
    parser.add_argument("labeler_inputs_dir", type=str, help="Directory containing input files")
    parser.add_argument("test_urls_file", type=str, help="JSON file with test URLs and expected labels")
    parser.add_argument("--emit_labels", action="store_true", help="Whether to emit labels to Bluesky")
    args = parser.parse_args()

    # Create the labeler
    labeler = PolicyProposalLabeler(client, args.labeler_inputs_dir)
    
    # Load test data
    with open(args.test_urls_file, 'r') as f:
        test_posts = json.load(f)
    
    # Run tests
    results = labeler.test_labeler(test_posts)
    
    # Report results
    success_count = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"The labeler produced {success_count} correct label assignments out of {total}")
    print(f"Overall accuracy: {success_count/total:.2f}")

if __name__ == "__main__":
    main()