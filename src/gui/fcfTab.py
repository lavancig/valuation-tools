import tkinter as tk
from tkinter import ttk

import threading


fcfTypes = ("Average", "Constant")

class FCFTab:
    def __init__(self, tabControl):
        self._tabControl = tabControl
        self._fcfTab = ttk.Frame(self._tabControl)

        self._fcfTypeSelection = tk.StringVar(value=fcfTypes[0])
        def onFCFTypeChanged(*args):
            self.getFCFTab()
        self._fcfTypeSelection.trace("w", onFCFTypeChanged)
        self._initialized = False
        self._typeSpecificWidgets = []

    def getFCFTab(self):
        self.clearFrame()
        if not self._initialized:
            ttk.Label(self._fcfTab,
                text ="FCF Type: ").grid(column = 0,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

            ttk.OptionMenu(self._fcfTab, self._fcfTypeSelection, fcfTypes[0], *fcfTypes).grid(column = 1,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

            def onButtonPress():
                def thread_function():        
                    if self._fcfTypeSelection.get() == "Average":
                        self._controllerObj.setFCFTypeAverage()
                    elif self._fcfTypeSelection.get() == "Constant":
                        self._controllerObj.setFCFTypeConstant(float(self._fcfValue.get())/100)
                buttonPressThread = threading.Thread(target=thread_function)
                buttonPressThread.start()

                    
            ttk.Button ( self._fcfTab, text="Apply", command = onButtonPress).grid(column = 2,
                                                                        row = 0, 
                                                                        padx = 10,
                                                                        pady = 10)
            self._initialized = True

        if self._fcfTypeSelection.get() == "Average":
            self.getAverageFCFTab()
        elif self._fcfTypeSelection.get() == "Constant":
            self.getConstantDiscountTab()


        return self._fcfTab

    def getAverageFCFTab(self):
        pass

    def getConstantDiscountTab(self):
        # Prediction Window    
        label = ttk.Label(self._fcfTab, text ="Profitability(%): ")
        label.grid(column = 0, row = 1,  padx = 10, pady = 10)
        self._typeSpecificWidgets.append(label)


        self._fcfValue = tk.StringVar(value=100)
        entry = ttk.Entry(self._fcfTab, textvariable=self._fcfValue)
        entry.grid(column = 1, row = 1, padx = 10, pady = 10)
        self._typeSpecificWidgets.append(entry)

    def clearFrame(self):
        while len(self._typeSpecificWidgets) > 0:
            self._typeSpecificWidgets.pop(0).destroy()

    def registerController(self, controllerObj):
        self._controllerObj = controllerObj