"""Implementation of automated moderator"""

from perception.hashers import PHash
from .label import post_from_url
from atproto import Client
from typing import List
from io import BytesIO
from PIL import Image
import pandas as pd
import requests
import os
import re


T_AND_S_LABEL = "t-and-s"
DOG_LABEL = "dog"  
THRESH = 0.3       

# === Utility Function ===
def check_keyword(keyword, post):
    """
    Check if the keyword is present in the post text using case-insensitive whole-word matching.
    """
    pattern = re.compile(r'\b' + keyword + r'\b', re.IGNORECASE)
    found = pattern.search(post)
    return found is not None


class AutomatedLabeler:
    """
    Automated labeler implementation.

    Milestone 2: Label posts with T&S words and domains.
    Milestone 3: Cite sources based on news domains.
    Milestone 4: Detect and label posts containing dog images based on perceptual hash matching.
    """

    def __init__(self, client: Client, input_dir):
        self.client = client

        # === Milestone 2: Load T&S Keywords ===
        # Load trusted-and-safety related words and domains from CSV files
        ts_domain_path = os.path.join(input_dir, 't-and-s-domains.csv')
        ts_word_path = os.path.join(input_dir, 't-and-s-words.csv')

        domains = pd.read_csv(ts_domain_path)['Domain'].tolist()
        words = pd.read_csv(ts_word_path)['Word'].tolist()

        # Combine both into a single list for matching
        self.ts_keywords = domains + words 


        # === Milestone 3: Load News Domain Sources ===
        # Load list of [Domain, Source] pairs from news-domains.csv
        news_domain = os.path.join(input_dir, 'news-domains.csv')
        self.news_source = pd.read_csv(news_domain).values.tolist()


        # === Milestone 4: Load dog perceptual hashes using perception ===
        self.hasher = PHash()
        self.dog_hashes = []
        dog_img_dir = os.path.join(input_dir, "dog-list-images")
        if os.path.exists(dog_img_dir):
            for filename in os.listdir(dog_img_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(dog_img_dir, filename)
                    try:
                        dog_hash = self.hasher.compute(image_path)
                        self.dog_hashes.append(dog_hash)
                    except Exception as e:
                        print(f"Error hashing {filename}: {e}")

    
    """
    Extract image URLs from a post.
    """
    def _extract_image_urls(self, post) -> List[str]:
        image_urls = []
        
        if hasattr(post, 'value') and hasattr(post.value, 'embed'):
            embed = post.value.embed
            if hasattr(embed, 'images'):
                for image in embed.images:
                    if hasattr(image, 'image') and hasattr(image.image, 'ref'):
                        did = post.uri.split('/')[2]
                        img_cid = image.image.ref.link
                    
                    # Try feed_fullsize first
                    full_url = f"https://cdn.bsky.app/img/feed_fullsize/plain/{did}/{img_cid}@jpeg"
                    try:
                        response = requests.head(full_url, timeout=3)
                        if response.status_code == 200:
                            image_urls.append(full_url)
                            continue
                    except requests.RequestException:
                        pass

                    # Fallback to feed_thumbnail
                    thumb_url = f"https://cdn.bsky.app/img/feed_thumbnail/plain/{did}/{img_cid}@jpeg"
                    image_urls.append(thumb_url)

        return image_urls

    """
    Determine whether an image matches any dog reference image.
    """
    def _is_dog_image(self, image_url: str) -> bool:
        
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                return False
            image = Image.open(BytesIO(response.content))
            image_hash = self.hasher.compute(image)
            return any(self.hasher.compute_distance(image_hash, dog_hash) <= THRESH for dog_hash in self.dog_hashes)
        except Exception as e:
            print(f"Failed to process image {image_url}: {e}")
            return False



    def moderate_post(self, url: str) -> List[str]:
        """
        Apply moderation to the post specified by the given URL.

        Milestone 2: Label post with 't-and-s' if it contains any T&S keywords.
        Milestone 3: Add label corresponding to the source if a news keyword is found.
        Milestone 4: Add label 'dog' if any attached image is perceptually similar to a known dog image.
        """
        labels = set()

        # Fetch post content using the provided client
        post = post_from_url(self.client, url)
        post_text = post.value.text

        # === Milestone 2: T&S keyword matching ===
        for keyword in self.ts_keywords:
            if check_keyword(keyword, post_text):
                labels.add(T_AND_S_LABEL)

        # === Milestone 3: News source keyword matching ===
        for keyword, source in self.news_source:
            if check_keyword(keyword, post_text):
                labels.add(source)

        # === Milestone 4: Dog image detection ===
        image_urls = self._extract_image_urls(post)
        for image_url in image_urls:
            if self._is_dog_image(image_url):
                labels.add(DOG_LABEL)
                break

        return list(labels) if labels else []