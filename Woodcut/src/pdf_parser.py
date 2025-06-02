"""
PDF Parser module for extracting data from architectural drawings.
"""
from pathlib import Path
import fitz  # PyMuPDF

class PDFParser:
    def __init__(self, pdf_path: str | Path):
        self.pdf_path = Path(pdf_path)
        self.doc = None
        self._load_document()
    
    def _load_document(self):
        """Load PDF document."""
        try:
            self.doc = fitz.open(self.pdf_path)
        except Exception as e:
            raise ValueError(f"Failed to load PDF: {e}")
    
    def extract_specification(self) -> dict:
        """Extract specification table if present. Пока просто возвращает текст всех страниц для анализа."""
        if not self.doc:
            self._load_document()
        all_text = []
        for page in self.doc:
            all_text.append(page.get_text())
        return {'pages': all_text}
    
    def extract_drawings(self) -> list:
        """Extract drawings and their measurements."""
        # TODO: Implement drawing extraction
        pass
    
    def analyze_page(self, page_num: int) -> dict:
        """Analyze specific page for wooden elements."""
        # TODO: Implement page analysis
        pass 