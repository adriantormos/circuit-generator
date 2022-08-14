from functools import lru_cache
from math import factorial
from typing import List, Optional, Tuple

from datatypes.geometry import Point2D, Vector2DCartesian
import numpy as np


class Straight:
    def __init__(self, start: Point2D, end: Point2D):
        self.start = start
        self.end = end

    def interpolate(self, ratio: float) -> Point2D:
        return Point2D((1 - ratio) * self.start.x + ratio * self.end.x,
                       (1 - ratio) * self.start.y + ratio * self.end.y)

    def length(self) -> float: return (self.end - self.start).length()

    def sample(self, amount_of_points: int) -> List[Point2D]:
        assert amount_of_points > 0
        return [self.interpolate(t) for t in np.linspace(0, 1, amount_of_points)]

    def __eq__(self, other):
        if not isinstance(other, Straight):
            return False
        return self.start == other.start and self.end == other.end


@lru_cache(maxsize=64)
def binomial(n, k): return factorial(n) / (factorial(k) * factorial(n - k))


class BezierTurn:
    def __init__(self, start: Point2D, control_points: List[Point2D], end: Point2D):
        self.start = start
        self.control_points = control_points
        self.end = end
        self.degree = len(control_points) + 1

    def curve(self, t):
        return (
                (1 - t) ** self.degree * self.start
                + sum([binomial(self.degree, i) * (1 - t) ** (self.degree - i) * t ** i * c
                       for i, c in enumerate(self.control_points, start=1)],
                      Point2D(0, 0))
                + t ** self.degree * self.end
        )

    def sample(self, amount_of_points: int) -> List[Point2D]:
        assert amount_of_points > 1
        return [self.curve(t) for t in np.linspace(0, 1, amount_of_points)]

    def length(self, samples=20):
        assert samples > 1
        points = self.sample(samples)
        return sum((points[i + 1] - p).to_polar().length() for i, p in enumerate(points[:-1]))

    def first_direction(self):
        return self.control_points[0] - self.start

    def last_direction(self):
        return self.end - self.control_points[-1]

    def __eq__(self, other):
        if not isinstance(other, BezierTurn):
            return False
        return self.start == other.start and self.end == other.end \
            and len(self.control_points) == len(other.control_points) \
            and all(x == y for x, y in zip(self.control_points, other.control_points))


class Segment:
    __slots__ = ['a', 'b']

    def __init__(self, a: Point2D, b: Point2D):
        self.a: Point2D
        self.b: Point2D
        assert isinstance(a, Point2D)
        assert isinstance(b, Point2D)
        object.__setattr__(self, 'a', a)
        object.__setattr__(self, 'b', b)

    def length(self) -> float:
        return (self.b - self.a).length()

    def _get_intersection_vectors(self, other) -> Tuple[Vector2DCartesian, Vector2DCartesian]:
        if not isinstance(other, Segment):
            raise ValueError('Parameter must be a Segment.')
        return (self.b - self.a).to_cartesian(), (other.b - other.a).to_cartesian()

    def intersects_with(self, other) -> bool:
        v1, v2 = self._get_intersection_vectors(other)
        denom: float = v1.y * v2.x - v1.x * v2.y
        if denom == 0:
            return False
        numer: float = v1.x * (other.a.y - self.a.y) - v1.y * (other.a.x - self.a.x)
        u: float = numer / denom
        t: float = (u * v2.x + other.a.x - self.a.x) / v1.x
        return 0 < u < 1 and 0 < t < 1

    def intersection(self, other) -> Optional[Point2D]:
        v1, v2 = self._get_intersection_vectors(other)
        denom: float = v1.y * v2.x - v1.x * v2.y
        if denom == 0:
            return None
        numer: float = v1.x * (other.a.y - self.a.y) - v1.y * (other.a.x - self.a.x)
        u: float = numer / denom
        t: float = (u * v2.x + other.a.x - self.a.x) / v1.x
        if 0 < u < 1 and 0 < t < 1:
            return other.a + u * v2
        return None

    def __eq__(self, other):
        if not isinstance(other, Segment):
            return False
        return self.a == other.a and self.b == other.b

    def __setattr__(self, key, value):
        raise TypeError('Segment object is immutable.')

    def __repr__(self):
        return f'{self.a}->{self.b}'

    def __str__(self):
        return self.__repr__()
