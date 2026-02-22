# PDF Compiler

A tool that processes large PDFs, extracts text using OCR, and generates simplified learning guides using Google's Gemini API. Creates concise, easy-to-read study materials that you can use instead of reading the lengthy original text. Includes a CLI and a web frontend.

## Features

- **OCR Text Extraction**: Automatically extracts text from PDFs using Tesseract OCR
- **Smart Text Detection**: Attempts text extraction first, falls back to OCR only when needed
- **Simplified Learning Guides**: Creates concise learning guides from verbose PDFs - removes filler and focuses on essential information
- **Sliding Window Processing**: Processes pages in overlapping groups of 5 (1-5, 4-9, 8-13, etc.)
- **Multiple Output Formats**: Generates both Markdown files and a compiled PDF
- **Batch Processing**: Handles multiple PDFs efficiently with progress tracking

## Prerequisites

- Python 3.8 or higher
- Tesseract OCR installed on your system:
  - **Linux**: `sudo apt-get install tesseract-ocr`
  - **macOS**: `brew install tesseract`
  - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Installation

1. Clone or download this repository

2. (Recommended) Create a virtual environment and install Python dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up your Gemini API key:
```bash
cp env.template .env
# Edit .env and add your GEMINI_API_KEY
```

Or export it as an environment variable:
```bash
export GEMINI_API_KEY=your_api_key_here
```

## Web Frontend

A Svelte + Tailwind + shadcn-svelte web interface lets you upload PDFs, process batches, and download compiled learning guides. Batch history is stored in localStorage (no authentication required).

**Run the web app:**

1. Start the API (from project root):
```bash
uvicorn api.main:app --reload --port 8000
```

2. Start the frontend:
```bash
cd frontend && npm run dev
```

3. Open http://localhost:5173

**Environment:** The frontend expects the API at `http://localhost:8000` by default. Set `VITE_API_URL` in `frontend/.env` if your API runs elsewhere.

## CLI Usage

The tool supports two modes:

- **Flat mode**: When you pass PDF files (or a mix of files and directories), all PDFs are processed into a single output directory with one compiled PDF.
- **Folder mode**: When you pass only directories, each directory is treated as a named group. Output is written to a matching subfolder under the output root, with one compiled PDF per group (e.g. for different lessons or semesters).

### Flat mode (files or mixed)

Process a single PDF:
```bash
python main.py path/to/your/document.pdf
```

Process multiple PDFs or a directory of PDFs (single output):
```bash
python main.py pdf1.pdf pdf2.pdf pdf3.pdf
python main.py /path/to/pdfs/
```

### Folder mode (directories only)

Put PDFs in named folders and get one output folder per input folder with the same name:

```bash
# One folder
python main.py input/topcit
# -> output/topcit/summaries/, output/topcit/compiled.pdf, etc.

# Multiple folders
python main.py input/topcit input/semester2-math
# -> output/topcit/ and output/semester2-math/
```

### Discover subfolders

Process all subfolders of an input root that contain PDFs:

```bash
python main.py input/ --discover
# Discovers input/topcit, input/semester2-math, ... and processes each to output/topcit/, output/semester2-math/, ...
```

### Options

- `--output-dir` or `-o`: Output root directory (default: `./output`)
- `--discover`: With a single directory argument, discover and process each subfolder that contains PDFs
- `--dpi`: OCR DPI setting (default: 300, higher = more accurate but slower)
- `--overlap`: Pages of overlap between groups (default: 2)
- `--skip-compiled`: Skip generating the compiled PDF (only generate Markdown files)

Example:
```bash
python main.py input/topcit -o ./output --dpi 400
python main.py input/ --discover
```

## Output Structure

**Flat mode** (single output dir):
- `output/summaries/`: Individual Markdown files per PDF
- `output/compiled.pdf`: Combined PDF with all learning guides
- `output/ocr_text/`, `output/raw_summaries/`: Per-page OCR text and raw API responses

**Folder mode** (one subfolder per input folder, same name):
- `output/<folder_name>/summaries/`: Individual Markdown files for PDFs in that folder
- `output/<folder_name>/compiled.pdf`: Combined PDF for that folder only
- `output/<folder_name>/ocr_text/`, `output/<folder_name>/raw_summaries/`: Same as above, scoped to that folder

File naming:
- OCR text: `{pdf_name}_page_{page_num}_{source}.txt` (source: `direct_extraction` or `ocr`)
- Raw summaries: `{pdf_name}_pages_{start}-{end}_{timestamp}.txt`

## How It Works

1. **PDF Processing**: Extracts pages and checks for text content
2. **OCR Extraction**: If no text found, converts pages to images and runs OCR
3. **Page Grouping**: Groups pages in sliding windows (e.g., pages 1-5, 4-9, 8-13)
4. **Learning Guide Creation**: Sends each group to Gemini API to create simplified, concise learning guides
   - Removes unnecessary verbosity and filler words
   - Focuses on essential concepts and key information
   - Organizes content for easy studying
5. **Output Generation**: Creates Markdown files and compiles final PDF

## Notes

- Processing 300-page PDFs can take significant time due to OCR and API calls
- Ensure you have sufficient API quota for Gemini
- Output quality depends on PDF image quality for OCR accuracy

## Troubleshooting

**Tesseract not found**: Make sure Tesseract is installed and in your PATH
**API errors**: Check your Gemini API key and quota limits
**Memory issues**: Reduce DPI setting or process PDFs individually

## License

MIT
