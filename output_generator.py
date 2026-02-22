"""Output generation module for Markdown and PDF compilation."""
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

try:
    import markdown
except ImportError:
    raise ImportError(
        "markdown package not found. "
        "Please install it: pip install markdown"
    )

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    raise ImportError(
        "weasyprint package not found. "
        "Please install it: pip install weasyprint"
    )

from utils import sanitize_filename, ensure_directory

logger = logging.getLogger(__name__)


class OutputGenerator:
    """Handles generation of Markdown and PDF outputs."""
    
    def __init__(self, output_dir: str):
        """
        Initialize output generator.
        
        Args:
            output_dir: Base output directory
        """
        self.output_dir = Path(output_dir)
        self.summaries_dir = self.output_dir / "summaries"
        
        # Ensure directories exist
        ensure_directory(str(self.output_dir))
        ensure_directory(str(self.summaries_dir))
    
    def markdown_exists(self, pdf_name: str) -> Optional[Path]:
        """
        Check if a Markdown file already exists for the given PDF.
        
        Args:
            pdf_name: Name of the source PDF (for filename)
        
        Returns:
            Path to existing file if found, None otherwise
        """
        safe_name = sanitize_filename(Path(pdf_name).stem)
        md_file = self.summaries_dir / f"{safe_name}_summary.md"
        
        if md_file.exists():
            return md_file
        return None
    
    def generate_markdown(
        self,
        pdf_name: str,
        summaries: Dict[Tuple[int, int], str]
    ) -> Path:
        """
        Generate a Markdown file for a PDF's summaries.
        
        Args:
            pdf_name: Name of the source PDF (for filename)
            summaries: Dictionary mapping (start_page, end_page) to summary text
        
        Returns:
            Path to the generated Markdown file
        """
        # Sanitize PDF name for filename
        safe_name = sanitize_filename(Path(pdf_name).stem)
        md_file = self.summaries_dir / f"{safe_name}_summary.md"
        
        logger.info(f"Generating Markdown file: {md_file}")
        
        # Build Markdown content
        content = []
        content.append(f"# Learning Guide: {Path(pdf_name).name}\n")
        content.append(f"\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        content.append(f"\n*This is a simplified learning guide created from the original PDF. Use this for studying instead of reading the lengthy original text.*\n")
        content.append("\n---\n")
        
        # Sort page groups by starting page
        sorted_groups = sorted(summaries.items(), key=lambda x: x[0][0])
        
        for (start_page, end_page), summary in sorted_groups:
            content.append(f"\n## Pages {start_page}-{end_page}\n")
            content.append(f"\n{summary}\n")
            content.append("\n---\n")
        
        # Write Markdown file
        try:
            md_content = "\n".join(content)
            md_file.write_text(md_content, encoding='utf-8')
            logger.info(f"Markdown file created: {md_file}")
            return md_file
        except PermissionError as e:
            error_msg = f"Permission denied writing to {md_file}: {e}"
            logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except OSError as e:
            error_msg = f"OS error writing Markdown file {md_file}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error writing Markdown file {md_file}: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def compile_markdown_to_pdf(
        self,
        md_file: Path,
        output_pdf: Path = None
    ) -> Path:
        """
        Compile a Markdown file to PDF.
        
        Args:
            md_file: Path to Markdown file
            output_pdf: Optional output PDF path (default: same name with .pdf extension)
        
        Returns:
            Path to the generated PDF file
        """
        if output_pdf is None:
            output_pdf = md_file.with_suffix('.pdf')
        
        logger.info(f"Compiling PDF: {output_pdf}")
        
        # Read Markdown content
        md_content = md_file.read_text(encoding='utf-8')
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['toc', 'tables', 'fenced_code', 'attr_list']
        )
        
        # Wrap in full HTML document with styling
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        body {{
            font-family: 'DejaVu Sans', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 5px;
            margin-top: 30px;
        }}
        h3 {{
            color: #555;
            margin-top: 20px;
        }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 20px 0;
        }}
        .toc {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
        
        # Generate PDF
        try:
            font_config = FontConfiguration()
            HTML(string=full_html).write_pdf(
                output_pdf,
                font_config=font_config
            )
            logger.info(f"PDF compiled successfully: {output_pdf}")
            return output_pdf
        
        except PermissionError as e:
            error_msg = f"Permission denied writing PDF to {output_pdf}: {e}"
            logger.error(error_msg)
            raise PermissionError(error_msg) from e
        except OSError as e:
            error_msg = f"OS error compiling PDF {output_pdf}: {e}"
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            error_msg = f"Error compiling PDF {output_pdf}: {e}"
            logger.error(error_msg, exc_info=True)
            # Check for common weasyprint errors
            error_str = str(e).lower()
            if "font" in error_str or "glyph" in error_str:
                logger.warning(
                    "Font-related error detected. The PDF may still be generated "
                    "but with default fonts."
                )
            raise RuntimeError(error_msg) from e

    def compile_summaries_folder_to_pdf(
        self,
        output_filename: str = "compiled.pdf",
        title: Optional[str] = None,
    ) -> Optional[Path]:
        """
        Compile all summary Markdown files in the summaries directory into a
        single PDF. Uses whatever is on disk so that re-runs include every
        summary that exists, not only those from the current run.

        Args:
            output_filename: Name for the output PDF file.
            title: Optional title for the compiled document (e.g. group name).

        Returns:
            Path to the compiled PDF, or None if no summary files exist.
        """
        summary_files = sorted(self.summaries_dir.glob("*_summary.md"))
        if not summary_files:
            logger.warning("No summary markdown files found; skipping compiled PDF.")
            return None

        logger.info(f"Compiling {len(summary_files)} summaries from folder into: {output_filename}")
        heading = f"# {title}\n" if title else "# PDF Learning Guides\n"
        content = []
        content.append(heading)
        content.append(f"\n*Compiled on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        content.append(f"\n*Total documents: {len(summary_files)}*\n")
        content.append("\n*These are simplified learning guides. Use these for studying instead of the lengthy originals.*\n")
        content.append("\n---\n")
        content.append("\n## Table of Contents\n\n")

        toc_entries = []
        file_contents = []
        for md_file in summary_files:
            text = md_file.read_text(encoding="utf-8")
            lines = text.split("\n")
            first_line = lines[0] if lines else ""
            if first_line.startswith("# "):
                doc_title = first_line[2:].strip()
            else:
                doc_title = md_file.stem.replace("_summary", "").replace("_", " ")
            anchor = (
                sanitize_filename(md_file.stem.replace("_summary", ""))
                .replace("_", "-")
                .replace(" ", "-")
                .lower()
            )
            toc_entries.append((doc_title, anchor))
            if first_line.startswith("# ") and "{" not in first_line:
                lines[0] = f"{first_line} {{#{anchor}}}"
            file_contents.append("\n".join(lines))

        for doc_title, anchor in toc_entries:
            content.append(f"- [{doc_title}](#{anchor})\n")
        content.append("\n---\n")

        for block in file_contents:
            content.append(block)
            content.append("\n---\n")

        combined_md = self.summaries_dir / "_combined.md"
        combined_md.write_text("\n".join(content), encoding="utf-8")
        output_pdf = self.output_dir / output_filename
        try:
            self.compile_markdown_to_pdf(combined_md, output_pdf)
            logger.info(f"Combined PDF created: {output_pdf}")
            return output_pdf
        except Exception as e:
            logger.error(f"Failed to compile combined PDF: {e}")
            raise
        finally:
            try:
                if combined_md.exists():
                    combined_md.unlink()
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {combined_md}: {cleanup_error}")

    def compile_all_to_single_pdf(
        self,
        pdf_summaries: Dict[str, Dict[Tuple[int, int], str]],
        output_filename: str = "compiled.pdf",
        title: Optional[str] = None
    ) -> Path:
        """
        Compile all PDF summaries into a single combined PDF.

        Args:
            pdf_summaries: Dictionary mapping PDF names to their summaries
            output_filename: Name for the output PDF file
            title: Optional title for the compiled document (e.g. group name).
                   Defaults to "PDF Learning Guides".

        Returns:
            Path to the compiled PDF
        """
        logger.info(f"Compiling all summaries into single PDF: {output_filename}")

        heading = f"# {title}\n" if title else "# PDF Learning Guides\n"
        content = []
        content.append(heading)
        content.append(f"\n*Compiled on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        content.append(f"\n*Total PDFs: {len(pdf_summaries)}*\n")
        content.append("\n*These are simplified learning guides created from the original PDFs. Use these for studying instead of reading the lengthy original text.*\n")
        content.append("\n---\n")
        
        # Table of contents
        content.append("\n## Table of Contents\n\n")
        for pdf_name in sorted(pdf_summaries.keys()):
            safe_name = sanitize_filename(Path(pdf_name).stem)
            content.append(f"- [{Path(pdf_name).name}](#{safe_name.replace('_', '-')})\n")
        content.append("\n---\n")
        
        # Add summaries for each PDF
        for pdf_name, summaries in sorted(pdf_summaries.items()):
            safe_name = sanitize_filename(Path(pdf_name).stem)
            content.append(f"\n# {Path(pdf_name).name}\n")
            content.append(f"{{#{safe_name.replace('_', '-')}}}\n")
            content.append("\n---\n")
            
            # Sort page groups
            sorted_groups = sorted(summaries.items(), key=lambda x: x[0][0])
            
            for (start_page, end_page), summary in sorted_groups:
                content.append(f"\n## Pages {start_page}-{end_page}\n")
                content.append(f"\n{summary}\n")
                content.append("\n---\n")
        
        # Write temporary combined Markdown
        combined_md = self.summaries_dir / "_combined.md"
        combined_md.write_text("\n".join(content), encoding='utf-8')
        
        # Compile to PDF
        output_pdf = self.output_dir / output_filename
        try:
            self.compile_markdown_to_pdf(combined_md, output_pdf)
            logger.info(f"Combined PDF created: {output_pdf}")
            return output_pdf
        except Exception as e:
            logger.error(f"Failed to compile combined PDF: {e}")
            raise
        finally:
            # Clean up temporary file
            try:
                if combined_md.exists():
                    combined_md.unlink()
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {combined_md}: {cleanup_error}")
