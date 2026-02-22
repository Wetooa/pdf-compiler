#!/usr/bin/env python3
"""Main CLI interface for TOPCIT PDF Summarizer."""
import argparse
import sys
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from .config import Config
from .pdf_processor import PDFProcessor
from .summarizer import Summarizer
from .output_generator import OutputGenerator
from .utils import (
    setup_logging,
    get_pdf_files,
    create_sliding_windows,
    ensure_directory,
    normalize_folder_name,
    discover_pdf_folders,
)

logger = logging.getLogger(__name__)


def process_single_pdf(
    pdf_path: str,
    pdf_processor: PDFProcessor,
    summarizer: Summarizer,
    output_gen: OutputGenerator,
    window_size: int,
    overlap: int
) -> Dict[Tuple[int, int], str]:
    """
    Process a single PDF and generate summaries.
    
    Args:
        pdf_path: Path to the PDF file
        pdf_processor: Initialized PDF processor
        summarizer: Initialized summarizer
        output_gen: Initialized output generator
        window_size: Number of pages per group
        overlap: Number of pages to overlap
    
    Returns:
        Dictionary mapping page ranges to summaries
    """
    logger.info(f"\n{'='*60}")
    logger.info(f"Processing: {Path(pdf_path).name}")
    logger.info(f"{'='*60}\n")
    
    try:
        # Extract text from all pages
        logger.info("Step 1: Extracting text from PDF pages...")
        page_texts = pdf_processor.process_pdf(pdf_path)
        
        if not page_texts:
            logger.error(f"No text extracted from {pdf_path}")
            return {}
        
        total_pages = max(page_texts.keys())
        logger.info(f"Successfully extracted text from {len(page_texts)} pages")
        
        # Create sliding windows
        logger.info(f"Step 2: Creating sliding windows (size={window_size}, overlap={overlap})...")
        windows = create_sliding_windows(total_pages, window_size, overlap)
        logger.info(f"Created {len(windows)} page groups")
        
        # Group text by windows
        logger.info("Step 3: Grouping page text...")
        page_groups = {}
        for start_page, end_page in windows:
            texts = []
            for page_num in range(start_page, end_page + 1):
                if page_num in page_texts:
                    texts.append(f"--- Page {page_num} ---\n{page_texts[page_num]}\n")
            
            if texts:
                combined_text = "\n".join(texts)
                page_groups[(start_page, end_page)] = combined_text
        
        logger.info(f"Prepared {len(page_groups)} groups for summarization")
        
        # Create learning guides for page groups
        logger.info("Step 4: Creating simplified learning guides with Gemini API...")
        pdf_name = Path(pdf_path).stem
        summaries = summarizer.summarize_multiple_groups(
            page_groups,
            pdf_name=pdf_name,
            delay_between_requests=1.0
        )
        
        logger.info(f"Generated {len(summaries)} learning guides")
        return summaries
        
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_path}: {e}", exc_info=True)
        return {}


