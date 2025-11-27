class Mapping:
    def __init__(self, b1: int, b2: int, b3: int, b4: int, l1: int, r1: int, lb: int, rb: int, back: int, start: int,
                 home: int, dUp: int, dDown: int, dLeft: int, dRight: int):

        self.btnMapping = {
            "BTN1": b1,
            "BTN2": b2,
            "BTN3": b3,
            "BTN4": b4,
            "BTNL1": l1,
            "BTNR1": r1,
            "BTNLB": lb,
            "BTNRB": rb,
            "BTNBACK": back,
            "BTNSTART": start,
            "BTNHOME": home,
            "BTNDUP": dUp,
            "BTNDOWN": dDown,
            "BTNDLEFT": dLeft,
            "BTNDRIGHT": dRight
        }

# @TODO - Consider adding axis and hats