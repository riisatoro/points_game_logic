
from dataclasses import asdict

from .structure import GamePoint, Point
from .core import Field


class GameFieldSerializer:
    def to_database(self, data):
        return asdict(data)

    def set_int_dict_keys(self, data):
        if data is None:
            return None
        tmp = {}
        for key, item in data.items():
            tmp[int(key)] = item
            if isinstance(item, list):
                tmp[int(key)] = [Point(x, y) for x, y in item]
            else:
                tmp[int(key)] = int(item)
        return tmp

    def from_database(self, data, height, width):
        field = data["field"]
        new_field = Field.create_field(height, width)
        for row_index, row in enumerate(field):
            for col_index, point in enumerate(row):
                owner = point.get("owner")
                if owner is not None:
                    owner = int(owner)
                captured = point.get("captured")
                if captured is not None:
                    captured = list(map(int, captured))
                new_field.field[row_index][col_index] = GamePoint(
                    owner=owner, captured=captured, border=point.get("border")
                )

        new_field.players = list(map(int, data.get("players")))
        new_field.loops = self.set_int_dict_keys(data.get("loops"))
        new_field.empty_loops = self.set_int_dict_keys(data.get("empty_loops"))
        new_field.score = self.set_int_dict_keys(data.get("score"))
        return new_field

    def to_client(self, data, pop_values: list = None):
        client_data = asdict(data)
        if pop_values:
            for key in pop_values:
                client_data.pop(key)
        return client_data
