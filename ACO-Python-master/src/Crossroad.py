class Crossroad:

    def __init__(self, position, steps):
        self.position = position
        self.steps = steps

    def get_position(self):
        return self.position

    def get_steps(self):
        return self.steps

    def increase_step(self):
        self.steps += 1
        return self
