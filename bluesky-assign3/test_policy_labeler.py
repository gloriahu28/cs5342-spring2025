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
    parser.add_argument("--output_file", type=str, help="Output file for detailed results")
    args = parser.parse_args()

    # Create the labeler
    labeler = PolicyProposalLabeler(client, args.labeler_inputs_dir)
    
    # Load test data
    with open(args.test_urls_file, 'r') as f:
        test_posts = json.load(f)
    
    # Run tests and get metrics
    print(f"Testing on {len(test_posts)} posts...")
    metrics = labeler.test_labeler(test_posts)
    
    # Report results
    results = metrics["results"]
    success_count = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\nTEST RESULTS:")
    print(f"The labeler produced {success_count} correct label assignments out of {total}")
    print(f"Overall accuracy: {metrics['accuracy']:.2f}")
    
    print(f"\nCLASSIFICATION METRICS:")
    print(f"Precision: {metrics['precision']:.2f}")
    print(f"Recall: {metrics['recall']:.2f}")
    print(f"F1 score: {metrics['f1']:.2f}")
    
    cm = metrics["confusion_matrix"]
    print(f"\nCONFUSION MATRIX:")
    print(f"True Positives: {cm['true_positives']}")
    print(f"False Positives: {cm['false_positives']}")
    print(f"True Negatives: {cm['true_negatives']}")
    print(f"False Negatives: {cm['false_negatives']}")
    
    perf = metrics["performance"]
    print(f"\nPERFORMANCE METRICS:")
    print(f"Average processing time: {perf['avg_processing_time']:.4f} seconds")
    print(f"Maximum processing time: {perf['max_processing_time']:.4f} seconds")
    print(f"Minimum processing time: {perf['min_processing_time']:.4f} seconds")
    print(f"Standard deviation: {perf['std_processing_time']:.4f} seconds")
    
    # Optionally save metrics to a file
    if hasattr(args, 'output_file') and args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"\nDetailed results saved to {args.output_file}")

if __name__ == "__main__":
    main()