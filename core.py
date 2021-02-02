from shapely.geometry import Point as shapePoint
from shapely.geometry import Polygon as shapePolygon
from .structure import Point, GamePoint, GameField

min_field_size = 5

DFS_WHITE = "WHITE"
DFS_GRAY = "GRAY"
DFS_BLACK = "BLACK"


class Field:
    @staticmethod
    def create_field(height: int, width: int) -> GameField:
        if height < min_field_size or width < min_field_size:
            raise ValueError("Field height or width must be bigger than 5")

        field = []
        border = [GamePoint(border=True)] * (width + 2)

        field.append(border)
        for _ in range(height):
            tmp_row = []
            for j in range(width+2):
                if j < 1 or j == width+1:
                    tmp_row.append(GamePoint(border=True))
                else:
                    tmp_row.append(GamePoint())
            field.append(tmp_row)
        field.append(border)

        return GameField(field)

    @staticmethod
    def add_player(field: GameField, player: int) -> GameField:
        if field.players:
            if player not in field.players:
                field.players.append(player)
        else:
            field.players = [player]

        field = Field.add_player_to_score(field, player)
        return field

    @staticmethod
    def add_player_to_score(field: GameField, player: int):
        if not field.players or player not in field.players:
            raise ValueError("Can't add player to the score table - invalid player ID")

        if field.score:
            field.score[player] = 0
        else:
            field.score = {player: 0}
        return field

    @staticmethod
    def change_owner(field: GameField, point: Point, owner: int):
        x, y = point

        if owner not in field.players:
            raise ValueError("Player ID is not in the GameField")

        if field.field[x][y].owner is None and not field.field[x][y].border and not field.field[x][y].captured:
            field.field[x][y].owner = owner

        return field

    @staticmethod
    def is_full_field(field: GameField):
        for row in field.field:
            for point in row:
                if point.owner is None and point.captured is None and not point.border:
                    return False
        return True

    @staticmethod
    def add_loop(field_loops, loop: [Point]):
        if not field_loops:
            return {1: loop}

        for key, item in field_loops.items():
            if set(item).issubset(set(loop)):
                return field_loops
            if set(loop).issubset(set(item)):
                field_loops[key] = loop
                return field_loops

        field_loops[max(field_loops.keys())+1] = loop
        return field_loops

