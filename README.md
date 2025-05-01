# Sexual Content Labeler for Bluesky

This labeler implements a comprehensive solution for detecting sexual content on Bluesky. It employs a multi-layered analysis approach, examining both text content and images to identify potentially sexual material while maintaining high precision.

## Implementation Approach

The labeler uses a combination of sophisticated techniques to identify sexual content:

### Text Analysis
1. **Sexual Terminology Detection**: Identifies posts containing explicit sexual terminology using a hierarchical dictionary of terms derived from analysis of 50 Bluesky posts.
2. **Context Analysis**: Distinguishes between legitimate discussions (educational, artistic) and explicitly sexual communication using pattern recognition.
3. **Solicitation Pattern Recognition**: Detects language patterns associated with solicitation or unwanted sexual advances.
4. **Explicit Intensity Scoring**: Evaluates content on a 0-5 scale based on term frequency, hashtag patterns, and emoji usage.
5. **Hashtag Analysis**: Special detection for posts containing primarily sexual hashtags like #nude, #artnude, etc.

### Image Analysis
1. **Perceptual Hashing**: Compares images against a database of known inappropriate content using perceptual hash similarity.
2. **Image Extraction**: Automatically extracts embedded images from posts for analysis.
3. **Content Sensitivity**: Implements thresholds to reduce false positives while catching problematic content.

## Key Features

- Multi-modal analysis of both text and image content
- Pattern matching for solicitation indicators and legitimate contexts
- Emoji pattern recognition for implicit sexual content
- Perfect precision (no false positives) with high recall
- Efficient processing (average 0.27 seconds per post)
- Thoroughly tested across 100 diverse posts

## Setup and Usage

1. Ensure your `.env` file is correctly set up with your Bluesky credentials:
   ```
   USERNAME=your-handle.bsky.social
   PW=your-app-password
   ```

2. Required dependencies:
   ```
   pip install atproto dotenv requests perception pillow pandas numpy
   ```

3. Place configuration files in your labeler inputs directory:
   - `sexual_terms.json`: List of terms related to sexual content
   - `nsfw_image_hashes.json`: Database of perceptual hashes of known inappropriate images

4. Part 1 (Automated Labeler for Trust & Safety, Citation, and Dog Detection):
   ```
   python test_labeler.py labeler-inputs test-data/input-posts-t-and-s.csv
   python test_labeler.py labeler-inputs test-data/input-posts-cite.csv
   python test_labeler.py labeler-inputs test-data/input-posts-dogs.csv
   ```

5. Part 2 (Sexual Content Labeler Testing):
   ```
   # Run each batch separately to manage API rate limits
   python test_policy_labeler.py labeler-inputs test_posts_batch1.json --output_file test_results_batch1.json
   python test_policy_labeler.py labeler-inputs test_posts_batch2.json --output_file test_results_batch2.json
   python test_policy_labeler.py labeler-inputs test_posts_batch3.json --output_file test_results_batch3.json
   python test_policy_labeler.py labeler-inputs test_posts_batch4.json --output_file test_results_batch4.json
   
   # Combine results from all batches
   python combine_all_results.py
   ```

6. Emit actual labels to Bluesky (use with caution):
   ```
   python test_policy_labeler.py labeler-inputs test_posts.json --emit_labels
   ```

## Comprehensive Testing Approach

Our labeler underwent rigorous testing with 100 diverse posts, split into 4 batches of 25 each:

- **Balanced Dataset**: 60 posts containing sexual content and 40 regular posts without sexual content
- **Batch Processing**: Testing in batches to manage API rate limits and enable incremental improvements
- **Performance Metrics**: Tracking accuracy, precision, recall, F1 score, and processing time
- **Extensive Analysis**: Creating confusion matrices to identify strengths and weaknesses

### Testing Results

| Metric | Overall (100 posts) |
|--------|---------------------|
| Accuracy | 94.0% |
| Precision | 100.0% |
| Recall | 90.0% |
| F1 Score | 94.7% |
| True Positives | 54 |
| False Positives | 0 |
| False Negatives | 6 |
| True Negatives | 40 |
| Avg. Processing Time | 0.273 sec/post |

## Ethical Considerations

This labeler aims to detect sexual content while respecting creator expression and user choice:

- **Content Detection vs. Censorship**: The system focuses on detection rather than automatically removing content
- **Context Sensitivity**: Special handling for educational, medical, or artistic sexual content
- **Perfect Precision**: Prioritizing the avoidance of false positives that could unfairly restrict legitimate content
- **Privacy Protections**: Minimal data retention and no user profiling
- **Transparency**: Clear labeling criteria and potential for contestability

## Future Improvements

1. Enhanced image analysis using advanced computer vision models
2. Better euphemism detection using more sophisticated NLP techniques
3. User feedback loop for continuous improvement
4. Cross-linguistic detection for multiple languages
5. Confidence scoring for borderline cases
6. Explainability features to clarify labeling decisions

## Team Members

- Gloria Hu
- Robert Jones
- Hycent Ajah
- Yibei Li