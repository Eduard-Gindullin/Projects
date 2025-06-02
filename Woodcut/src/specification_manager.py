"""
Specification manager module for handling wood piece specifications.
Supports manual input and import from various formats.
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
import pandas as pd
from pathlib import Path
import json
import csv

@dataclass
class WoodElement:
    id: str
    description: str
    length: float
    width: float
    quantity: int
    height: float = 0.0
    is_rectangular: bool = True
    notes: str = ""
    custom_shape: Optional[dict] = None  # For non-rectangular pieces

class SpecificationManager:
    def __init__(self):
        self.elements: Dict[str, WoodElement] = {}
        self.project_name: str = ""
        self.project_notes: str = ""

    def add_element(self, element: WoodElement) -> None:
        """Add or update a wood element manually."""
        self.elements[element.id] = element

    def remove_element(self, element_id: str) -> None:
        """Remove an element from specification."""
        if element_id in self.elements:
            del self.elements[element_id]

    def import_from_excel(self, file_path: str | Path) -> None:
        """Import specification from Excel file."""
        try:
            df = pd.read_excel(file_path)
            required_columns = ['id', 'description', 'length', 'width', 'height', 'quantity']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"Missing required columns. Required: {required_columns}")
            
            for _, row in df.iterrows():
                element = WoodElement(
                    id=str(row['id']),
                    description=str(row['description']),
                    length=float(row['length']),
                    width=float(row['width']),
                    height=float(row.get('height', 0)),
                    quantity=int(row['quantity']),
                    is_rectangular=row.get('is_rectangular', True),
                    notes=str(row.get('notes', "")),
                    custom_shape=json.loads(row['custom_shape']) if 'custom_shape' in row else None
                )
                self.add_element(element)
        except Exception as e:
            raise ValueError(f"Failed to import Excel file: {e}")

    def import_from_csv(self, file_path: str | Path) -> None:
        """Import specification from CSV file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    element = WoodElement(
                        id=row['id'],
                        description=row['description'],
                        length=float(row['length']),
                        width=float(row['width']),
                        height=float(row.get('height', 0)),
                        quantity=int(row['quantity']),
                        is_rectangular=row.get('is_rectangular', 'True').lower() == 'true',
                        notes=row.get('notes', ""),
                        custom_shape=json.loads(row['custom_shape']) if 'custom_shape' in row else None
                    )
                    self.add_element(element)
        except Exception as e:
            raise ValueError(f"Failed to import CSV file: {e}")

    def export_to_excel(self, file_path: str | Path) -> None:
        """Export specification to Excel file."""
        data = []
        for element in self.elements.values():
            element_dict = {
                'id': element.id,
                'description': element.description,
                'length': element.length,
                'width': element.width,
                'height': getattr(element, 'height', 0.0),
                'quantity': element.quantity,
                'is_rectangular': element.is_rectangular,
                'notes': element.notes,
                'custom_shape': json.dumps(element.custom_shape) if element.custom_shape else None
            }
            data.append(element_dict)
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)

    def get_total_elements(self) -> int:
        """Get total number of elements."""
        return sum(element.quantity for element in self.elements.values())

    def get_unique_sizes(self) -> List[tuple]:
        """Get list of unique sizes (length, width)."""
        sizes = set()
        for element in self.elements.values():
            sizes.add((element.length, element.width))
        return sorted(list(sizes))

    def calculate_total_length(self) -> float:
        """Calculate total length of all elements."""
        return sum(element.length * element.quantity for element in self.elements.values())

    def to_dict(self) -> dict:
        """Convert specification to dictionary."""
        return {
            'project_name': self.project_name,
            'project_notes': self.project_notes,
            'elements': {
                id: {
                    'id': e.id,
                    'description': e.description,
                    'length': e.length,
                    'width': e.width,
                    'height': getattr(e, 'height', 0.0),
                    'quantity': e.quantity,
                    'is_rectangular': e.is_rectangular,
                    'notes': e.notes,
                    'custom_shape': e.custom_shape
                }
                for id, e in self.elements.items()
            }
        }

    def from_dict(self, data: dict) -> None:
        """Load specification from dictionary."""
        self.project_name = data.get('project_name', '')
        self.project_notes = data.get('project_notes', '')
        self.elements.clear()
        
        for element_data in data.get('elements', {}).values():
            element = WoodElement(**element_data)
            self.add_element(element) 