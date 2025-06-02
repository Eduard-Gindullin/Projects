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
        """Extract specification table if present. Ищет страницы с 'Спецификация материалов' и парсит таблицу."""
        if not self.doc:
            self._load_document()
        all_text = []
        for page in self.doc:
            all_text.append(page.get_text())
        # Найти страницы с таблицей спецификаций
        spec_pages = []
        for i, text in enumerate(all_text):
            if 'Спецификация материалов' in text:
                spec_pages.append((i, text))
        # Парсить таблицы
        specs = []
        for page_num, text in spec_pages:
            lines = text.splitlines()
            # Найти начало таблицы по ключевым словам
            try:
                start_idx = next(i for i, l in enumerate(lines) if 'Поз.' in l and 'Наименование' in l)
            except StopIteration:
                continue
            # Найти конец таблицы (до следующего заголовка или пустой строки)
            table_lines = []
            for l in lines[start_idx+1:]:
                if l.strip() == '' or 'Итоговая спецификация' in l:
                    break
                table_lines.append(l)
            print(f"\n--- Таблица на странице {page_num+1} ---")
            for l in table_lines:
                print(l)
            # Парсить строки таблицы
            # Ожидаем: Поз., Обозначение, Наименование, Длина, мм, Кол-во, шт.
            # Данные могут идти в несколько строк, поэтому ищем паттерны
            current = {}
            for l in table_lines:
                parts = l.split()
                if len(parts) < 2:
                    continue
                # Если строка начинается с Д/Б/Брус/Брусок и далее есть числа, это строка спецификации
                if parts[0].startswith(('Д', 'Б')) and any(p.isdigit() for p in parts):
                    # Пример: Д37 Доска, сечение 150 x 50 мм 50 5
                    poz = parts[0]
                    # Наименование может быть из нескольких слов
                    try:
                        length_idx = next(i for i, p in enumerate(parts) if p.replace(' ', '').isdigit())
                    except StopIteration:
                        continue
                    name = ' '.join(parts[1:length_idx])
                    length = parts[length_idx]
                    qty = parts[length_idx+1] if length_idx+1 < len(parts) else ''
                    specs.append({
                        'Поз': poz,
                        'Наименование': name,
                        'Длина, мм': length,
                        'Кол-во, шт.': qty
                    })
            # Можно добавить обработку многострочных наименований при необходимости
        return {'specifications': specs}
    
    def extract_drawings(self) -> list:
        """Extract drawings and their measurements."""
        # TODO: Implement drawing extraction
        pass
    
    def analyze_page(self, page_num: int) -> dict:
        """Analyze specific page for wooden elements."""
        # TODO: Implement page analysis
        pass 