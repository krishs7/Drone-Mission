from pygame.joystick import Joystick
import pygame
import Consts
import ControllerMapping


class ControllerUtils:
    CONTROLLER_COUNT = 0

    consts = Consts.Consts()

    if consts.DRIFT_VAL >= 1 or consts.DRIFT_VAL < 0:
        print("Error - DRIFT_VAl is out of bounds\nAborting...")
        exit(1)

    def getController(self) -> Joystick:
        print("Initializing Controller Check")

        pygame.joystick.init()

        totalJoysticks = pygame.joystick.get_count()

        ctr: Joystick = None 
        if totalJoysticks == 0:
            ctr = self.__reconnectJoystick()
        elif totalJoysticks > 1:
            ctr = self.__selectController(self.__getAllControllers())
        else:
            ctr = pygame.joystick.Joystick(0)

        self.CONTROLLER_COUNT = pygame.joystick.get_count()
        self.__assigningButtonMappings(ctr.get_name())

        print("The following Controller has been selected")
        self.__displayControllerInfo(ctr)
        print("The Controller is ready!")

        return ctr

    def __assigningButtonMappings(self, name: str):
        print("Attempting to map buttons to " + name + "...")
        if name == "Controller (XBOX 360 For Windows)":
            self.__mapXBOX360()
        elif name == "PS4 Controller":
            self.__mapPS4()
        else:
            print("WARNING - " + name + " is not recognized\nUsing default mapping...")
            self.__mapXBOX360()

    def __mapPS4(self):
        BTN1 = 2  # Square
        BTN2 = 0  # X
        BTN3 = 3  # Triangle
        BTN4 = 1  # Circle

        BTNL1 = 9
        BTNR1 = 10
        BTNLB = 7
        BTNRB = 8

        BTNBACK = 4
        BTNSTART = 6
        BTNHOME = 5

        BTNDUP = 11
        BTNDDOWN = 12
        BTNDLEFT = 13
        BTNDRIGHT = 14

        self.MAP = ControllerMapping.Mapping(BTN1, BTN2, BTN3, BTN4, BTNL1, BTNR1, BTNLB, BTNRB, BTNBACK, BTNSTART, BTNHOME, BTNDUP,
                           BTNDDOWN, BTNDLEFT, BTNDRIGHT)

    def __mapXBOX360(self):
        BTN1 = 2  # X
        BTN2 = 0  # A
        BTN3 = 3  # Y
        BTN4 = 1  # B

        BTNL1 = 4
        BTNR1 = 5
        BTNLB = 8
        BTNRB = 9

        BTNBACK = 6
        BTNSTART = 7
        BTNHOME = 10

        BTNDUP = -1
        BTNDDOWN = -1
        BTNDLEFT = -1
        BTNDRIGHT = -1

        self.MAP = ControllerMapping.Mapping(BTN1, BTN2, BTN3, BTN4, BTNL1, BTNR1, BTNLB, BTNRB, BTNBACK, BTNSTART, BTNHOME, BTNDUP,
                           BTNDDOWN, BTNDLEFT, BTNDRIGHT)

    def __reconnectJoystick(self) -> Joystick:
        if pygame.joystick.get_count() == 0:
            print("\tConnection Error - No Connected Joysticks Found")
            i = 0
            while pygame.joystick.get_count() == 0:
                pygame.joystick.quit()
                pygame.joystick.init()
                pygame.time.wait(1000)
                print(self.__connectionMsg(0, i))
                i = self.__messageInfo(i)
            if pygame.joystick.get_count() > 0:
                print("\tConnection found!")
                pygame.joystick.init() 
                return pygame.joystick.Joystick

    def __selectController(self, controllers: list) -> Joystick:
        print("Several Controllers Detected")
        for ctr in controllers:
            self.__displayControllerInfo(ctr)

        print("Press any button on the controller you wish to use...")
        i = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONDOWN:
                    ctrID = event.__getattribute__('instance_id')
                    print("Input detected")
                    return controllers[ctrID]
            pygame.time.wait(1000)
            print(self.__connectionMsg(1, i))
            i = self.__messageInfo(i)

    def __messageInfo(self, x: int) -> int:
        if x < 3:
            return x + 1
        else:
            return 0

    def __connectionMsg(self, msgNum: int, x: int) -> str:
        msg = "\t\tWaiting for Controller "
        if msgNum == 0:
            msg += "connection"
        if msgNum == 1:
            msg += "input"
        for _ in range(x):
            msg += "."
        return msg

    def __displayControllerInfo(self, controller: Joystick):
        name = controller.get_name()
        idValue = controller.get_id()
        numAxes = controller.get_numaxes()
        numBalls = controller.get_numballs()
        numButtons = controller.get_numbuttons()
        numHats = controller.get_numhats()

        print("Controller Information")
        print("\tName: " + str(name))
        print("\tID: " + str(idValue))
        print("\t\tNumber of Axes: " + str(numAxes))
        print("\t\tNumber of Balls: " + str(numBalls))
        print("\t\tNumber of Buttons: " + str(numButtons))
        print("\t\tNumber of Hats: " + str(numHats))

    def __getAllControllers(self) -> list:
        pygame.joystick.init()
        totalJoysticks = pygame.joystick.get_count()
        ctrList = []
        for i in range(totalJoysticks):
            ctr = pygame.joystick.Joystick(i)
            ctrList.append(ctr)
        return ctrList

    def getHatValues(self, controller: Joystick, axis: int) -> tuple:
        return controller.get_hat(axis)