import time
class Core:
    @staticmethod
    def player_set_point(field: GameField, point: Point, owner: int):
        start_time = time.time()
        field = Field.change_owner(field, point, owner)
        print("--- %s seconds on change_owner() ---" % (time.time() - start_time))

        start_time = time.time()
        loops = Core.find_all_new_loops(field, point, owner)
        print("--- %s seconds on find_all_new_loops() ---" % (time.time() - start_time))

        start_time = time.time()
        field = Core.add_loops_and_capture_points(field, loops, owner)
        print("--- %s seconds on add_loops_and_capture_points() ---" % (time.time() - start_time))
        
        start_time = time.time()
        empty_loop_id = Core.is_point_in_empty_loop(field, point)
        print("--- %s seconds on is_point_in_empty_loop() ---" % (time.time() - start_time))

        if not loops and empty_loop_id:
            start_time = time.time()
            loop = field.empty_loops.pop(empty_loop_id)
            x, y = loop[0]
            owner = field.field[x][y].owner

            field = Core.add_loops_and_capture_points(field, [loop], owner)
            print("--- %s seconds when point is empty loop ---" % (time.time() - start_time))

        return field

    @staticmethod
    def is_neighbour(point_1, point_2):
        equals = point_1 == point_2
        horisontal = abs(point_1[0] - point_2[0]) < 2
        vertical = abs(point_1[1] - point_2[1]) < 2
        diagonal = (horisontal - vertical) <= 2
        return not equals and horisontal and vertical and diagonal

    @staticmethod
    def find_loop_in_path(path):
        indexes = []
        if len(path) > 3:
            for i in range(0, len(path)-3):
                if Core.is_neighbour(path[i], path[-1]):
                    indexes.append(i)
        return indexes

    @staticmethod
    def append_new_loop(pathes, loops):
        set_of_path = set(pathes)
        for index, item in enumerate(loops):
            set_of_item = set(item)
            if set_of_path.issubset(set_of_item):
                loops[index] = pathes.copy()

        loops.append(pathes.copy())
        return True

    @staticmethod
    def get_loops_from_path(path, loops):
        set_of_loops = list(map(set, loops))
        for i in range(0, len(path)-3):
            if Core.is_neighbour(path[i], path[-1]):
                for points_set in set_of_loops:
                    if points_set.issubset(set(path[i:])):
                        return
                else:
                    loops.append(path[i:].copy())

    @staticmethod
    def filter_only_new_loops(loops, captured_loops, empty_loops):
        for index, loop in enumerate(loops):
            if not loops:
                return
            loop_set = set(loop)
            for captured in captured_loops:
                if captured.issubser(loop_set):
                    loops.pop(index)
                    break
        
            for empty in empty_loops:
                if empty.issubset(loop_set):
                    loops.pop(index)
                    break

    @staticmethod
    def filter_has_points_to_capture(field, loops, owner):
        for index, loop in enumerate(loops):
            point = loop[0]
            for loop_point in loop:
                if not Core.is_neighbour(point, loop_point):
                    break
            else:
                loops.pop(index)
                

    @staticmethod
    def dfs(field, captured_loops, empty_loops, point, path, loops, owner):
        x, y = point
        surrounded_points = [
            Point(i, j) 
            for i in range(x-1, x+2) 
            for j in range(y-1, y+2) 
            if Point(i, j) != point
                and Point(i, j) not in path
                and not field[i][j].border
                and field[i][j].owner == owner
                and field[i][j].captured == None
        ]

        path.append(point)
        if len(path) > 3 and shapePolygon(path).area > 1.0:
            Core.get_loops_from_path(path, loops)
            Core.filter_only_new_loops(loops, captured_loops, empty_loops)


        # loops.append(path.copy())
        
        for next_point in surrounded_points:
            Core.dfs(field, captured_loops, empty_loops, next_point, path, loops, owner)
            path.pop()

        """
        for i, j in surrounded_points:
            new_point = Point(i, j)
            if point != new_point and not field[i][j].border and field[i][j].owner == owner and new_point not in path and field[i][j].captured is None:
                path.append(new_point)
                loop_indexes = Core.find_loop_in_path(path)
                for index in loop_indexes:
                    if index != 0 and captured_loops is not None:
                        if set(path[index:]) in list(map(set, captured_loops.values())) or set(path[index:]) in list(map(set, empty_loops.values())):
                            return path[index+1]
                    
                    if len(path) > 3 and Core.is_neighbour(path[0], path[-1]):
                        loops.append(path.copy())

                return_to = Core.dfs(field, captured_loops, empty_loops, new_point, path, loops, owner)
                path.pop()

                if return_to is not None and return_to != path[-1]:
                    return return_to
        """

    @staticmethod
    def find_all_new_loops(field, point, owner):
        x, y = point
        surrounded_points = [
            Point(i, j) 
            for i in range(x-1, x+2) 
            for j in range(y-1, y+2) 
            if Point(i, j) != point
                and not field.field[i][j].border
                and field.field[i][j].owner == owner
                and field.field[i][j].captured == None
        ]
        if len(surrounded_points) < 2:
            return []

        path, loops = [], []
        
        captured_loops = []
        empty_loops = []
        if field.loops:
            captured_loops = list(map(set, field.loops.values()))
        if field.empty_loops:
            empty_loops = list(map(set, field.empty_loops.values()))
        print(captured_loops, empty_loops)
        
        Core.dfs(field.field, captured_loops, empty_loops, point, path, loops, owner)
        return loops

    @staticmethod
    def find_enemy_captured(field, points, owner):
        if len(points) == 0:
            return False
        for x, y in points:
            point = field.field[x][y]
            if not point.border and point.owner is not None and point.owner != owner:
                if point.captured is None or point.captured[-1] != owner:
                    return True
        return False

    @staticmethod
    def only_empty_captured(field, loop):
        for x, y in loop:
            if field[x][y].owner is not None:
                return False
        return True

    @staticmethod
    def is_empty_loop(field, captured):
        for x, y in captured:
            if field[x][y].owner is not None:
                return False
        return True

    @staticmethod
    def add_loops_and_capture_points(field, loops, owner):
        for loop in loops:
            captured = Core.find_all_captured_points(field, loop, owner)
            if not captured:
                continue

            if Core.find_enemy_captured(field, captured, owner):
                field.loops = Field.add_loop(field.loops, loop)
                field = Core.set_captured_points(field, captured, owner)
                field = Core.calc_score(field)
            else:
                if Core.is_empty_loop(field.field, captured):
                    field.empty_loops = Field.add_loop(field.empty_loops, loop)

        return field

    @staticmethod
    def find_all_captured_points(field: GameField, loop: [Point], owner: int):
        polygon = shapePolygon(loop)
        captured = []

        for x in range(1, len(field.field)-1):
            for y in range(1, len(field.field[0])-1):
                if field.field[x][y].owner != owner or (field.field[x][y].owner == owner and field.field[x][y].captured is not None):
                    if polygon.contains(shapePoint(x, y)):
                        captured.append(Point(x, y))
        return captured

    @staticmethod
    def is_point_in_empty_loop(field: GameField, point: Point):
        loop_id = False
        empty_loops = field.empty_loops

        if not empty_loops:
            return loop_id

        for key, loop in empty_loops.items():
            polygon = shapePolygon(loop)
            if polygon.contains(shapePoint(point)):
                if loop_id:
                    if len(loop) < len(empty_loops[loop_id]):
                        loop_id = key
                else:
                    loop_id = key
        return loop_id

    @staticmethod
    def calc_score(field: GameField):
        score = {}
        for player in field.players:
            score[player] = 0

        for row in field.field:
            for point in row:
                if point.captured and point.owner != point.captured[-1] and point.owner is not None:
                    score[point.captured[-1]] += 1

        field.score = score
        return field

    @staticmethod
    def set_captured_points(field: GameField, points: [Point], owner: int):
        for x, y in points:
            if field.field[x][y].captured is not None:
                field.field[x][y].captured.append(owner)
            else:
                field.field[x][y].captured = [owner]
        return field

    @staticmethod
    def is_loop_already_found(field: GameField, loop: [Point]):
        loop_size = len(loop)
        loop_set = set(loop)

        loops = field.empty_loops
        if loops:
            for _, item in loops.items():
                if loop_set == set(item) or set(item).issubset(loop_set) or len(item) == loop_size:
                    return True

        loops = field.loops
        if loops:
            for _, item in loops.items():
                if set(item).issubset(loop_set) or len(item) == loop_size or loop_set == set(item):
                    return True

        return False
