import random
from math import tau
from typing import Optional, List, Union

from datatypes.geometry import Point2D, Vector2D

from circuit_generator.circuit import Circuit
from circuit_generator.sections import Straight, BezierTurn


def displace(point: Point2D, max_radius: float):
    displacement_vector = Vector2D(r=max_radius * random.random(), t=random.uniform(0, tau))
    return point + displacement_vector


class CircuitGenerator:
    def __init__(self,
                 coordinate_range=(-500, 500, -500, 500), n_points=(9, 12),
                 minimum_distance_between_points=60, chicane_threshold=60,
                 straight_threshold=(200, 500), short_straight_probability=0.15,
                 small_angle_threshold=0.436, consecutive_turns_maximum=3, radius_ranges=(0.8, 0.9, 0.1, 0.25),
                 cubic_turn_probability=0.4, turn_displacement_ranges=(0.3, 0.4), minimum_control_point_ratio=0.5,
                 track_width=15
                 ):
        # Coordinate range for initial points
        self.X_MIN, self.X_MAX, self.Y_MIN, self.Y_MAX = coordinate_range
        # Amount of generated points
        self.POINTS_MIN, self.POINTS_MAX = n_points
        # Below these distances, respectively, there can
        # not exist a segment and a segment will always
        # be a straight to avoid weird, very small curves
        self.INTERPOINT_THRESHOLD, self.CHICANE_THRESHOLD = minimum_distance_between_points, chicane_threshold
        # Minimum distance for a short straight, and probability of becoming one
        self.SHORT_STRAIGHT_THRESHOLD, self.SS_PROBABILITY = straight_threshold[0], short_straight_probability
        # Minimum distance for a long straight
        self.LONG_STRAIGHT_THRESHOLD = straight_threshold[1]
        # Maximum angle (radians) to be considered a small one
        self.SMALL_ANGLE_THRESHOLD = small_angle_threshold
        # Maximum amount of consecutive turns
        # (tries to avoid Bézier curves going crazy when a lot
        # of them go one after another)
        self.MAX_CONSECUTIVE_TURNS = consecutive_turns_maximum
        # Relative range to create a radius after a straight
        # (SSR = turn start; SER = turn end)
        self.SSR_MIN, self.SSR_MAX, self.SER_MIN, self.SER_MAX = radius_ranges
        # Probability that the turn will have two control points
        self.CUBIC_TURN_PROBABILITY = cubic_turn_probability
        # Turn displacement ratio (with respect to segment length) interval
        self.TDR_MIN, self.TDR_MAX = turn_displacement_ranges
        # Minimum ratio for control point position when correcting flow
        self.CP_RATIO_MIN = minimum_control_point_ratio
        # Distance from exterior to interior limit of the track
        self.TRACK_WIDTH = track_width

        self._last_layout: Optional[Circuit] = None

    def generate_layout(self):
        points = self._generate_random_points()
        points = self._order_points_by_angle(points)
        points = self._correct_very_small_angles(points)
        circuit = self._detect_straights(points)
        circuit = self._avoid_too_many_consecutive_turns(circuit)
        circuit = self._create_turns_after_straights(circuit)
        circuit = self._create_turns(circuit)
        circuit = self._correct_circuit_flow(circuit)
        self._last_layout = Circuit.from_objects(circuit)
        return circuit

    def _generate_random_points(self) -> List[Point2D]:
        """
        Generate a list of random points
        """
        points_amount = random.randint(self.POINTS_MIN, self.POINTS_MAX)
        return [Point2D(random.randint(self.X_MIN, self.X_MAX),
                        random.randint(self.Y_MIN, self.Y_MAX))
                for _ in range(points_amount)]

    def _order_points_by_angle(self, points: List[Point2D]) -> List[Point2D]:
        angles_to_origin = [Vector2D(x=p.x, y=p.y).to_polar().t for p in points]
        sort_mapping = {(p.x, p.y): angles_to_origin[i] for i, p in enumerate(points)}
        return sorted(points, key=lambda p: sort_mapping[(p.x, p.y)])

    def _correct_very_small_angles(self, points: List[Point2D]) -> List[Point2D]:
        def correct_small_angle_sequence(sequence: List[Point2D]):
            pointer = 0
            while pointer + 1 < len(sequence):
                sequence[0], sequence[1] = sequence[1], sequence[0]
                pointer += 2
            return sequence

        circuit = []
        small_angle_sequence = []
        for i in range(len(points)):
            previous_point = points[(i - 1) % len(points)]
            point = points[i]
            next_point = points[(i + 1) % len(points)]

            v1, v2 = previous_point - point, next_point - point
            angle = v1.angle_with(v2)
            small_angle_sequence.append(point)

            if angle > self.SMALL_ANGLE_THRESHOLD and len(small_angle_sequence) == 1:
                circuit.extend(small_angle_sequence)
                small_angle_sequence = []
            elif angle > self.SMALL_ANGLE_THRESHOLD:
                small_angle_sequence = correct_small_angle_sequence(small_angle_sequence)
                circuit.extend(small_angle_sequence)
                # circuit.append(point)
                small_angle_sequence = []
            else:
                pass

        return circuit

    def _detect_straights(self, points: List[Point2D]) -> List[Union[Straight, Point2D]]:
        circuit = []

        for i, point in enumerate(points):
            next_point = points[(i + 1) % len(points)]
            section_distance = (next_point - point).length()

            if section_distance > self.LONG_STRAIGHT_THRESHOLD \
                    or section_distance > self.SHORT_STRAIGHT_THRESHOLD and random.random() < self.SS_PROBABILITY \
                    or section_distance < self.CHICANE_THRESHOLD:
                circuit.append(Straight(point, next_point))
            else:
                circuit.append(point)

        return circuit

    def _avoid_too_many_consecutive_turns(self, section_list: List[Union[Straight, Point2D]]) \
            -> List[Union[Straight, Point2D]]:
        section_pointer, turn_counter = 0, 0
        while True:
            section = section_list[section_pointer % len(section_list)]
            if isinstance(section, Straight):
                turn_counter = 0
            else:
                turn_counter += 1
            if turn_counter > self.MAX_CONSECUTIVE_TURNS:
                next_section = section_list[(section_pointer + 1) % len(section_list)]
                section_list[section_pointer % len(section_list)] = \
                    Straight(section,
                             next_section if isinstance(next_section, Point2D) else next_section.start)
                turn_counter = 0

            section_pointer += 1
            if section_pointer > len(section_list) and turn_counter == 0:
                break

        return section_list

    def _create_turns_after_straights(self, section_list: List[Union[Straight, Point2D]]) \
            -> List[Union[Straight, BezierTurn, Point2D]]:
        circuit = []

        for i in range(len(section_list)):
            previous_section = section_list[(i - 1) % len(section_list)]
            section = section_list[i]
            next_section = section_list[(i + 1) % len(section_list)]
            # If section after a straight
            if isinstance(previous_section, Straight):
                # Create a bezier turn in the end vertex of the straight
                turn_start = previous_section.interpolate(random.uniform(self.SSR_MIN, self.SSR_MAX))
                turn_end = Straight(
                    section if isinstance(section, Point2D) else section.start,
                    next_section if isinstance(next_section, Point2D) else next_section.start
                ).interpolate(random.uniform(self.SER_MIN, self.SER_MAX))
                circuit.append(BezierTurn(
                    turn_start,
                    # TODO: Displace control point by a maximum of SR_DISPLACEMENT_MAX
                    [section if isinstance(section, Point2D) else section.start],
                    turn_end
                ))
                previous_section.end = turn_start
                if isinstance(section, Point2D):
                    section = turn_end
                else:
                    section.start = turn_end
                circuit.append(section)
            else:
                circuit.append(section)

        return circuit

    def _create_turns(self, section_list: List[Union[Straight, BezierTurn, Point2D]]) \
            -> List[Union[Straight, BezierTurn]]:
        circuit = []

        for i, section in enumerate(section_list):
            next_section = section_list[(i + 1) % len(section_list)]
            if isinstance(section, Point2D):
                turn_start = section
                turn_end = next_section if isinstance(next_section, Point2D) else next_section.start
                aux_straight = Straight(turn_start, turn_end)
                if random.random() < self.CUBIC_TURN_PROBABILITY:
                    circuit.append(BezierTurn(
                        turn_start,
                        [displace(aux_straight.interpolate(1 / 3),
                                  aux_straight.length() * random.uniform(self.TDR_MIN, self.TDR_MAX)),
                         displace(aux_straight.interpolate(2 / 3),
                                  aux_straight.length() * random.uniform(self.TDR_MIN, self.TDR_MAX))],
                        turn_end
                    ))
                else:
                    circuit.append(BezierTurn(
                        turn_start,
                        [displace(aux_straight.interpolate(1 / 2),
                                  aux_straight.length() * random.uniform(self.TDR_MIN, self.TDR_MAX))],
                        turn_end
                    ))
            else:
                circuit.append(section)

        return circuit

    def _correct_circuit_flow(self, section_list: List[Union[Straight, BezierTurn]]):
        circuit = []

        for i, section in enumerate(section_list):
            previous_section = section_list[(i - 1) % len(section_list)]
            # Only correct flow of turns preceded by turns
            if isinstance(previous_section, BezierTurn) and isinstance(section, BezierTurn):
                section.control_points[0] = \
                    section.start + previous_section.last_direction() * random.uniform(self.CP_RATIO_MIN, 1)
            elif isinstance(section, Straight) \
                    and section.length() > self.SHORT_STRAIGHT_THRESHOLD \
                    and isinstance(previous_section, BezierTurn):
                turn_start = Straight(
                    previous_section.control_points[-1], previous_section.end
                ).interpolate(random.uniform(self.SSR_MIN * self.SSR_MIN, self.SSR_MAX * self.SSR_MAX))
                turn_end = section.interpolate(random.uniform(self.SER_MIN, self.SER_MAX))
                circuit.append(BezierTurn(turn_start, [section.start], turn_end))
                previous_section.end = turn_start
                section.start = turn_end
            circuit.append(section)

        return circuit
