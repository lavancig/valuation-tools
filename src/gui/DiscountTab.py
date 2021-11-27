import tkinter as tk
from tkinter import ttk

import threading


discountTypes = ("WACC", "Constant")

class DiscountTab:
    def __init__(self, tabControl):
        self._tabControl = tabControl
        self._discountTab = ttk.Frame(self._tabControl)

        self._discountTypeSelection = tk.StringVar(value=discountTypes[0])
        def onDiscountTypeChanged(*args):
            self.getDiscountTab()
        self._discountTypeSelection.trace("w", onDiscountTypeChanged)
        self._initialized = False
        self._typeSpecificWidgets = []

    def getDiscountTab(self):
        self.clearFrame()
        if not self._initialized:
            ttk.Label(self._discountTab,
                text ="Discount Type: ").grid(column = 0,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

            ttk.OptionMenu(self._discountTab, self._discountTypeSelection, discountTypes[0], *discountTypes).grid(column = 1,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

            def onButtonPress():
                def thread_function():        
                    if self._discountTypeSelection.get() == "WACC":
                        self._controllerObj.setDiscountTypeWACC()
                    elif self._discountTypeSelection.get() == "Constant":
                        self._controllerObj.setDiscountTypeConstant(float(self._discountValue.get())/100)
                buttonPressThread = threading.Thread(target=thread_function)
                buttonPressThread.start()

                    
            ttk.Button ( self._discountTab, text="Apply", command = onButtonPress).grid(column = 2,
                                                                        row = 0, 
                                                                        padx = 10,
                                                                        pady = 10)
            self._initialized = True

        if self._discountTypeSelection.get() == "WACC":
            self.getWACCDiscountTab()
        elif self._discountTypeSelection.get() == "Constant":
            self.getConstantDiscountTab()


        return self._discountTab

    def getWACCDiscountTab(self):
        pass

    def getConstantDiscountTab(self):
        # Prediction Window    
        label = ttk.Label(self._discountTab, text ="Discount(%): ")
        label.grid(column = 0, row = 1,  padx = 10, pady = 10)
        self._typeSpecificWidgets.append(label)


        self._discountValue = tk.StringVar(value=7)
        entry = ttk.Entry(self._discountTab, textvariable=self._discountValue)
        entry.grid(column = 1, row = 1, padx = 10, pady = 10)
        self._typeSpecificWidgets.append(entry)

    def clearFrame(self):
        while len(self._typeSpecificWidgets) > 0:
            self._typeSpecificWidgets.pop(0).destroy()

    def registerController(self, controllerObj):
        self._controllerObj = controllerObj