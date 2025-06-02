"""
PDF Parser module for extracting data from architectural drawings.
"""
from pathlib import Path
import fitz  # PyMuPDF
import re
import pandas as pd

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
        """Extract specification table if present. Ищет таблицы с нужными колонками и корректно парсит значения."""
        if not self.doc:
            self._load_document()
        all_text = []
        for page in self.doc:
            all_text.append(page.get_text("text"))
        # Ключевые слова для поиска таблиц
        keywords = [
            'спецификация', 'стена', 'доски', 'кровля', 'балка', 'брус', 'перекрытие', 'стропила', 'рама', 'обвязка'
        ]
        spec_tables = []
        for page_text in all_text:
            if any(kw.lower() in page_text.lower() for kw in keywords):
                lines = page_text.splitlines()
                print("[DEBUG] --- Страница с ключевым словом ---")
                for l in lines:
                    print(f"[DEBUG] {l}")
                # Индексы заголовков
                headers = ['Поз.', 'Наименование', 'Длина, мм', 'Ширина, мм', 'Толщина, мм', 'Высота, мм', 'Кол-во, шт.']
                header_indices = {}
                for idx, line in enumerate(lines):
                    if line.strip() in headers:
                        header_indices[line.strip()] = idx
                # Собираем значения под каждым заголовком, фильтруя только данные
                def is_number(s):
                    return bool(re.match(r'^\d+[\d.,]*$', s.strip()))
                columns = {}
                for h, start_idx in header_indices.items():
                    next_indices = [i for i in header_indices.values() if i > start_idx]
                    end_idx = min(next_indices) if next_indices else len(lines)
                    raw_values = [l.strip() for l in lines[start_idx+1:end_idx] if l.strip()]
                    # Для 'Поз.' и 'Наименование' берём все строки, для остальных — только числа
                    if h in ['Поз.', 'Наименование']:
                        values = [v for v in raw_values if v not in headers and v.lower() not in ['мм', 'высота', 'ширина', 'толщина', 'длина', 'кол-во', 'шт.']]
                    else:
                        values = [v for v in raw_values if is_number(v)]
                    columns[h] = values
                    print(f"[DEBUG] {h}: {values}")
                n = max(len(col) for col in columns.values()) if columns else 0
                data = []
                for i in range(n):
                    row = {
                        'Поз': columns.get('Поз.', [''])[i] if i < len(columns.get('Поз.', [])) else '',
                        'Наименование': columns.get('Наименование', [''])[i] if i < len(columns.get('Наименование', [])) else '',
                        'Длина, мм': float(columns.get('Длина, мм', ['0'])[i].replace(' ', '').replace('\u00A0', '').replace(',', '.')) if i < len(columns.get('Длина, мм', [])) and columns.get('Длина, мм', [''])[i] else 0.0,
                        'Ширина, мм': float(columns.get('Ширина, мм', ['0'])[i].replace(' ', '').replace('\u00A0', '').replace(',', '.')) if i < len(columns.get('Ширина, мм', [])) and columns.get('Ширина, мм', [''])[i] else 0.0,
                        'Толщина, мм': float(columns.get('Толщина, мм', ['0'])[i].replace(' ', '').replace('\u00A0', '').replace(',', '.')) if i < len(columns.get('Толщина, мм', [])) and columns.get('Толщина, мм', [''])[i] else 0.0,
                        'Высота, мм': float(columns.get('Высота, мм', ['0'])[i].replace(' ', '').replace('\u00A0', '').replace(',', '.')) if i < len(columns.get('Высота, мм', [])) and columns.get('Высота, мм', [''])[i] else 0.0,
                        'Кол-во, шт.': int(columns.get('Кол-во, шт.', ['1'])[i].replace(' ', '').replace('\u00A0', '')) if i < len(columns.get('Кол-во, шт.', [])) and columns.get('Кол-во, шт.', [''])[i] else 1
                    }
                    data.append(row)
                if data:
                    print(f"[DEBUG] Первая собранная строка: {data[0]}")
                    spec_tables.extend(data)
        return {'specifications': spec_tables}
    
    def extract_drawings(self) -> list:
        """Extract drawings and their measurements."""
        # TODO: Implement drawing extraction
        pass
    
    def analyze_page(self, page_num: int) -> dict:
        """Analyze specific page for wooden elements."""
        # TODO: Implement page analysis
        pass 