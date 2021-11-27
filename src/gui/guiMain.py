
import tkinter as tk
from tkinter import getdouble, ttk

from .ParametersTab import getParametersTab
from .ValuationTab import ValuationTab
from .DiscountTab import DiscountTab


tabControl = []

class GuiMain:
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("1000x600")
        self.root.title("Valuation Tools")
        tabControl = ttk.Notebook(self.root)
        
        # Creates tab objects
        self._valuationTab = ValuationTab(tabControl)
        self._discountTab = DiscountTab(tabControl)


        # Sets tabs in place
        suitabilityTab = ttk.Frame(tabControl)
        valuationTab = self._valuationTab.getValuationTab()
        discountTab = self._discountTab.getDiscountTab()
        parametersTab = getParametersTab(tabControl)
        
        tabControl.add(suitabilityTab, text ='Suitability')
        tabControl.add(valuationTab, text ='Valuation')
        tabControl.add(discountTab, text ='Discount')
        tabControl.add(parametersTab, text ='Parameters')

        tabControl.pack(expand = 1, fill ="both")
        
        ttk.Label(suitabilityTab, 
                text ="Under Development").grid(column = 0, 
                                    columnspan = 5,
                                    row = 0,
                                    padx = 10,
                                    pady = 10, 
                                    sticky = tk.W+tk.E)  

    def registerController(self, controllerObj):
        self._controllerObj = controllerObj
        self._valuationTab.registerController(controllerObj)
        self._discountTab.registerController(controllerObj)

    def addDiscountTab(self, discountObj):
        discountTab = getDiscountTab(discountObj)
        tabControl.add(discountTab, text ='Discount')
        # tabControl.pack_forget()
        # tabControl.pack(expand = 1, fill ="both")

    def startGUI(self):
        self.root.mainloop()

    def updteFairValue(self, fairValue):
        self._valuationTab.updateLoadingLabel(fairValue)

    def updateValuationSummaryTable(self, summaryTable):
        self._valuationTab.updateSummaryTable(summaryTable)

    def getControllerObj(self):
        return self._controllerObj

