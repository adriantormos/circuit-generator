from math import sqrt
from unittest import TestCase
from datatypes.geometry import Point2D

from circuit_generator.sections import Straight


class TestStraight(TestCase):
    def test_init(self):
        s = Straight(Point2D(0, 100), Point2D(300, 200))
        self.assertEqual([type(s), s.start, s.end], [Straight, Point2D(0, 100), Point2D(300, 200)])

    def test_interpolate(self):
        s = Straight(Point2D(0, 100), Point2D(300, 200))
        self.assertEqual(s.interpolate(0.0), Point2D(0, 100))
        self.assertEqual(s.interpolate(0.4), Point2D(120, 140))
        self.assertEqual(s.interpolate(1.0), Point2D(300, 200))

    def test_length(self):
        s = Straight(Point2D(0, 100), Point2D(300, 200))
        self.assertEqual(s.length(), sqrt(100000))

    def test_sample(self):
        s = Straight(Point2D(0, 100), Point2D(300, 200))
        self.assertEqual(s.sample(5), [Point2D(300*t, 100+100*t) for t in [0, 0.25, 0.5, 0.75, 1]])

    def test_eq(self):
        s = Straight(Point2D(0, 100), Point2D(300, 200))
        t = Straight(Point2D(0, 100), Point2D(300, 200))
        u = Straight(Point2D(0, 600), Point2D(300, 200))
        self.assertEqual(s == t, True)
        self.assertEqual(s == u, False)
