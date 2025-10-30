"""
Configuration settings for LLM processing
"""

# LLM Output Settings
LLM_OUTPUT_SETTINGS = {
    "default_max_tokens": 5000,  # Increased to use most of 8192 context (leaves ~3000 for prompt)
    "short_article_max_tokens": 3000,  # Increased for short articles
    "long_article_max_tokens": 6000,  # Increased to use most of 8192 context (leaves ~2000 for prompt)
    "min_tokens": 500,  # Minimum words for output
}

# LLM Model Settings
LLM_MODEL_SETTINGS = {
    "model_name": "aya-expanse:8b",
    "temperature": 0.9,  # Creativity level (0.0 = deterministic, 1.0 = very creative)
    "top_p": 0.9,  # Nucleus sampling parameter
}

# Content Settings
CONTENT_SETTINGS = {
    "include_metadata": True,  # Whether to include metadata in processing
    "avoid_repetition": True,  # Whether to avoid repetition from previous articles
    "professional_tone": True,  # Whether to use professional tone
}

# Feedback Processing Settings
FEEDBACK_SETTINGS = {
    "enable_thinking_prompt": True,  # Whether to include thinking prompt
    "enable_quality_check": True,  # Whether to apply quality check
    "feedback_file_path": "feedback_clean.json",  # Path to feedback rules
    "auto_correct": False,  # Whether to automatically correct issues
    "manual_review": True,  # Whether to require manual review
}

def get_max_tokens(article_type="default"):
    """Get maximum tokens based on article type"""
    if article_type == "short":
        return LLM_OUTPUT_SETTINGS["short_article_max_tokens"]
    elif article_type == "long":
        return LLM_OUTPUT_SETTINGS["long_article_max_tokens"]
    else:
        return LLM_OUTPUT_SETTINGS["default_max_tokens"] 