def process_pdf_list(
    pdf_files: List[str],
    pdf_processor: PDFProcessor,
    summarizer: Summarizer,
    output_gen: OutputGenerator,
    window_size: int,
    overlap: int,
    skip_compiled: bool,
    compiled_title: Optional[str] = None,
) -> tuple:
    """
    Process a list of PDFs and optionally compile to a single PDF.

    Returns:
        (all_summaries, successful_pdfs, failed_pdfs)
    """
    all_summaries = {}
    successful_pdfs = []
    failed_pdfs = []

    for pdf_path in pdf_files:
        try:
            pdf_name = Path(pdf_path).name

            existing_md = output_gen.markdown_exists(pdf_path)
            if existing_md:
                logger.info(f"\n{'='*60}")
                logger.info(f"Found existing markdown for: {pdf_name}")
                logger.info(f"File: {existing_md.name}")
                logger.info(f"Skipping processing - markdown already exists")
                logger.info(f"{'='*60}\n")
                successful_pdfs.append(pdf_path)
                continue

            summaries = process_single_pdf(
                pdf_path,
                pdf_processor,
                summarizer,
                output_gen,
                window_size,
                overlap,
            )

            if summaries:
                all_summaries[pdf_path] = summaries
                logger.info("Step 5: Generating Markdown output...")
                output_gen.generate_markdown(pdf_path, summaries)
                successful_pdfs.append(pdf_path)
                logger.info(f"✓ Successfully processed {pdf_name}\n")
            else:
                failed_pdfs.append(pdf_path)
                logger.warning(f"✗ No summaries generated for {pdf_name}\n")

        except KeyboardInterrupt:
            raise
        except Exception as e:
            logger.error(f"Failed to process {pdf_path}: {e}", exc_info=True)
            failed_pdfs.append(pdf_path)

    if not skip_compiled:
        logger.info(f"\n{'='*60}")
        logger.info("Generating compiled PDF from all summaries in folder...")
        logger.info(f"{'='*60}\n")
        try:
            compiled_pdf = output_gen.compile_summaries_folder_to_pdf(
                title=compiled_title
            )
            if compiled_pdf:
                logger.info(f"✓ Compiled PDF created: {compiled_pdf}\n")
            else:
                logger.warning("No summary files found; compiled PDF not created.\n")
        except Exception as e:
            logger.error(f"Failed to compile PDF: {e}", exc_info=True)

    return all_summaries, successful_pdfs, failed_pdfs


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="TOPCIT PDF Summarizer - Extract text from PDFs and generate summaries using Gemini API",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'pdfs',
        nargs='+',
        help='PDF file(s) or directory containing PDFs to process'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default=Config.DEFAULT_OUTPUT_DIR,
        help=f'Output directory for summaries (default: {Config.DEFAULT_OUTPUT_DIR})'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=Config.OCR_DPI,
        help=f'DPI for OCR image conversion (default: {Config.OCR_DPI})'
    )
    
    parser.add_argument(
        '--window-size',
        type=int,
        default=Config.PAGES_PER_GROUP,
        help=f'Number of pages per group (default: {Config.PAGES_PER_GROUP})'
    )
    
    parser.add_argument(
        '--overlap',
        type=int,
        default=Config.DEFAULT_OVERLAP,
        help=f'Pages of overlap between groups (default: {Config.DEFAULT_OVERLAP})'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--skip-compiled',
        action='store_true',
        help='Skip generating the compiled PDF (only generate Markdown files)'
    )

    parser.add_argument(
        '--discover',
        action='store_true',
        help='Treat single directory as input root and process each subfolder that contains PDFs'
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(verbose=args.verbose)

    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    output_root = Path(args.output_dir)
    all_successful = []
    all_failed = []
    total_pdfs = 0

    # Determine mode: flat (files or mixed) vs folder (directories only)
    path_objs = [Path(p) for p in args.pdfs]
    any_file = any(p.is_file() for p in path_objs)
    all_dirs = all(p.is_dir() for p in path_objs)

    if any_file:
        # Flat mode: collect all PDFs into one list, single output dir
        all_pdf_files = []
        for pdf_input in args.pdfs:
            try:
                pdf_files = get_pdf_files(pdf_input)
                all_pdf_files.extend(pdf_files)
            except ValueError as e:
                logger.warning(f"Skipping {pdf_input}: {e}")

        if not all_pdf_files:
            logger.error("No PDF files found to process")
            sys.exit(1)

        logger.info(f"Found {len(all_pdf_files)} PDF file(s) to process (flat mode)")
        total_pdfs = len(all_pdf_files)

        ocr_output_dir = output_root / Config.OCR_TEXT_SUBDIR
        raw_summaries_dir = output_root / Config.RAW_SUMMARIES_SUBDIR
        ensure_directory(str(output_root))
        ensure_directory(str(ocr_output_dir))
        ensure_directory(str(raw_summaries_dir))
        logger.info(f"Output directory: {output_root}\n")

        try:
            pdf_processor = PDFProcessor(dpi=args.dpi, ocr_output_dir=str(ocr_output_dir))
            summarizer = Summarizer(raw_summaries_dir=str(raw_summaries_dir))
            output_gen = OutputGenerator(str(output_root))
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}", exc_info=True)
            sys.exit(1)

        try:
            _, successful_pdfs, failed_pdfs = process_pdf_list(
                all_pdf_files,
                pdf_processor,
                summarizer,
                output_gen,
                args.window_size,
                args.overlap,
                args.skip_compiled,
                compiled_title=None,
            )
            all_successful.extend(successful_pdfs)
            all_failed.extend(failed_pdfs)
        except KeyboardInterrupt:
            logger.warning("\n\nProcess interrupted by user")
            sys.exit(1)

    elif all_dirs and (not args.discover or len(args.pdfs) != 1):
        # Folder mode: each directory is a group (explicit list, or multiple dirs)
        if args.discover and len(args.pdfs) != 1:
            logger.warning("--discover requires a single directory argument; ignoring --discover")

        groups = []
        for p in args.pdfs:
            path = Path(p)
            if path.is_dir():
                groups.append((str(path.resolve()), normalize_folder_name(p)))

        if not groups:
            logger.error("No directories found to process")
            sys.exit(1)

        for folder_path, folder_name in groups:
            try:
                pdf_files = get_pdf_files(folder_path)
            except ValueError as e:
                logger.warning(f"Skipping folder {folder_path}: {e}")
                continue

            logger.info(f"\n{'='*60}")
            logger.info(f"Folder: {folder_name} ({len(pdf_files)} PDF(s))")
            logger.info(f"{'='*60}\n")
            total_pdfs += len(pdf_files)

            group_output_dir = output_root / folder_name
            ocr_output_dir = group_output_dir / Config.OCR_TEXT_SUBDIR
            raw_summaries_dir = group_output_dir / Config.RAW_SUMMARIES_SUBDIR
            ensure_directory(str(group_output_dir))
            ensure_directory(str(ocr_output_dir))
            ensure_directory(str(raw_summaries_dir))
            logger.info(f"Output directory: {group_output_dir}\n")

            try:
                pdf_processor = PDFProcessor(dpi=args.dpi, ocr_output_dir=str(ocr_output_dir))
                summarizer = Summarizer(raw_summaries_dir=str(raw_summaries_dir))
                output_gen = OutputGenerator(str(group_output_dir))
            except Exception as e:
                logger.error(f"Failed to initialize components for {folder_name}: {e}", exc_info=True)
                all_failed.extend(pdf_files)
                continue

            try:
                _, successful_pdfs, failed_pdfs = process_pdf_list(
                    pdf_files,
                    pdf_processor,
                    summarizer,
                    output_gen,
                    args.window_size,
                    args.overlap,
                    args.skip_compiled,
                    compiled_title=f"Learning Guides: {folder_name}",
                )
                all_successful.extend(successful_pdfs)
                all_failed.extend(failed_pdfs)
            except KeyboardInterrupt:
                logger.warning("\n\nProcess interrupted by user")
                sys.exit(1)

    else:
        # --discover with single directory: discover subfolders
        if not (args.discover and len(args.pdfs) == 1):
            logger.error("No PDF files or directories found to process")
            sys.exit(1)

        root_dir = args.pdfs[0]
        try:
            groups = discover_pdf_folders(root_dir)
        except ValueError as e:
            logger.error(str(e))
            sys.exit(1)

        if not groups:
            logger.error(f"No subfolders containing PDFs found under {root_dir}")
            sys.exit(1)

        logger.info(f"Discovered {len(groups)} folder(s) with PDFs under {root_dir}\n")

        for folder_path, folder_name in groups:
            try:
                pdf_files = get_pdf_files(folder_path)
            except ValueError:
                continue

            logger.info(f"\n{'='*60}")
            logger.info(f"Folder: {folder_name} ({len(pdf_files)} PDF(s))")
            logger.info(f"{'='*60}\n")
            total_pdfs += len(pdf_files)

            group_output_dir = output_root / folder_name
            ocr_output_dir = group_output_dir / Config.OCR_TEXT_SUBDIR
            raw_summaries_dir = group_output_dir / Config.RAW_SUMMARIES_SUBDIR
            ensure_directory(str(group_output_dir))
            ensure_directory(str(ocr_output_dir))
            ensure_directory(str(raw_summaries_dir))
            logger.info(f"Output directory: {group_output_dir}\n")

            try:
                pdf_processor = PDFProcessor(dpi=args.dpi, ocr_output_dir=str(ocr_output_dir))
                summarizer = Summarizer(raw_summaries_dir=str(raw_summaries_dir))
                output_gen = OutputGenerator(str(group_output_dir))
            except Exception as e:
                logger.error(f"Failed to initialize components for {folder_name}: {e}", exc_info=True)
                all_failed.extend(pdf_files)
                continue

            try:
                _, successful_pdfs, failed_pdfs = process_pdf_list(
                    pdf_files,
                    pdf_processor,
                    summarizer,
                    output_gen,
                    args.window_size,
                    args.overlap,
                    args.skip_compiled,
                    compiled_title=f"Learning Guides: {folder_name}",
                )
                all_successful.extend(successful_pdfs)
                all_failed.extend(failed_pdfs)
            except KeyboardInterrupt:
                logger.warning("\n\nProcess interrupted by user")
                sys.exit(1)

    # Print summary
    logger.info(f"\n{'='*60}")
    logger.info("Processing Summary")
    logger.info(f"{'='*60}")
    logger.info(f"Total PDFs: {total_pdfs}")
    logger.info(f"Successful: {len(all_successful)}")
    logger.info(f"Failed: {len(all_failed)}")

    if all_successful:
        logger.info("\nSuccessfully processed:")
        for pdf in all_successful:
            logger.info(f"  - {Path(pdf).name}")

    if all_failed:
        logger.warning("\nFailed to process:")
        for pdf in all_failed:
            logger.warning(f"  - {Path(pdf).name}")
        sys.exit(1)


if __name__ == "__main__":
    main()

