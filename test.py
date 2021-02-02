from .core import Field, Core
from .structure import Point, GamePoint

field = Field.create_field(10, 10)
player = Field.add_player(self.field, 5)
points_1 = [
            Point(2, 3), Point(3, 2), Point(3 ,4), Point(4, 3)
]
points_2 = [
            Point(5, 3), Point(6, 4), Point(5, 5), Point(4, 5)
]

points_3 = [
            Point(6, 6), Point(6, 7), Point(5, 6), Point(5, 7),
            Point(4, 6), Point(4, 7), Point(3, 6), Point(3, 8),
            Point(2, 6), Point(2, 7), Point(2, 8),
]

def test_normal(self):
    for x, y in points_1:
           field.field[x][y].owner = 5

    loops = Core.find_all_new_loops(field, Point(4, 3), 5)
    field.empty_loops = {1: loops[0]}

    for x, y in points_2:
        self.field.field[x][y].owner = 5

    loops = Core.find_all_new_loops(field, Point(4, 5), 5)
    field.empty_loops[2] =  loops[0]

    for x, y in points_3:
        field.field[x][y].owner = 5

    loops = Core.find_all_new_loops(field, Point(2, 7), 5)
    print(loops)