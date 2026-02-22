"""Configuration management for the PDF summarizer."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # Gemini API configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL", "gemini-1.5-flash"
    )  # Default to flash for speed

    # OCR configuration
    OCR_DPI = 300
    OCR_LANG = "eng"

    # Processing configuration
    PAGES_PER_GROUP = 20
    DEFAULT_OVERLAP = 2

    # Input/Output configuration
    DEFAULT_INPUT_DIR = "./input"
    DEFAULT_OUTPUT_DIR = "./output"
    SUMMARIES_SUBDIR = "summaries"
    OCR_TEXT_SUBDIR = "ocr_text"  # Folder for OCR extracted text files
    RAW_SUMMARIES_SUBDIR = "raw_summaries"  # Folder for individual API responses

    @classmethod
    def validate(cls):
        """
        Validate configuration settings.

        Raises:
            ValueError: If required configuration is missing or invalid
        """
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Please set it in .env file or as environment variable.\n"
                "Example: export GEMINI_API_KEY=your_key_here"
            )

        if cls.OCR_DPI < 72 or cls.OCR_DPI > 600:
            raise ValueError(
                f"Invalid OCR_DPI value: {cls.OCR_DPI}. Must be between 72 and 600."
            )

        if cls.PAGES_PER_GROUP < 1:
            raise ValueError(
                f"Invalid PAGES_PER_GROUP value: {cls.PAGES_PER_GROUP}. "
                "Must be at least 1."
            )

        if cls.DEFAULT_OVERLAP < 0 or cls.DEFAULT_OVERLAP >= cls.PAGES_PER_GROUP:
            raise ValueError(
                f"Invalid DEFAULT_OVERLAP value: {cls.DEFAULT_OVERLAP}. "
                f"Must be between 0 and {cls.PAGES_PER_GROUP - 1}."
            )
