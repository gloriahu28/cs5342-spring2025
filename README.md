# Unwanted Sexual Content Labeler

This labeler implements our policy proposal from Assignment 2 to detect unwanted sexual content on Bluesky. It employs a dual-analysis approach, examining both text content and images to identify potentially unwanted sexually explicit material.

## Implementation Approach

The labeler uses a combination of techniques to identify unwanted sexual content:

### Text Analysis
1. **Keyword Detection**: Identifies posts containing explicit sexual terminology using a configurable dictionary of terms.
2. **Context Analysis**: Distinguishes between legitimate discussions about sexual topics and potentially unwanted/inappropriate communication.
3. **Solicitation Pattern Recognition**: Detects language patterns associated with solicitation or unwanted sexual advances.
4. **Intensity Scoring**: Evaluates the explicitness level of content based on term frequency and context.

### Image Analysis
1. **Perceptual Hashing**: Compares images against a database of known inappropriate content using perceptual hash similarity.
2. **Image Extraction**: Automatically extracts embedded images from posts for analysis.
3. **Content Sensitivity**: Implements thresholds to reduce false positives while catching genuinely problematic content.

## Key Features

- Dual-modality analysis of both text and image content
- Pattern matching for solicitation indicators
- Context sensitivity to reduce false positives
- Configurable through external term lists and image hash databases
- Comprehensive reporting of moderation decisions

## Setup and Usage

1. Ensure your `.env` file is correctly set up with your Bluesky credentials:
   ```
   USERNAME=your-handle.bsky.social
   PW=your-app-password
   ```

2. Required dependencies:
if your device is macOS, use python 3.9
   ```
   pip install atproto dotenv requests perception pillow pandas opencv-python
   ```

3. Place configuration files in your labeler inputs directory:
   - `sexual_terms.json`: List of terms related to sexual content
   - `nsfw_image_hashes.json`: (Optional) Database of perceptual hashes of known inappropriate images

4. Run automated_labeler.py (Part1 - Milestone 2,3,4):
   ```
   python test_labeler.py labeler-inputs test-data/input-posts-t-and-s.csv && \
   python test_labeler.py labeler-inputs test-data/input-posts-cite.csv && \
   python test_labeler.py labeler-inputs test-data/input-posts-dogs.csv
   ```

5. Run policy_proposal_labeler.py with test data (Part2):
   ```
   python test_policy_labeler.py labeler-inputs test_posts.json
   ```

6. Run policy_proposal_labeler.py, To emit actual labels to Bluesky (use with caution):
   ```
   python test_policy_labeler.py labeler-inputs test_posts.json --emit_labels
   ```

## Testing Approach

The labeler includes a built-in testing framework that:

1. Loads test cases from a JSON file
2. Runs the labeler on each test case, analyzing both text and images
3. Compares the actual label with the expected label
4. Reports accuracy statistics

## Ethical Considerations

This labeler aims to help make Bluesky safer by identifying potentially unwanted sexual content. However, we acknowledge that:

- Context matters: Sexual discussions in educational, medical, or policy contexts should not be censored.
- False positives can occur: The system may incorrectly flag legitimate content.
- Cultural differences exist: Sensitivity around sexual content varies across cultures.
- Privacy concerns: Image analysis is conducted with respect for user privacy.

The labeler is designed to be a tool that helps moderators, not a definitive arbiter of what content is acceptable.

## Future Improvements

1. Incorporate more sophisticated NLP techniques for better context understanding
2. Enhance image analysis with AI-based nudity detection models
3. Implement feedback mechanisms to improve accuracy over time
4. Add user-specific preferences for moderation sensitivity

## Team Members

- Gloria Hu
- Robert Jones
- Hycent Ajah
- Yibei Li