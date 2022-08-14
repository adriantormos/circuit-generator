from unittest import TestCase

from datatypes.collections import CyclicList
from datatypes.geometry import Point2D, Vector2D

from circuit_generator.circuit import CircuitPerimeter
from circuit_generator.sections import Segment


class TestCircuitPerimeter(TestCase):
    def test_init(self):
        c = CircuitPerimeter([
            Segment(Point2D(0, 0), Point2D(300, 0)),
            Segment(Point2D(300, 0), Point2D(300, 300)),
            Segment(Point2D(300, 300), Point2D(0, 300)),
            Segment(Point2D(0, 300), Point2D(0, 0))
        ])
        self.assertEqual([type(c),
                          c.segments],
                         [CircuitPerimeter,
                          CyclicList([
                              Segment(Point2D(0, 0), Point2D(300, 0)),
                              Segment(Point2D(300, 0), Point2D(300, 300)),
                              Segment(Point2D(300, 300), Point2D(0, 300)),
                              Segment(Point2D(0, 300), Point2D(0, 0))
                          ])]
                         )

    def test_iter(self):
        c = CircuitPerimeter([
            Segment(Point2D(0, 0), Point2D(300, 0)),
            Segment(Point2D(300, 0), Point2D(300, 300)),
            Segment(Point2D(300, 300), Point2D(0, 300)),
            Segment(Point2D(0, 300), Point2D(0, 0))
        ])
        l = []
        for p in c:
            l.append(p)
        self.assertEqual(l, [Segment(Point2D(0, 0), Point2D(300, 0)), Segment(Point2D(300, 0), Point2D(300, 300)),
                             Segment(Point2D(300, 300), Point2D(0, 300)), Segment(Point2D(0, 300), Point2D(0, 0))])

    def test_add(self):
        c = CircuitPerimeter([
            Segment(Point2D(0, 0), Point2D(300, 0)),
            Segment(Point2D(300, 0), Point2D(300, 300)),
            Segment(Point2D(300, 300), Point2D(0, 300)),
            Segment(Point2D(0, 300), Point2D(0, 0))
        ])
        self.assertEqual(
            c+Vector2D(100, 50),
            CircuitPerimeter([Segment(Point2D(100, 50), Point2D(400, 50)), Segment(Point2D(400, 50), Point2D(400, 350)),
                              Segment(Point2D(400, 350), Point2D(100, 350)),
                              Segment(Point2D(100, 350), Point2D(100, 50))
                              ])
        )
        self.assertEqual(
            Vector2D(100, 50)+c,
            CircuitPerimeter([Segment(Point2D(100, 50), Point2D(400, 50)), Segment(Point2D(400, 50), Point2D(400, 350)),
                              Segment(Point2D(400, 350), Point2D(100, 350)),
                              Segment(Point2D(100, 350), Point2D(100, 50))
                              ])
        )

    def test_mul(self):
        c = CircuitPerimeter([
            Segment(Point2D(0, 0), Point2D(300, 0)),
            Segment(Point2D(300, 0), Point2D(300, 300)),
            Segment(Point2D(300, 300), Point2D(0, 300)),
            Segment(Point2D(0, 300), Point2D(0, 0))
        ])
        self.assertEqual(
            c*2,
            CircuitPerimeter([Segment(Point2D(0, 0), Point2D(600, 0)), Segment(Point2D(600, 0), Point2D(600, 600)),
                              Segment(Point2D(600, 600), Point2D(0, 600)), Segment(Point2D(0, 600), Point2D(0, 0))])
        )
        self.assertEqual(
            2*c,
            CircuitPerimeter([Segment(Point2D(0, 0), Point2D(600, 0)), Segment(Point2D(600, 0), Point2D(600, 600)),
                              Segment(Point2D(600, 600), Point2D(0, 600)), Segment(Point2D(0, 600), Point2D(0, 0))])
        )

    def test_div(self):
        c = CircuitPerimeter([
            Segment(Point2D(0, 0), Point2D(300, 0)),
            Segment(Point2D(300, 0), Point2D(300, 300)),
            Segment(Point2D(300, 300), Point2D(0, 300)),
            Segment(Point2D(0, 300), Point2D(0, 0))
        ])
        self.assertEqual(
            c/2,
            CircuitPerimeter([Segment(Point2D(0, 0), Point2D(150, 0)), Segment(Point2D(150, 0), Point2D(150, 150)),
                              Segment(Point2D(150, 150), Point2D(0, 150)), Segment(Point2D(0, 150), Point2D(0, 0))])
        )