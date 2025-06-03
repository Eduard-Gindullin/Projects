import unittest
from .geometry import Circle, Triangle
from .factory import FigureFactory

class TestGeometry(unittest.TestCase):
    def test_circle_area(self):
        c = Circle(2)
        self.assertAlmostEqual(c.area(), 12.5663706, places=5)

    def test_triangle_area(self):
        t = Triangle(3, 4, 5)
        self.assertAlmostEqual(t.area(), 6.0, places=5)

    def test_triangle_is_right(self):
        t = Triangle(3, 4, 5)
        self.assertTrue(t.is_right())
        t2 = Triangle(2, 2, 3)
        self.assertFalse(t2.is_right())

    def test_factory_circle(self):
        f = FigureFactory.create_figure(radius=1)
        self.assertIsInstance(f, Circle)
        self.assertAlmostEqual(f.area(), 3.1415926, places=5)

    def test_factory_triangle(self):
        f = FigureFactory.create_figure(a=3, b=4, c=5)
        self.assertIsInstance(f, Triangle)
        self.assertAlmostEqual(f.area(), 6.0, places=5)

    def test_factory_invalid(self):
        with self.assertRaises(ValueError):
            FigureFactory.create_figure(x=1, y=2)

if __name__ == '__main__':
    unittest.main() 