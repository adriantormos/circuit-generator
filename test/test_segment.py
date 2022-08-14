from math import sqrt
from unittest import TestCase
from datatypes.geometry import Point2D

from circuit_generator.sections import Segment


class TestSegment(TestCase):
    def test_init(self):
        s = Segment(Point2D(0, 100), Point2D(300, 200))
        self.assertEqual([type(s), s.a, s.b], [Segment, Point2D(0, 100), Point2D(300, 200)])

    def test_length(self):
        s = Segment(Point2D(0, 100), Point2D(300, 200))
        self.assertEqual(s.length(), sqrt(100000))

    def test_intersects_with(self):
        s = Segment(Point2D(0, 100), Point2D(300, 200))
        t = Segment(Point2D(300, 100), Point2D(0, 200))
        u = Segment(Point2D(300, 100), Point2D(600, 200))
        self.assertEqual(s.intersects_with(s), False)
        self.assertEqual(s.intersects_with(t), True)
        self.assertEqual(s.intersects_with(u), False)

    def test_intersection(self):
        s = Segment(Point2D(0, 0), Point2D(300, 300))
        t = Segment(Point2D(300, 0), Point2D(0, 300))
        u = Segment(Point2D(300, 300), Point2D(600, 600))
        self.assertEqual(s.intersection(s), None)
        self.assertEqual(s.intersection(t), Point2D(150, 150))
        self.assertEqual(s.intersection(u), None)
