from typing import List, Union, Dict

import numpy as np
from datatypes.collections import CyclicList
from datatypes.geometry import Point2D, Vector2D

from circuit_generator.sections import BezierTurn, Straight, Segment


class CircuitPerimeter:
    def __init__(self, segments):
        if not isinstance(segments, CyclicList):
            segments = CyclicList(segments)
        self.segments: CyclicList = segments

    def __getitem__(self, item):
        return self.segments[item]

    def __setitem__(self, pos, item):
        self.segments[pos] = item

    def __iter__(self):
        return self.segments.__iter__()

    def __add__(self, other):
        if not isinstance(other, Vector2D):
            return NotImplemented
        return CircuitPerimeter([Segment(s.a + other, s.b + other) for s in self])

    def __radd__(self, other):
        return self + other

    def __mul__(self, other):
        if not np.isreal(other):
            return NotImplemented
        if other == 0:
            zero = Point2D(x=0, y=0)
            CircuitPerimeter(CyclicList([Segment(zero, zero) for _ in self]))
        return CircuitPerimeter(CyclicList([Segment(s.a * other, s.b * other) for s in self]))

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        if not np.isreal(other):
            return NotImplemented
        if other == 0:
            raise ZeroDivisionError
        return CircuitPerimeter(CyclicList([Segment(s.a / other, s.b / other) for s in self]))

    def __eq__(self, other):
        if not isinstance(other, CircuitPerimeter):
            return False
        return self.segments == other.segments


class Circuit:
    def __init__(self):
        self._section_list: List[Union[Straight, BezierTurn]] = []

    def length(self, samples=10):
        return np.sum(np.array([s.length() if isinstance(s, Straight) else s.length(samples)
                                for s in self._section_list]))

    def to_dicts(self) -> List[Dict[str, Union[str, list]]]:
        circuit = []
        for section in self._section_list:
            section_dict = {
                'type': 'Straight' if isinstance(section, Straight) else 'BezierTurn',
                'data': [[x.x, x.y] for x in [section.start, section.end]] if isinstance(section, Straight)
                else [[x.x, x.y] for x in [section.start, *section.control_points, section.end]]
            }
            circuit.append(section_dict)
        return circuit

    @staticmethod
    def from_dicts(section_list: List[Dict[str, Union[str, list]]]):
        c = Circuit()
        for section in section_list:
            data = section['data']
            if section['type'] == 'Straight':
                c._section_list.append(Straight(*[Point2D(*x) for x in data]))
            elif section['type'] == 'BezierTurn':
                c._section_list.append(BezierTurn(Point2D(*data[0]),
                                                  [Point2D(*p) for p in data[1:-1]],
                                                  Point2D(*data[-1])))
            else:
                raise NotImplementedError
        return c

    @staticmethod
    def from_objects(section_list: List[Union[Straight, BezierTurn]]):
        c = Circuit()
        assert (all(isinstance(section, Straight)
                    or isinstance(section, BezierTurn)
                    for section in section_list))
        c._section_list = section_list
        return c

    def __iter__(self):
        return iter(self._section_list)

    def __getitem__(self, item):
        return self._section_list[item]

    def to_perimeter(self, sample_rate: int = 10) -> CircuitPerimeter:
        sampled_circuit = CyclicList([])
        for section in self._section_list:
            section_length = section.length()
            samples = section.sample(max(int(section_length / sample_rate), 2))
            sampled_circuit.extend(samples[:-1])
        perimeter = CyclicList([])
        for i, point in enumerate(sampled_circuit):
            perimeter.append(Segment(point, sampled_circuit[i + 1]))
        return CircuitPerimeter(CyclicList(perimeter))
