# Unwanted Sexual Content Labeler

This labeler implements part of our policy proposal from Assignment 2 to detect unwanted sexual content on Bluesky. It focuses specifically on identifying potentially unwanted sexually explicit communication in text posts.

## Implementation Approach

The labeler uses a combination of techniques to identify unwanted sexual content:

1. **Keyword Detection**: Identifies posts containing explicit sexual terminology.
2. **Context Analysis**: Distinguishes between legitimate discussions about sexual topics and potentially unwanted/inappropriate communication.
3. **Solicitation Pattern Recognition**: Detects language patterns associated with solicitation or unwanted sexual advances.

## Key Features

- Text-based analysis of post content
- Pattern matching for solicitation indicators
- Context sensitivity to reduce false positives
- Configurable through external term lists

## Setup and Usage

1. Ensure your `.env` file is correctly set up with your Bluesky credentials:

2. Place `sexual_terms.json` in your labeler inputs directory.

3. Run the labeler with test data:

4. To emit actual labels to Bluesky (use with caution):

## Testing Approach

The labeler includes a built-in testing function that:

1. Loads test cases from a JSON file
2. Runs the labeler on each test case
3. Compares the actual label with the expected label
4. Reports accuracy statistics

## Ethical Considerations

This labeler aims to help make Bluesky safer by identifying potentially unwanted sexual content. However, we acknowledge that:

- Context matters: Sexual discussions in educational, medical, or policy contexts should not be censored.
- False positives can occur: The system may incorrectly flag legitimate content.
- Cultural differences exist: Sensitivity around sexual content varies across cultures.

The labeler is designed to be a tool that helps moderators, not a definitive arbiter of what content is acceptable.

## Future Improvements

1. Incorporate more sophisticated NLP techniques for better context understanding
2. Add language/cultural adaptations for international application
3. Implement feedback mechanisms to improve accuracy over time
4. Add support for image analysis using computer vision models

## Team Members

- Gloria Hu
- Robert Jones
- Hycent Ajah
- Yibei Li