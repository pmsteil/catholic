#!/usr/bin/env python3
"""
PDF Merger Script

Combines all PDF files in a given directory into a single PDF file.

Usage:
    python merge-chapters.py <source_directory> <output_filename>
    uv run merge-chapters.py . book.pdf

Example:
    uv run merge-chapters.py ./chapters combined_book.pdf
"""

import sys
import os
import glob
from pathlib import Path
import PyPDF2
from PyPDF2 import PdfMerger


def natural_sort_key(filename):
    """
    Sort filenames naturally (e.g., chapter1.pdf, chapter2.pdf, chapter10.pdf)
    instead of lexicographically (chapter1.pdf, chapter10.pdf, chapter2.pdf)
    """
    import re
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', filename)]


def merge_pdfs(source_dir, output_filename):
    """
    Merge all PDF files in source_dir into output_filename
    """
    # Convert to Path objects for easier handling
    source_path = Path(source_dir).resolve()
    
    # Find all PDF files in the source directory
    pdf_pattern = source_path / "*.pdf"
    pdf_files = glob.glob(str(pdf_pattern))
    
    if not pdf_files:
        print(f"No PDF files found in directory: {source_path}")
        return False
    
    # Sort files naturally (handles numeric ordering correctly)
    pdf_files.sort(key=lambda x: natural_sort_key(os.path.basename(x)))
    
    print(f"Found {len(pdf_files)} PDF files to merge:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"  {i:2d}. {os.path.basename(pdf_file)}")
    
    # Create merger object
    merger = PdfMerger()
    
    try:
        # Add each PDF file to the merger
        for pdf_file in pdf_files:
            print(f"Adding: {os.path.basename(pdf_file)}")
            try:
                merger.append(pdf_file)
            except Exception as e:
                print(f"Warning: Could not add {pdf_file}: {e}")
                continue
        
        # Write the merged PDF
        print(f"Writing merged PDF to: {output_filename}")
        with open(output_filename, 'wb') as output_file:
            merger.write(output_file)
        
        merger.close()
        print(f"Successfully merged {len(pdf_files)} PDFs into {output_filename}")
        return True
        
    except Exception as e:
        print(f"Error during merge: {e}")
        merger.close()
        return False


def main():
    if len(sys.argv) != 3:
        print("Usage: python merge-chapters.py <source_directory> <output_filename>")
        print("Example: uv run merge-chapters.py . book.pdf")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    output_filename = sys.argv[2]
    
    # Validate source directory
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist or is not a directory")
        sys.exit(1)
    
    # Ensure output filename has .pdf extension
    if not output_filename.lower().endswith('.pdf'):
        output_filename += '.pdf'
    
    # Check if output file already exists
    if os.path.exists(output_filename):
        response = input(f"Output file '{output_filename}' already exists. Overwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            sys.exit(0)
    
    # Perform the merge
    success = merge_pdfs(source_dir, output_filename)
    
    if success:
        # Show file size of result
        file_size = os.path.getsize(output_filename)
        file_size_mb = file_size / (1024 * 1024)
        print(f"Output file size: {file_size_mb:.2f} MB")
        sys.exit(0)
    else:
        print("Merge failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
