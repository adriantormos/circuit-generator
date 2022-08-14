from math import sqrt
from unittest import TestCase
from datatypes.geometry import Point2D, Vector2D

from circuit_generator.sections import BezierTurn


class TestBezierTurn(TestCase):
    def test_init(self):
        t = BezierTurn(Point2D(0, 100), [Point2D(100, 200)], Point2D(300, 200))
        self.assertEqual([type(t), t.start, t.control_points, t.end, t.degree],
                         [BezierTurn, Point2D(0, 100), [Point2D(100, 200)], Point2D(300, 200), 2])

    def test_sample(self):
        t = BezierTurn(Point2D(0, 100), [Point2D(100, 200)], Point2D(300, 200))
        self.assertEqual(
            t.sample(5),
            [Point2D(0, 100),
             Point2D(0.75*50 + 0.25*75, 0.75*75 + 75 + 0.25*50),
             Point2D(125, 175),
             Point2D(0.75*50 + 0.75*225, 0.25*25 + 75 + 0.75*150),
             Point2D(300, 200)]
        )

    def test_length(self):
        t = BezierTurn(Point2D(0, 100), [Point2D(100, 200)], Point2D(300, 200))
        samples = [Point2D(0, 100), Point2D(0.75*50 + 0.25*75, 0.75*75 + 75 + 0.25*50), Point2D(125, 175),
                   Point2D(0.75*50 + 0.75*225, 0.25*25 + 75 + 0.75*150), Point2D(300, 200)]
        self.assertEqual(t.length(samples=5),
                         sum((samples[i+1]-samples[i]).length() for i in range(4)))

    def test_directions(self):
        t = BezierTurn(Point2D(0, 100), [Point2D(100, 200)], Point2D(300, 200))
        self.assertEqual([t.first_direction(), t.last_direction()],
                         [Vector2D(100, 100), Vector2D(200, 0)])

    def test_eq(self):
        t = BezierTurn(Point2D(0, 100), [Point2D(100, 200)], Point2D(300, 200))
        u = BezierTurn(Point2D(0, 100), [Point2D(100, 200)], Point2D(300, 200))
        v = BezierTurn(Point2D(0, 100), [Point2D(0, 200)], Point2D(300, 200))
        w = BezierTurn(Point2D(300, 100), [Point2D(100, 200)], Point2D(300, 200))
        x = BezierTurn(Point2D(0, 100), [Point2D(100, 200), Point2D(100, 200)], Point2D(300, 200))
        self.assertEqual(t == u, True)
        self.assertEqual(t == v, False)
        self.assertEqual(t == w, False)
        self.assertEqual(t == x, False)
