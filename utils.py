"""Utility functions for the PDF summarizer."""
import os
import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def ensure_directory(path: str):
    """Ensure a directory exists, creating it if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)


def get_pdf_files(path: str) -> List[str]:
    """Get all PDF files from a path (file or directory)."""
    path_obj = Path(path)
    
    if path_obj.is_file():
        if path_obj.suffix.lower() == '.pdf':
            return [str(path_obj.absolute())]
        else:
            raise ValueError(f"File is not a PDF: {path}")
    
    elif path_obj.is_dir():
        pdf_files = list(path_obj.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in directory: {path}")
        return [str(f.absolute()) for f in pdf_files]
    
    else:
        raise ValueError(f"Path does not exist: {path}")


def normalize_folder_name(path: str) -> str:
    """Return the last path component for use as output folder name."""
    return Path(path).resolve().name


def discover_pdf_folders(root_dir: str) -> List[Tuple[str, str]]:
    """
    Discover immediate subdirectories of root_dir that contain at least one PDF.

    Args:
        root_dir: Path to the input root directory.

    Returns:
        List of (folder_path, folder_name) for each subdir that has PDFs.
        folder_name is the last path component (e.g. 'topcit' for 'input/topcit').

    Raises:
        ValueError: If root_dir does not exist or is not a directory.
    """
    root = Path(root_dir)
    if not root.exists():
        raise ValueError(f"Path does not exist: {root_dir}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root_dir}")

    result = []
    for item in sorted(root.iterdir()):
        if item.is_dir():
            try:
                get_pdf_files(str(item))
                result.append((str(item.resolve()), normalize_folder_name(str(item))))
            except ValueError:
                continue
    return result


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename for safe filesystem usage."""
    # Remove path separators and other problematic characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def create_sliding_windows(total_pages: int, window_size: int, overlap: int) -> List[Tuple[int, int]]:
    """
    Create sliding windows for page grouping.
    
    Args:
        total_pages: Total number of pages
        window_size: Number of pages per window
        overlap: Number of pages to overlap between windows
    
    Returns:
        List of tuples (start_page, end_page) (1-indexed)
    
    Raises:
        ValueError: If parameters are invalid
    
    Example:
        create_sliding_windows(10, 5, 2)
        # Returns: [(1, 5), (4, 9), (8, 13)]  (if total_pages >= 13)
    """
    if total_pages < 1:
        raise ValueError(f"total_pages must be at least 1, got {total_pages}")
    
    if window_size < 1:
        raise ValueError(f"window_size must be at least 1, got {window_size}")
    
    if overlap < 0:
        raise ValueError(f"overlap must be non-negative, got {overlap}")
    
    if overlap >= window_size:
        raise ValueError(
            f"overlap ({overlap}) must be less than window_size ({window_size})"
        )
    
    windows = []
    start = 1
    
    while start <= total_pages:
        end = min(start + window_size - 1, total_pages)
        windows.append((start, end))
        
        # Move to next window with overlap
        if end >= total_pages:
            break
        start = end - overlap + 1
        
        # Safety check to prevent infinite loops
        if start <= windows[-1][0] if windows else 1:
            logger.warning(
                f"Window progression stopped. Generated {len(windows)} windows "
                f"for {total_pages} pages with window_size={window_size}, overlap={overlap}"
            )
            break
    
    if not windows:
        raise ValueError(
            f"Failed to create any windows for total_pages={total_pages}, "
            f"window_size={window_size}, overlap={overlap}"
        )
    
    return windows
