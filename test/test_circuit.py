from unittest import TestCase

from datatypes.collections import CyclicList
from datatypes.geometry import Point2D

from circuit_generator.circuit import Circuit, CircuitPerimeter
from circuit_generator.sections import Straight, BezierTurn, Segment


class TestCircuit(TestCase):
    def test_init(self):
        c = Circuit()
        self.assertEqual([type(c), c._section_list], [Circuit, []])

    def test_from_dicts(self):
        c = Circuit.from_dicts([
            {'type': 'Straight', 'data': [[0, 100], [300, 200]]},
            {'type': 'BezierTurn', 'data': [[300, 200], [200, 300], [300, 500]]},
            {'type': 'Straight', 'data': [[300, 500], [300, 600]]}
        ])
        self.assertEqual(
            c._section_list,
            [Straight(Point2D(0, 100), Point2D(300, 200)),
             BezierTurn(Point2D(300, 200), [Point2D(200, 300)], Point2D(300, 500)),
             Straight(Point2D(300, 500), Point2D(300, 600))]
        )

    def test_from_objects(self):
        c = Circuit.from_objects([
            Straight(Point2D(0, 100), Point2D(300, 200)),
            BezierTurn(Point2D(300, 200), [Point2D(200, 300)], Point2D(300, 500)),
            Straight(Point2D(300, 500), Point2D(300, 600))
        ])
        self.assertEqual(
            c._section_list,
            [Straight(Point2D(0, 100), Point2D(300, 200)),
             BezierTurn(Point2D(300, 200), [Point2D(200, 300)], Point2D(300, 500)),
             Straight(Point2D(300, 500), Point2D(300, 600))]
        )

    def test_to_dicts(self):
        c = Circuit.from_objects([
            Straight(Point2D(0, 100), Point2D(300, 200)),
            BezierTurn(Point2D(300, 200), [Point2D(200, 300)], Point2D(300, 500)),
            Straight(Point2D(300, 500), Point2D(300, 600))
        ])
        self.assertEqual(
            c.to_dicts(),
            [{'type': 'Straight', 'data': [[0, 100], [300, 200]]},
             {'type': 'BezierTurn', 'data': [[300, 200], [200, 300], [300, 500]]},
             {'type': 'Straight', 'data': [[300, 500], [300, 600]]}]
        )

    def test_to_perimeter(self):
        c = Circuit.from_objects([
            Straight(Point2D(0, 100), Point2D(300, 200)),
            BezierTurn(Point2D(300, 200), [Point2D(200, 300)], Point2D(300, 500)),
            Straight(Point2D(300, 500), Point2D(300, 600))
        ])
        points = CyclicList([
            s
            for section in c._section_list
            for s in section.sample(max(int(section.length() / 10), 2))[:-1]
        ])
        segments = CircuitPerimeter(CyclicList([Segment(points[i], points[i+1]) for i, _ in enumerate(points)]))
        self.assertEqual(
            c.to_perimeter(),
            segments
        )

    def test_length(self):
        s1 = Straight(Point2D(0, 100), Point2D(300, 200))
        s2 = BezierTurn(Point2D(300, 200), [Point2D(200, 300)], Point2D(300, 500))
        s3 = Straight(Point2D(300, 500), Point2D(300, 600))
        c = Circuit.from_objects([s1, s2, s3])
        self.assertEqual(
            [c.length(10), c.length(25), c.length(50)],
            [s1.length() + s2.length(10) + s3.length(),
             s1.length() + s2.length(25) + s3.length(),
             s1.length() + s2.length(50) + s3.length()]
        )
