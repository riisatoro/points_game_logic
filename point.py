class Point():
    def __init__(self, color):
        self.color = color
        self.part_of_loop = False
        self.loop_id = []
        self.captured = False

    def is_free(self):
        return self.captured and self.part_of_loop

    def __str__(self):
        return f"{self.color}|loop: {self.part_of_loop}|captured: {self.captured}"

    def __eq__(self, color:str):
        return self.color == color

    def __ne__(self, color:str):
        return not self.color == color
