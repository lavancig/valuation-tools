
from src.globals import loadGlobals

from src.gui.guiMain import GuiMain
from src.Controller import Controller
from src.ValuationModel import ValuationModel

import numpy as np



def mainFunction():
    loadGlobals()
    guiObj = GuiMain()
    modelObj = ValuationModel()
    ControllerObj = Controller(guiObj, modelObj)

    guiObj.registerController(ControllerObj)
    modelObj.registerController(ControllerObj)

    guiObj.startGUI()



if __name__ == "__main__":
    mainFunction()