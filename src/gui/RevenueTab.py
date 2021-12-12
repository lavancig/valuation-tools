import tkinter as tk
from tkinter import ttk

import threading


revenueTypes = ("Specialist Estimates", "Constant")

class RevenueTab:
    def __init__(self, tabControl):
        self._tabControl = tabControl
        self._revenueTab = ttk.Frame(self._tabControl)

        self._revenueTypeSelection = tk.StringVar(value=revenueTypes[0])
        def onRevenueTypeChanged(*args):
            self.getRevenueTab()
        self._revenueTypeSelection.trace("w", onRevenueTypeChanged)
        self._initialized = False
        self._typeSpecificWidgets = []

    def getRevenueTab(self):
        self.clearFrame()
        if not self._initialized:
            ttk.Label(self._revenueTab,
                text ="Revenue Type: ").grid(column = 0,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

            ttk.OptionMenu(self._revenueTab, self._revenueTypeSelection, revenueTypes[0], *revenueTypes).grid(column = 1,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

            def onButtonPress():
                def thread_function():        
                    if self._revenueTypeSelection.get() == "Specialist Estimates":
                        self._controllerObj.setRevenueTypeAverage()
                    elif self._revenueTypeSelection.get() == "Constant":
                        self._controllerObj.setRevenueTypeConstant(float(self._revenueValue.get())/100)
                buttonPressThread = threading.Thread(target=thread_function)
                buttonPressThread.start()

                    
            ttk.Button ( self._revenueTab, text="Apply", command = onButtonPress).grid(column = 2,
                                                                        row = 0, 
                                                                        padx = 10,
                                                                        pady = 10)
            self._initialized = True

        if self._revenueTypeSelection.get() == "Specialist Estimates":
            self.getAverageRevenueTab()
        elif self._revenueTypeSelection.get() == "Constant":
            self.getConstantRevenueTab()


        return self._revenueTab

    def getAverageRevenueTab(self):
        pass

    def getConstantRevenueTab(self):
        # Prediction Window    
        label = ttk.Label(self._revenueTab, text ="Revenue Growth(%): ")
        label.grid(column = 0, row = 1,  padx = 10, pady = 10)
        self._typeSpecificWidgets.append(label)


        self._revenueValue = tk.StringVar(value=20)
        entry = ttk.Entry(self._revenueTab, textvariable=self._revenueValue)
        entry.grid(column = 1, row = 1, padx = 10, pady = 10)
        self._typeSpecificWidgets.append(entry)

    def clearFrame(self):
        while len(self._typeSpecificWidgets) > 0:
            self._typeSpecificWidgets.pop(0).destroy()

    def registerController(self, controllerObj):
        self._controllerObj = controllerObj