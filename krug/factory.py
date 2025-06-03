from .geometry import Circle, Triangle

class FigureFactory:
    @staticmethod
    def create_figure(**kwargs):
        if 'radius' in kwargs:
            return Circle(kwargs['radius'])
        elif all(k in kwargs for k in ('a', 'b', 'c')):
            return Triangle(kwargs['a'], kwargs['b'], kwargs['c'])
        else:
            raise ValueError('Unknown figure parameters') 