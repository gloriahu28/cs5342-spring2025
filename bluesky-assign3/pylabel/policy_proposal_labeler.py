"""Implementation of policy proposal labeler for unwanted sexual content

This labeler aims to detect and label posts containing potentially unwanted sexual 
communication, focusing on both unsolicited sexually explicit text and images. It 
implements a moderation approach as outlined in Assignment 2, applying detection 
techniques to identify inappropriate content patterns.

The labeler attaches a "sexual-content" label to posts that match detection criteria.
"""

from typing import List, Optional, Dict, Any, Set, Tuple
import re
import os
import json
import requests
import numpy as np
import time
from perception import hashers
from PIL import Image
from io import BytesIO
from atproto import Client

from .label import post_from_url

# Define the label we'll use
SEXUAL_CONTENT_LABEL = "sexual-content"

class PolicyProposalLabeler:
    """
    Labeler implementation for unwanted sexual content
    This focuses on detecting sexually explicit text and image content that may be unwanted
    """

    def __init__(self, client: Client, input_dir: str):
        """
        Initialize the labeler with necessary components
        
        Args:
            client: AT Protocol client for accessing posts
            input_dir: Directory containing input files for the labeler
        """
        self.client = client
        self.input_dir = input_dir
        self.image_hash_threshold = 10  # Threshold for perceptual hash matching (lower = stricter)
        
        # Load dictionaries of sexual terms and phrases
        self._load_dictionaries()
        
        # Initialize image hash database
        self._init_image_database()
        
        # Define patterns that indicate solicitation or unwanted communication
        self.solicitation_patterns = [
            r'\b(?:send|share|give|show|post|upload)\s+(?:me|us|your)\b',
            r'\b(?:dm|pm|message|chat)\s+(?:me|us)\b',
            r'\b(?:want|looking for|seeking|need).{0,30}(?:pics|pictures|photos|vids|videos|content)\b',
            r'\b(?:add|follow).{0,20}(?:premium|private|exclusive)\b'
        ]
        
        # Define patterns that might indicate consent or legitimate discussion
        self.legitimate_context_patterns = [
            r'\b(?:discuss|discussing|conversation|talking about|education|educational|research|article|study|health|medical)\b',
            r'\b(?:policy|policies|guidelines|terms|rules|moderation|safety)\b',
            r'\b(?:report|reporting|flagging|harmful|abusive)\b'
        ]
    
    def _load_dictionaries(self):
        """Load dictionaries of terms from files or define them inline"""
        # Primary sexual terms dictionary - terms that are explicitly sexual
        self.primary_terms = {
            "nsfw", "explicit", "pornographic", "sexual", "nude", "nudity", 
            "intimate", "obscene", "lewd", "indecent", "nudist", "nudism",
            "artnude", "fineartnude", "artisticnude", "nudeart", "nudemodel",
            "naked", "erotica", "erotic", "sexy", "sensual", "boudoir"
        }
        
        # Try to load additional terms from file if available
        try:
            terms_file = os.path.join(self.input_dir, "sexual_terms.json")
            if os.path.exists(terms_file):
                with open(terms_file, 'r') as f:
                    loaded_terms = json.load(f)
                    self.primary_terms.update(loaded_terms)
        except Exception as e:
            print(f"Warning: Could not load sexual terms file: {e}")
    
    def _init_image_database(self):
        """Initialize the image database for matching potentially inappropriate images"""
        self.image_hasher = hashers.PHash()
        self.known_nsfw_hashes = []
        
        # Ideally, load hashes from a database file
        # For this implementation, we'll use a sample approach
        try:
            # Try to load image hashes from a sample file if it exists
            sample_hashes_file = os.path.join(self.input_dir, "nsfw_image_hashes.json")
            if os.path.exists(sample_hashes_file):
                with open(sample_hashes_file, 'r') as f:
                    self.known_nsfw_hashes = json.load(f)
            else:
                print("No image hash database found. Will rely on other detection methods.")
        except Exception as e:
            print(f"Warning: Could not load image hash database: {e}")
    
    def _check_for_hashtags(self, text: str) -> bool:
        """
        Specifically check for hashtags containing sexual terms
        
        Args:
            text: Text content to analyze
            
        Returns:
            True if sexual hashtags are found, False otherwise
        """
        # Extract hashtags
        hashtags = [word[1:].lower() for word in text.split() if word.startswith('#')]
        
        # Check if any hashtag is in our primary terms dictionary
        for hashtag in hashtags:
            if any(term in hashtag for term in self.primary_terms):
                return True
                
        return False
    
    def _contains_sexual_terms(self, text: str) -> bool:
        """
        Check if text contains sexual terminology
        
        Args:
            text: Text content to analyze
            
        Returns:
            True if sexual terms are found, False otherwise
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Check for primary sexual terms
        for term in self.primary_terms:
            if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
                return True
        
        # Check for hashtags containing sexual terms
        if self._check_for_hashtags(text):
            return True
            
        return False
    
    def _indicates_solicitation(self, text: str) -> bool:
        """
        Check if text contains patterns indicating solicitation
        
        Args:
            text: Text content to analyze
            
        Returns:
            True if solicitation patterns are found, False otherwise
        """
        text_lower = text.lower()
        
        for pattern in self.solicitation_patterns:
            if re.search(pattern, text_lower):
                return True
                
        return False
    
    def _indicates_legitimate_context(self, text: str) -> bool:
        """
        Check if text indicates legitimate discussion context
        
        Args:
            text: Text content to analyze
            
        Returns:
            True if legitimate context is indicated, False otherwise
        """
        text_lower = text.lower()
        
        for pattern in self.legitimate_context_patterns:
            if re.search(pattern, text_lower):
                return True
                
        return False
    
    def _analyze_post_content(self, text: str) -> bool:
        """
        Analyze post text content to determine if it should be labeled
        
        Args:
            text: Text content to analyze
            
        Returns:
            True if post should be labeled, False otherwise
        """
        # Skip very short posts as they're unlikely to contain enough context
        if len(text.split()) < 3:
            return False
            
        # Check for sexual terminology
        contains_sexual_terms = self._contains_sexual_terms(text)
        
        # If no sexual terms, no need to label
        if not contains_sexual_terms:
            return False
        
        # IMPORTANT: For artistic nude content with hashtags, we consider it sexual content
        # This is based on the nature of the posts we're analyzing
        if self._check_for_hashtags(text):
            return True
            
        # Check if the post appears to be solicitation
        is_solicitation = self._indicates_solicitation(text)
        
        # Check if the post appears to be legitimate discussion
        is_legitimate = self._indicates_legitimate_context(text)
        
        # Label if sexual + solicitation and not legitimate context
        if contains_sexual_terms and is_solicitation and not is_legitimate:
            return True
            
        # Higher threshold for labeling without solicitation patterns
        return contains_sexual_terms and not is_legitimate and self._explicit_intensity(text) > 2
    
    def _explicit_intensity(self, text: str) -> int:
        """
        Measure the intensity/explicitness of sexual content
        
        Args:
            text: Text content to analyze
            
        Returns:
            Integer score of explicitness (0-5)
        """
        # This is a simplified scoring mechanism
        # In a real implementation, this would use more sophisticated NLP techniques
        
        score = 0
        text_lower = text.lower()
        
        # Count occurrences of sexual terms
        term_count = sum(1 for term in self.primary_terms 
                         if re.search(r'\b' + re.escape(term) + r'\b', text_lower))
        
        if term_count > 5:
            score += 2
        elif term_count > 2:
            score += 1
        
        # Count sexual hashtags
        hashtags = [word[1:].lower() for word in text.split() if word.startswith('#')]
        sexual_hashtags = sum(1 for tag in hashtags if any(term in tag for term in self.primary_terms))
        
        if sexual_hashtags > 3:
            score += 2
        elif sexual_hashtags > 0:
            score += 1
            
        # Check for patterns indicating more explicit content
        explicit_indicators = [
            r'\b(?:sex|sexual|sexually)\b',
            r'\b(?:nsfw|18\+|xxx)\b',
            r'(?:🔞|🍑|🍆|💦)'  # Emojis often used to indicate sexual content
        ]
        
        for pattern in explicit_indicators:
            if re.search(pattern, text_lower):
                score += 1
                
        return min(score, 5)  # Cap at 5
    
    def _extract_image_urls(self, post):
        """
        Extract image URLs from a post
        
        Args:
            post: Bluesky post object
            
        Returns:
            List of image URLs found in the post
        """
        image_urls = []
        
        # Check if post has embedded images
        if hasattr(post, 'embed') and post.embed:
            # Handle different embed types
            if hasattr(post.embed, 'images'):
                for img in post.embed.images:
                    if hasattr(img, 'fullsize'):
                        image_urls.append(img.fullsize)
            elif hasattr(post.embed, 'media') and hasattr(post.embed.media, 'images'):
                for img in post.embed.media.images:
                    if hasattr(img, 'fullsize'):
                        image_urls.append(img.fullsize)
                        
        return image_urls
    
    def _analyze_image(self, image_url: str) -> bool:
        """
        Analyze an image to determine if it contains inappropriate content
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            True if the image is flagged as inappropriate, False otherwise
        """
        try:
            # Download the image
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                print(f"Failed to download image: {image_url}")
                return False
                
            # Process the image
            img = Image.open(BytesIO(response.content))
            
            # Compute perceptual hash
            img_hash = self.image_hasher.compute(img)
            
            # Compare with known NSFW image hashes
            for known_hash in self.known_nsfw_hashes:
                # Check if the hash is close enough to a known NSFW hash
                if self.image_hasher.compare(img_hash, known_hash) < self.image_hash_threshold:
                    return True
            
            # Additional image analysis could be added here
            # For example, skin tone detection, pose detection, etc.
            
            return False
            
        except Exception as e:
            print(f"Error analyzing image {image_url}: {e}")
            return False
    
    def _analyze_post_images(self, post) -> bool:
        """
        Analyze all images in a post to determine if any contain inappropriate content
        
        Args:
            post: Bluesky post object
            
        Returns:
            True if any image is flagged as inappropriate, False otherwise
        """
        # Extract image URLs from the post
        image_urls = self._extract_image_urls(post)
        
        # If no images, no need to label based on images
        if not image_urls:
            return False
            
        # Analyze each image
        for image_url in image_urls:
            if self._analyze_image(image_url):
                return True
                
        return False
    
    def moderate_post(self, url: str) -> Optional[str]:
        """
        Apply moderation to the post specified by the given URL
        
        Args:
            url: URL to the Bluesky post
            
        Returns:
            Label to apply, or None if no label should be applied
        """
        try:
            # Fetch the post content
            post = post_from_url(self.client, url)
            
            if not post or not hasattr(post, 'value'):
                print(f"Warning: Could not retrieve post {url}")
                return None
                
            # Check text content if available
            if hasattr(post.value, 'text'):
                post_text = post.value.text
                if self._analyze_post_content(post_text):
                    return SEXUAL_CONTENT_LABEL
            
            # Check image content if available
            if self._analyze_post_images(post.value):
                return SEXUAL_CONTENT_LABEL
                
            return None
                
        except Exception as e:
            print(f"Error moderating post {url}: {e}")
            return None
    
    def test_labeler(self, test_posts: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Test the labeler on a list of posts
        
        Args:
            test_posts: List of dictionaries with 'url' and 'expected_label' keys
            
        Returns:
            Dictionary with test results and metrics
        """
        results = {}
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        true_negatives = 0
        
        # Track processing times
        processing_times = []
        
        for post in test_posts:
            url = post['url']
            expected_label = post.get('expected_label')
            
            # Time the processing
            start_time = time.time()
            actual_label = self.moderate_post(url)
            end_time = time.time()
            processing_times.append(end_time - start_time)
            
            # Determine if this was a success
            success = (actual_label == expected_label) or \
                    (actual_label is None and expected_label is None)
                    
            results[url] = success
            
            # Update confusion matrix
            if expected_label and actual_label == expected_label:
                true_positives += 1
            elif expected_label and actual_label != expected_label:
                false_negatives += 1
            elif not expected_label and actual_label:
                false_positives += 1
            else:
                true_negatives += 1
            
            if not success:
                print(f"Test failed for {url}: expected {expected_label}, got {actual_label}")
        
        # Calculate metrics
        total = len(results)
        accuracy = sum(1 for success in results.values() if success) / total if total > 0 else 0
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # Calculate processing time statistics
        avg_time = np.mean(processing_times) if processing_times else 0
        max_time = np.max(processing_times) if processing_times else 0
        min_time = np.min(processing_times) if processing_times else 0
        std_time = np.std(processing_times) if processing_times else 0
        
        # Prepare the final metrics dictionary
        metrics = {
            "results": results,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "confusion_matrix": {
                "true_positives": true_positives,
                "false_positives": false_positives,
                "false_negatives": false_negatives,
                "true_negatives": true_negatives
            },
            "performance": {
                "avg_processing_time": avg_time,
                "max_processing_time": max_time,
                "min_processing_time": min_time,
                "std_processing_time": std_time
            }
        }
        
        return metrics