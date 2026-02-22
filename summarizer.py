"""Summarization module using Google Gemini API."""
import logging
import time
from typing import List, Dict, Optional
import sys

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "google-generativeai package not found. "
        "Please install it: pip install google-generativeai"
    )

from config import Config
from utils import sanitize_filename, ensure_directory
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class Summarizer:
    """Handles summarization using Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None, raw_summaries_dir: Optional[str] = None):
        """
        Initialize summarizer.
        
        Args:
            api_key: Gemini API key (default: from Config)
            raw_summaries_dir: Directory to save individual API responses (optional)
        """
        self.api_key = api_key or Config.GEMINI_API_KEY
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. "
                "Set GEMINI_API_KEY environment variable or pass it to Summarizer."
            )
        
        # Configure the API
        logger.info("Configuring Gemini API...")
        genai.configure(api_key=self.api_key)
        
        # Set up raw summaries output directory
        self.raw_summaries_dir = Path(raw_summaries_dir) if raw_summaries_dir else None
        if self.raw_summaries_dir:
            ensure_directory(str(self.raw_summaries_dir))
            logger.info(f"Raw summaries will be saved to: {self.raw_summaries_dir}")
        
        # Determine which model to use
        model_name = getattr(Config, 'GEMINI_MODEL', 'gemini-1.5-flash')
        self.model = None
        
        # List of models to try in order of preference (fastest to most capable)
        model_options = [
            model_name,  # User specified or default
            'gemini-1.5-flash',  # Fast and efficient (recommended)
            'gemini-1.5-pro',    # More capable but slower
            'gemini-pro',        # Legacy model (may not be available)
        ]
        
        # Remove duplicates while preserving order
        model_options = list(dict.fromkeys(model_options))
        
        # First, try to get list of available models
        available_model_names = []
        try:
            available_models = genai.list_models()
            available_model_names = [
                m.name.split('/')[-1] for m in available_models
                if 'generateContent' in m.supported_generation_methods
            ]
            if available_model_names:
                logger.info(f"Available Gemini models: {', '.join(available_model_names)}")
        except Exception as e:
            logger.warning(f"Could not list available models: {e}. Will try default models.")
        
        # Try each model option
        for model_option in model_options:
            # Skip if we know it's not available
            if available_model_names and model_option not in available_model_names:
                logger.debug(f"Skipping {model_option} (not in available models)")
                continue
                
            try:
                logger.info(f"Initializing Gemini model: {model_option}")
                self.model = genai.GenerativeModel(model_option)
                logger.info(f"✓ Successfully initialized model: {model_option}")
                break
            except Exception as e:
                logger.debug(f"Failed to initialize {model_option}: {e}")
                continue
        
        # If still no model, try first available one
        if self.model is None and available_model_names:
            try:
                first_available = available_model_names[0]
                logger.warning(f"No preferred model worked. Trying first available: {first_available}")
                self.model = genai.GenerativeModel(first_available)
                logger.info(f"✓ Successfully initialized model: {first_available}")
            except Exception as e:
                error_msg = (
                    f"Failed to initialize any Gemini model. "
                    f"Available models: {available_model_names}. Error: {e}"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg) from e
        
        if self.model is None:
            error_msg = (
                f"Failed to initialize any Gemini model. "
                f"Tried: {model_options}. Please check your API key and try again."
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    
    def summarize_text(self, text: str, page_range: Optional[tuple] = None) -> str:
        """
        Create a simplified learning guide from the given text using Gemini API.
        
        Args:
            text: Text to process
            page_range: Optional tuple (start_page, end_page) for context
        
        Returns:
            Simplified learning guide
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for processing")
            return ""
        
        # Construct the prompt
        page_context = ""
        if page_range:
            start, end = page_range
            page_context = f" (Pages {start}-{end})"
        
        prompt = f"""Transform the following text{page_context} into a simplified, easy-to-read learning guide that I can study from instead of reading the original verbose text.

INSTRUCTIONS:
- Remove all unnecessary verbosity, filler words, and repetitive explanations
- Extract only the essential information needed for learning
- Organize content in a clear, logical structure
- Use concise bullet points, lists, or short paragraphs
- Focus on key concepts, definitions, important facts, and practical information
- Make it readable and study-friendly - something I can actually use to learn
- Keep technical terms but explain them briefly when first introduced
- Remove redundant explanations and "yapping" - get straight to the point

Format the output as a learning guide with clear sections and structure. Make it something I can read INSTEAD of the original text.

Original text:
{text}

Learning Guide:"""
        
        try:
            logger.info(f"→ Sending API request to Gemini... (text length: {len(text)} chars)")
            start_time = time.time()
            response = self.model.generate_content(prompt)
            elapsed_time = time.time() - start_time
            
            if not response or not hasattr(response, 'text'):
                raise ValueError("Invalid response from Gemini API: missing text attribute")
            
            learning_guide = response.text.strip()
            
            if not learning_guide:
                raise ValueError("Empty learning guide received from Gemini API")
            
            logger.info(f"✓ Learning guide generated in {elapsed_time:.2f}s: {len(learning_guide)} characters")
            logger.debug(f"Preview: {learning_guide[:200]}...")
            return learning_guide
        
        except ValueError as e:
            logger.error(f"Value error during summarization: {e}")
            raise
        except Exception as e:
            error_msg = str(e).lower()
            
            # Check for rate limiting or quota errors
            if "quota" in error_msg or "rate limit" in error_msg or "429" in error_msg:
                logger.warning(f"Rate limit/quota error: {e}. Waiting before retry...")
                time.sleep(5)
                try:
                    response = self.model.generate_content(prompt)
                    if response and hasattr(response, 'text'):
                        summary = response.text.strip()
                        if summary:
                            logger.info("Summary generated successfully on retry after rate limit")
                            return summary
                except Exception as retry_error:
                    logger.error(f"Retry after rate limit failed: {retry_error}")
                    raise RuntimeError(
                        f"API rate limit exceeded. Please wait before trying again. "
                        f"Original error: {e}"
                    ) from retry_error
            
            logger.error(f"Error during summarization: {e}")
            # Retry once after a short delay for other errors
            try:
                time.sleep(2)
                response = self.model.generate_content(prompt)
                if response and hasattr(response, 'text'):
                    summary = response.text.strip()
                    if summary:
                        logger.info("Summary generated successfully on retry")
                        return summary
                    else:
                        raise ValueError("Empty summary on retry")
            except Exception as retry_error:
                logger.error(f"Retry failed: {retry_error}")
                raise RuntimeError(
                    f"Failed to generate summary after retry. "
                    f"Original error: {e}, Retry error: {retry_error}"
                ) from retry_error
    
    def summarize_page_group(
        self,
        text: str,
        start_page: int,
        end_page: int,
        pdf_name: str = None,
        max_retries: int = 3,
        retry_delay: int = 2
    ) -> str:
        """
        Create a simplified learning guide for a group of pages.
        
        Args:
            text: Combined text from the page group
            start_page: Starting page number
            end_page: Ending page number
            pdf_name: Name of the PDF file (for saving raw summaries)
            max_retries: Maximum number of retry attempts
            retry_delay: Delay in seconds between retries
        
        Returns:
            Learning guide for the page group
        """
        page_range = (start_page, end_page)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"  Attempt {attempt + 1}/{max_retries} for pages {start_page}-{end_page}...")
                learning_guide = self.summarize_text(text, page_range)
                
                # Save raw learning guide immediately
                if self.raw_summaries_dir and pdf_name:
                    self._save_raw_summary(pdf_name, start_page, end_page, learning_guide, text)
                
                return learning_guide
            
            except KeyboardInterrupt:
                logger.warning("Summarization interrupted by user")
                raise
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    error_type = type(e).__name__
                    logger.warning(
                        f"Summarization attempt {attempt + 1}/{max_retries} failed "
                        f"({error_type}). Retrying in {wait_time} seconds... "
                        f"Error: {str(e)[:100]}"
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(
                        f"All {max_retries} summarization attempts failed for "
                        f"pages {start_page}-{end_page}. Last error: {e}"
                    )
                    raise RuntimeError(
                        f"Failed to summarize pages {start_page}-{end_page} after "
                        f"{max_retries} attempts: {e}"
                    ) from e
        
        return ""
    
    def _find_existing_raw_summary(self, pdf_name: str, start_page: int, end_page: int) -> Optional[Path]:
        """
        Check if a raw summary file already exists for the given page range.
        
        Args:
            pdf_name: Name of the PDF file
            start_page: Starting page number
            end_page: Ending page number
        
        Returns:
            Path to existing file if found, None otherwise
        """
        if not self.raw_summaries_dir:
            return None
        
        safe_pdf_name = sanitize_filename(pdf_name)
        # Look for files matching the pattern (timestamp may vary)
        pattern = f"{safe_pdf_name}_pages_{start_page:04d}-{end_page:04d}_*.txt"
        
        matching_files = list(self.raw_summaries_dir.glob(pattern))
        
        if matching_files:
            # Return the most recent file if multiple exist
            return max(matching_files, key=lambda p: p.stat().st_mtime)
        
        return None
    
    def _load_existing_raw_summary(self, file_path: Path) -> str:
        """
        Load learning guide from an existing raw summary file.
        
        Args:
            file_path: Path to the raw summary file
        
        Returns:
            Extracted learning guide text
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract learning guide section
            # Look for the LEARNING GUIDE section between the markers
            start_marker = "=" * 80 + "\nLEARNING GUIDE\n" + "=" * 80
            end_marker = "\n" + "=" * 80 + "\nORIGINAL TEXT"
            
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker)
            
            if start_idx != -1 and end_idx != -1:
                learning_guide = content[start_idx + len(start_marker):end_idx].strip()
                return learning_guide
            else:
                # Fallback: try to find content after "LEARNING GUIDE" header
                # Some files might have different formatting
                lines = content.split('\n')
                in_guide = False
                guide_lines = []
                
                for line in lines:
                    if "LEARNING GUIDE" in line and "=" * 80 in content[content.find(line):content.find(line)+100]:
                        in_guide = True
                        continue
                    if in_guide:
                        if "=" * 80 in line and "ORIGINAL TEXT" in content[content.find(line):content.find(line)+100]:
                            break
                        guide_lines.append(line)
                
                if guide_lines:
                    return '\n'.join(guide_lines).strip()
                
                logger.warning(f"Could not parse existing file format, using full content")
                return content
                
        except Exception as e:
            logger.error(f"Error loading existing summary from {file_path}: {e}")
            raise
    
    def _find_existing_raw_summary(self, pdf_name: str, start_page: int, end_page: int) -> Optional[Path]:
        """
        Check if a raw summary file already exists for the given page range.
        
        Args:
            pdf_name: Name of the PDF file
            start_page: Starting page number
            end_page: Ending page number
        
        Returns:
            Path to existing file if found, None otherwise
        """
        if not self.raw_summaries_dir:
            return None
        
        safe_pdf_name = sanitize_filename(pdf_name)
        # Look for files matching the pattern (timestamp may vary)
        pattern = f"{safe_pdf_name}_pages_{start_page:04d}-{end_page:04d}_*.txt"
        
        matching_files = list(self.raw_summaries_dir.glob(pattern))
        
        if matching_files:
            # Return the most recent file if multiple exist
            return max(matching_files, key=lambda p: p.stat().st_mtime)
        
        return None
    
    def _load_existing_raw_summary(self, file_path: Path) -> str:
        """
        Load learning guide from an existing raw summary file.
        
        Args:
            file_path: Path to the raw summary file
        
        Returns:
            Extracted learning guide text
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Look for the LEARNING GUIDE section markers
            # Format: ===...=== \n LEARNING GUIDE \n ===...===
            lines = content.split('\n')
            
            start_idx = None
            end_idx = None
            
            # Find start: line with "LEARNING GUIDE" surrounded by separator lines
            for i, line in enumerate(lines):
                if line.strip() == "LEARNING GUIDE":
                    # Check if previous and next lines are separators
                    if i > 0 and i < len(lines) - 1:
                        prev_line = lines[i-1].strip()
                        next_line = lines[i+1].strip()
                        if prev_line.startswith("=") and next_line.startswith("="):
                            start_idx = i + 2  # Start after the separator
                            break
            
            # Find end: line with "ORIGINAL TEXT"
            if start_idx is not None:
                for i in range(start_idx, len(lines)):
                    if "ORIGINAL TEXT" in lines[i] and i > 0:
                        # Check if previous line is a separator
                        if lines[i-1].strip().startswith("="):
                            end_idx = i - 1  # End before the separator
                            break
            
            if start_idx is not None and end_idx is not None:
                guide_lines = lines[start_idx:end_idx]
                learning_guide = '\n'.join(guide_lines).strip()
                if learning_guide:
                    return learning_guide
            
            # Fallback: try simple pattern matching
            start_marker = "LEARNING GUIDE"
            end_marker = "ORIGINAL TEXT"
            
            start_pos = content.find(start_marker)
            end_pos = content.find(end_marker)
            
            if start_pos != -1 and end_pos != -1 and end_pos > start_pos:
                # Extract text between markers, skipping the marker lines and separators
                snippet = content[start_pos:end_pos]
                lines_snippet = snippet.split('\n')
                # Skip first few lines (marker and separators) and get the content
                guide_lines = []
                skip_lines = 0
                for line in lines_snippet:
                    if skip_lines < 3 or line.strip().startswith("="):
                        skip_lines += 1
                        continue
                    guide_lines.append(line)
                
                if guide_lines:
                    return '\n'.join(guide_lines).strip()
            
            logger.warning(f"Could not parse existing file format cleanly, returning full content")
            return content
                
        except Exception as e:
            logger.error(f"Error loading existing summary from {file_path}: {e}")
            raise
    
    def _save_raw_summary(self, pdf_name: str, start_page: int, end_page: int, 
                          learning_guide: str, original_text: str):
        """
        Save raw learning guide response to a file.
        
        Args:
            pdf_name: Name of the PDF file
            start_page: Starting page number
            end_page: Ending page number
            learning_guide: Generated learning guide
            original_text: Original text that was processed
        """
        if not self.raw_summaries_dir:
            return
        
        try:
            safe_pdf_name = sanitize_filename(pdf_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_pdf_name}_pages_{start_page:04d}-{end_page:04d}_{timestamp}.txt"
            file_path = self.raw_summaries_dir / filename
            
            content = f"""LEARNING GUIDE: Pages {start_page}-{end_page}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
PDF: {pdf_name}

{'='*80}
LEARNING GUIDE
{'='*80}

{learning_guide}

{'='*80}
ORIGINAL TEXT (First 5000 chars)
{'='*80}

{original_text[:5000]}{'...' if len(original_text) > 5000 else ''}
"""
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"  → Saved learning guide to: {file_path.name}")
        except Exception as e:
            logger.warning(f"Failed to save learning guide for pages {start_page}-{end_page}: {e}")
    
    def summarize_multiple_groups(
        self,
        page_groups: Dict[tuple, str],
        pdf_name: str = None,
        delay_between_requests: float = 1.0
    ) -> Dict[tuple, str]:
        """
        Create simplified learning guides for multiple page groups sequentially.
        
        Args:
            page_groups: Dictionary mapping (start_page, end_page) tuples to text
            pdf_name: Name of the PDF file (for saving raw learning guides)
            delay_between_requests: Delay in seconds between API requests
        
        Returns:
            Dictionary mapping page ranges to learning guides
        """
        summaries = {}
        total_groups = len(page_groups)
        
        logger.info(f"{'='*60}")
        logger.info(f"Starting learning guide creation for {total_groups} page groups...")
        logger.info(f"{'='*60}")
        
        for idx, ((start_page, end_page), text) in enumerate(page_groups.items(), 1):
            logger.info(f"\n[{idx}/{total_groups}] Processing pages {start_page}-{end_page}...")
            
            # Check if this page group already has a saved learning guide
            existing_file = self._find_existing_raw_summary(pdf_name, start_page, end_page)
            
            if existing_file:
                logger.info(f"  → Found existing learning guide: {existing_file.name}")
                try:
                    learning_guide = self._load_existing_raw_summary(existing_file)
                    summaries[(start_page, end_page)] = learning_guide
                    logger.info(f"✓ Loaded existing learning guide for pages {start_page}-{end_page} ({len(learning_guide)} chars)\n")
                    continue  # Skip API call
                except Exception as e:
                    logger.warning(f"  Failed to load existing file, will regenerate: {e}")
                    # Fall through to generate new one
            
            logger.info(f"  Text length: {len(text)} characters")
            
            try:
                learning_guide = self.summarize_page_group(text, start_page, end_page, pdf_name)
                summaries[(start_page, end_page)] = learning_guide
                logger.info(f"✓ Successfully created learning guide for pages {start_page}-{end_page}\n")
                
                # Rate limiting: delay between requests
                if idx < total_groups and delay_between_requests > 0:
                    logger.debug(f"Waiting {delay_between_requests}s before next request...")
                    time.sleep(delay_between_requests)
            
            except KeyboardInterrupt:
                logger.warning("\n\nSummarization interrupted by user. Stopping...")
                raise
            except Exception as e:
                error_msg = str(e)
                logger.error(
                    f"✗ Failed to create learning guide for pages {start_page}-{end_page}: {error_msg}"
                )
                # Continue with other groups even if one fails
                summaries[(start_page, end_page)] = (
                    f"[ERROR: Failed to generate learning guide for pages {start_page}-{end_page}. "
                    f"Error: {error_msg}]"
                )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Completed learning guide creation: {len(summaries)}/{total_groups} groups successful")
        logger.info(f"{'='*60}\n")
        return summaries
