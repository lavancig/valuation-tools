
from src.globals import loadGlobals

from src.gui.guiMain import guiMain



from datetime import date
import numpy as np
import pandas as pd



def mainFunction():
    loadGlobals()
    guiMain()

if __name__ == "__main__":
    mainFunction()