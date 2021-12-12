import tkinter as tk
from tkinter import ttk

import threading


profitabilityTypes = ("Average", "Constant")

class ProfitabilityTab:
    def __init__(self, tabControl):
        self._tabControl = tabControl
        self._profitabilityTab = ttk.Frame(self._tabControl)

        self._profitabilityTypeSelection = tk.StringVar(value=profitabilityTypes[0])
        def onProfitabilityTypeChanged(*args):
            self.getProfitabilityTab()
        self._profitabilityTypeSelection.trace("w", onProfitabilityTypeChanged)
        self._initialized = False
        self._typeSpecificWidgets = []

    def getProfitabilityTab(self):
        self.clearFrame()
        if not self._initialized:
            ttk.Label(self._profitabilityTab,
                text ="Profitability Type: ").grid(column = 0,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

            ttk.OptionMenu(self._profitabilityTab, self._profitabilityTypeSelection, profitabilityTypes[0], *profitabilityTypes).grid(column = 1,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

            def onButtonPress():
                def thread_function():        
                    if self._profitabilityTypeSelection.get() == "Average":
                        self._controllerObj.setProfitablityTypeAverage()
                    elif self._profitabilityTypeSelection.get() == "Constant":
                        self._controllerObj.setProfitabilityTypeConstant(float(self._profitabilityValue.get())/100)
                buttonPressThread = threading.Thread(target=thread_function)
                buttonPressThread.start()

                    
            ttk.Button ( self._profitabilityTab, text="Apply", command = onButtonPress).grid(column = 2,
                                                                        row = 0, 
                                                                        padx = 10,
                                                                        pady = 10)
            self._initialized = True

        if self._profitabilityTypeSelection.get() == "Average":
            self.getAverageProfitabilityTab()
        elif self._profitabilityTypeSelection.get() == "Constant":
            self.getConstantProfitabilityTab()


        return self._profitabilityTab

    def getAverageProfitabilityTab(self):
        pass

    def getConstantProfitabilityTab(self):
        # Prediction Window    
        label = ttk.Label(self._profitabilityTab, text ="Profitability(%): ")
        label.grid(column = 0, row = 1,  padx = 10, pady = 10)
        self._typeSpecificWidgets.append(label)


        self._profitabilityValue = tk.StringVar(value=20)
        entry = ttk.Entry(self._profitabilityTab, textvariable=self._profitabilityValue)
        entry.grid(column = 1, row = 1, padx = 10, pady = 10)
        self._typeSpecificWidgets.append(entry)

    def clearFrame(self):
        while len(self._typeSpecificWidgets) > 0:
            self._typeSpecificWidgets.pop(0).destroy()

    def registerController(self, controllerObj):
        self._controllerObj = controllerObj