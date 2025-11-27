class Drone:
    def __init__(self, name: str = "Drone1", starting_position=[0, 0, 0]) -> None:

        self.name: str = name

        self.power: bool = False

        self.LED = (0, 0, 0)

        self.position = [0, 0, 0]  # Drone position and orientation
        self.orientation = [0, 0, 0]  # [pitch, yaw, roll]

    def TogglePower(self) -> None:
        self.power = not self.power


# @TODO - Add more functions
# @TODO - Add pygame clock and use that to limit movement