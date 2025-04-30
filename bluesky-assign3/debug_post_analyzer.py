"""Script to debug post analysis issues"""

import os
import json
from atproto import Client
from dotenv import load_dotenv

from pylabel import PolicyProposalLabeler, label, post_from_url

load_dotenv(override=True)
USERNAME = os.getenv("USERNAME")
PW = os.getenv("PW")

def analyze_post_details(url, client):
    """Analyze a post in detail to see what content is being detected"""
    post = post_from_url(client, url)
    
    if not post or not hasattr(post, 'value'):
        print(f"Warning: Could not retrieve post {url}")
        return
    
    print(f"\nAnalyzing post: {url}")
    
    # Print post text
    if hasattr(post.value, 'text'):
        post_text = post.value.text
        print(f"Post text: {post_text}")
        
        # Analyze for sexual terms
        labeler = PolicyProposalLabeler(client, "labeler-inputs")
        contains_sexual_terms = labeler._contains_sexual_terms(post_text)
        print(f"Contains sexual terms: {contains_sexual_terms}")
        
        # If no sexual terms found, print the terms dictionary
        if not contains_sexual_terms:
            print(f"Sexual terms dictionary: {labeler.primary_terms}")
            print("Checking for hashtags...")
            
            # Check specifically for hashtags
            hashtags = [word for word in post_text.split() if word.startswith('#')]
            print(f"Hashtags in post: {hashtags}")
            
            for hashtag in hashtags:
                # Remove the # and check if the term is in the dictionary
                term = hashtag[1:].lower()
                print(f"Checking hashtag term: {term}")
                print(f"Term in dictionary: {term in labeler.primary_terms}")
        
        # Check for solicitation
        is_solicitation = labeler._indicates_solicitation(post_text)
        print(f"Indicates solicitation: {is_solicitation}")
        
        # Check for legitimate context
        is_legitimate = labeler._indicates_legitimate_context(post_text)
        print(f"Indicates legitimate context: {is_legitimate}")
        
        # Check explicit intensity
        intensity = labeler._explicit_intensity(post_text)
        print(f"Explicit intensity score: {intensity}")
        
        # Final analysis result
        should_label = labeler._analyze_post_content(post_text)
        print(f"Analysis result - should label: {should_label}")
    
    # Check for images
    if hasattr(post.value, 'embed'):
        print("Post has embed content")
        
        # Extract image URLs
        labeler = PolicyProposalLabeler(client, "labeler-inputs")
        image_urls = labeler._extract_image_urls(post.value)
        print(f"Image URLs found: {len(image_urls)}")
        for url in image_urls:
            print(f"  - {url}")

def main():
    """Main function for debugging"""
    client = Client()
    client.login(USERNAME, PW)
    
    # Test a single post first
    test_url = "https://bsky.app/profile/babes2025.bsky.social/post/3lnsrbkn6rd2z"
    analyze_post_details(test_url, client)
    
    # Test another post
    test_url_2 = "https://bsky.app/profile/ayla-jay.bsky.social/post/3lno4akjgv22h"
    analyze_post_details(test_url_2, client)

if __name__ == "__main__":
    main()