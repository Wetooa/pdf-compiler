"""PDF processing module for text extraction and OCR."""
import logging
from pathlib import Path
from typing import List, Optional, Dict
import io

try:
    from PyPDF2 import PdfReader
except ImportError:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ImportError("Please install PyPDF2 or pypdf: pip install PyPDF2")

try:
    from pdf2image import convert_from_path
except ImportError:
    raise ImportError("Please install pdf2image: pip install pdf2image")

try:
    import pytesseract
    from PIL import Image
except ImportError:
    raise ImportError("Please install pytesseract and Pillow: pip install pytesseract Pillow")

from config import Config
from utils import sanitize_filename, ensure_directory

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Handles PDF text extraction with OCR fallback."""
    
    def __init__(self, dpi: int = None, ocr_lang: str = None, ocr_output_dir: str = None):
        """
        Initialize PDF processor.
        
        Args:
            dpi: DPI for image conversion (default: Config.OCR_DPI)
            ocr_lang: OCR language (default: Config.OCR_LANG)
            ocr_output_dir: Directory to save OCR extracted text files (optional)
        """
        self.dpi = dpi or Config.OCR_DPI
        self.ocr_lang = ocr_lang or Config.OCR_LANG
        self.ocr_output_dir = Path(ocr_output_dir) if ocr_output_dir else None
        if self.ocr_output_dir:
            ensure_directory(str(self.ocr_output_dir))
        
    def process_pdf(self, pdf_path: str) -> Dict[int, str]:
        """
        Process a PDF and extract text from all pages.
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Dictionary mapping page numbers (1-indexed) to extracted text
        
        Raises:
            FileNotFoundError: If PDF file doesn't exist
            ValueError: If PDF path is invalid
            RuntimeError: If processing fails
        """
        logger.info(f"Processing PDF: {pdf_path}")
        pdf_path_obj = Path(pdf_path)
        pdf_name = pdf_path_obj.stem
        
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path_obj}")
        
        if not pdf_path_obj.is_file():
            raise ValueError(f"Path is not a file: {pdf_path_obj}")
        
        if pdf_path_obj.suffix.lower() != '.pdf':
            raise ValueError(f"File is not a PDF: {pdf_path_obj}")
        
        try:
            # Try to extract text directly first
            logger.info("Step 1.1: Extracting text directly from PDF...")
            text_pages = self._extract_text_from_pdf(str(pdf_path_obj))
            
            if not text_pages:
                raise RuntimeError(f"Failed to extract any pages from PDF: {pdf_path_obj}")
            
            # Save extracted text if output directory is set
            if self.ocr_output_dir:
                logger.info("Saving extracted text files...")
                for page_num, text in text_pages.items():
                    self._save_page_text(pdf_name, page_num, text, source="direct_extraction")
            
            # Determine which pages need OCR
            pages_needing_ocr = [
                page_num for page_num, text in text_pages.items()
                if not text or len(text.strip()) < 50  # Threshold for "no text"
            ]
            
            if pages_needing_ocr:
                logger.info(
                    f"Found {len(pages_needing_ocr)} pages needing OCR "
                    f"(out of {len(text_pages)} total)"
                )
                logger.info(f"Pages requiring OCR: {pages_needing_ocr}")
                try:
                    ocr_results = self._ocr_pages(str(pdf_path_obj), pages_needing_ocr, pdf_name=pdf_name)
                    
                    # Merge OCR results with extracted text
                    for page_num, ocr_text in ocr_results.items():
                        if ocr_text and len(ocr_text.strip()) > len(text_pages.get(page_num, "").strip()):
                            text_pages[page_num] = ocr_text
                            # Save OCR text if output directory is set
                            if self.ocr_output_dir:
                                self._save_page_text(pdf_name, page_num, ocr_text, source="ocr")
                except RuntimeError as e:
                    logger.warning(f"OCR failed, using extracted text only: {e}")
                    # Continue with text extraction results only
            
            # Filter out pages with no text
            text_pages = {
                page_num: text for page_num, text in text_pages.items()
                if text and text.strip()
            }
            
            if not text_pages:
                raise RuntimeError(
                    f"No text could be extracted from any pages in PDF: {pdf_path_obj}"
                )
            
            logger.info(
                f"✓ Successfully extracted text from {len(text_pages)} pages"
            )
            
            return text_pages
        
        except (FileNotFoundError, ValueError, RuntimeError):
            raise
        except Exception as e:
            error_msg = f"Unexpected error processing PDF {pdf_path_obj}: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def _extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """
        Attempt to extract text directly from PDF.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Dictionary mapping page numbers to extracted text
        """
        text_pages = {}
        
        try:
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            logger.info(f"PDF has {total_pages} pages")
            
            for page_num in range(total_pages):
                try:
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    text_pages[page_num + 1] = text  # 1-indexed
                except Exception as e:
                    logger.warning(
                        f"Error extracting text from page {page_num + 1}: {e}"
                    )
                    text_pages[page_num + 1] = ""
        
        except Exception as e:
            logger.error(f"Error reading PDF: {e}")
            raise
        
        return text_pages
    
    def _save_page_text(self, pdf_name: str, page_num: int, text: str, source: str = "unknown"):
        """
        Save extracted text to a file.
        
        Args:
            pdf_name: Name of the PDF file (without extension)
            page_num: Page number
            text: Extracted text
            source: Source of extraction (e.g., "direct_extraction", "ocr")
        """
        if not self.ocr_output_dir:
            return
        
        try:
            safe_pdf_name = sanitize_filename(pdf_name)
            filename = f"{safe_pdf_name}_page_{page_num:04d}_{source}.txt"
            file_path = self.ocr_output_dir / filename
            
            file_path.write_text(text, encoding='utf-8')
            logger.debug(f"Saved {source} text for page {page_num} to {file_path}")
        except Exception as e:
            logger.warning(f"Failed to save text for page {page_num}: {e}")
    
    def _ocr_pages(self, pdf_path: str, page_numbers: List[int], pdf_name: str = None) -> Dict[int, str]:
        """
        Perform OCR on specific pages of a PDF.
        
        Args:
            pdf_path: Path to PDF file
            page_numbers: List of page numbers to OCR (1-indexed)
        
        Returns:
            Dictionary mapping page numbers to OCR text
        """
        if not page_numbers:
            return {}
        
        logger.info(f"Starting OCR for {len(page_numbers)} pages...")
        ocr_results = {}
        
        try:
            # Validate Tesseract installation
            try:
                pytesseract.get_tesseract_version()
            except Exception as e:
                error_msg = (
                    f"Tesseract OCR not found or not accessible: {e}. "
                    "Please ensure Tesseract is installed and in your PATH."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg) from e
            
            # Convert and OCR each page individually to avoid memory issues
            # when pages are far apart (e.g., page 5 and page 121)
            for page_idx, page_num in enumerate(sorted(page_numbers), 1):
                logger.info(f"Running OCR on page {page_num} ({page_idx}/{len(page_numbers)})...")
                
                try:
                    # Convert only this specific page to image
                    # pdf2image uses 1-indexed pages for first_page/last_page
                    page_image = convert_from_path(
                        pdf_path,
                        dpi=self.dpi,
                        first_page=page_num,
                        last_page=page_num
                    )
                    
                    if not page_image:
                        logger.warning(f"No image generated for page {page_num}")
                        ocr_results[page_num] = ""
                        continue
                    
                    # Extract the single image
                    image = page_image[0]
                    
                    # Run OCR on the image
                    text = pytesseract.image_to_string(image, lang=self.ocr_lang)
                    
                    if text:
                        text_length = len(text.strip())
                        ocr_results[page_num] = text
                        logger.info(f"✓ OCR completed for page {page_num}: extracted {text_length} characters")
                        
                        # Save OCR text immediately
                        if self.ocr_output_dir and pdf_name:
                            self._save_page_text(pdf_name, page_num, text, source="ocr")
                    else:
                        logger.warning(f"No text extracted from page {page_num} via OCR")
                        ocr_results[page_num] = ""
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check if poppler is installed
                    if "poppler" in error_msg or "pdftoppm" in error_msg:
                        raise RuntimeError(
                            "PDF conversion failed. Please ensure poppler-utils is installed:\n"
                            "  Linux: sudo apt-get install poppler-utils\n"
                            "  macOS: brew install poppler\n"
                            "  Windows: Download from poppler.freedesktop.org"
                        ) from e
                    
                    if isinstance(e, pytesseract.TesseractError):
                        logger.warning(f"Tesseract error on page {page_num}: {e}")
                    else:
                        logger.warning(f"Error processing page {page_num}: {e}")
                    ocr_results[page_num] = ""
        
        except RuntimeError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during OCR: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
        
        successful = sum(1 for text in ocr_results.values() if text.strip())
        logger.info(f"OCR completed: {successful}/{len(page_numbers)} pages extracted successfully")
        
        return ocr_results
    
    def get_page_text(self, pdf_path: str, page_number: int) -> str:
        """
        Get text from a specific page.
        
        Args:
            pdf_path: Path to PDF file
            page_number: Page number (1-indexed)
        
        Returns:
            Extracted text from the page
        """
        all_pages = self.process_pdf(pdf_path)
        return all_pages.get(page_number, "")
    
    def get_page_range_text(self, pdf_path: str, start_page: int, end_page: int) -> str:
        """
        Get combined text from a range of pages.
        
        Args:
            pdf_path: Path to PDF file
            start_page: Starting page number (1-indexed)
            end_page: Ending page number (1-indexed, inclusive)
        
        Returns:
            Combined text from all pages in range
        """
        all_pages = self.process_pdf(pdf_path)
        
        texts = []
        for page_num in range(start_page, end_page + 1):
            if page_num in all_pages:
                texts.append(f"--- Page {page_num} ---\n{all_pages[page_num]}\n")
        
        return "\n".join(texts)
