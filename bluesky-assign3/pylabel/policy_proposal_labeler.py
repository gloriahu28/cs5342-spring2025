"""Implementation of policy proposal labeler for unwanted sexual content

This labeler aims to detect and label posts containing potentially unwanted sexual 
communication, focusing specifically on unsolicited sexually explicit text. It 
implements a moderation approach as outlined in Assignment 2, applying natural
language processing techniques to identify inappropriate content patterns.

The labeler attaches a "sexual-content" label to posts that match detection criteria.
"""

from typing import List, Optional, Dict, Set
import re
import os
import json
from atproto import Client

from .label import post_from_url

# Define the label we'll use
SEXUAL_CONTENT_LABEL = "sexual-content"

class PolicyProposalLabeler:
    """
    Labeler implementation for unwanted sexual content
    This focuses on detecting sexually explicit text communication that may be unwanted
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
        
        # Load dictionaries of sexual terms and phrases
        self._load_dictionaries()
        
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
            "intimate", "obscene", "lewd", "indecent"
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
        Analyze post content to determine if it should be labeled
        
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
            
            if not post or not hasattr(post, 'value') or not hasattr(post.value, 'text'):
                print(f"Warning: Could not retrieve text from post {url}")
                return None
                
            post_text = post.value.text
            
            # Analyze the post content to determine if it should be labeled
            if self._analyze_post_content(post_text):
                return SEXUAL_CONTENT_LABEL
                
            return None
                
        except Exception as e:
            print(f"Error moderating post {url}: {e}")
            return None
    
    def test_labeler(self, test_posts: List[Dict[str, str]]) -> Dict[str, bool]:
        """
        Test the labeler on a list of posts
        
        Args:
            test_posts: List of dictionaries with 'url' and 'expected_label' keys
            
        Returns:
            Dictionary mapping post URLs to success status
        """
        results = {}
        
        for post in test_posts:
            url = post['url']
            expected_label = post.get('expected_label')
            
            actual_label = self.moderate_post(url)
            
            # Compare actual with expected
            success = (actual_label == expected_label) or \
                      (actual_label is None and expected_label is None)
                      
            results[url] = success
            
            if not success:
                print(f"Test failed for {url}: expected {expected_label}, got {actual_label}")
        
        return results