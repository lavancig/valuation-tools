
import tkinter as tk
from tkinter import getdouble, ttk


from .ParametersTab import getParametersTab
from .ValuationTab import ValuationTab
from .DiscountTab import DiscountTab
from .ProfitabilityTab import ProfitabilityTab
from .fcfTab import FCFTab
from .RevenueTab import RevenueTab
from .SensitivityTab import SensitivityTab

tabControl = []

class GuiMain:
    def __init__(self):
        self.root = tk.Tk()

        self.root.geometry("1200x600")
        self.root.title("Valuation Tools")
        tabControl = ttk.Notebook(self.root)
        
        # Creates tab objects
        self._valuationTab = ValuationTab(tabControl)
        self._discountTab = DiscountTab(tabControl)
        self._profitabilityTab = ProfitabilityTab(tabControl)
        self._fcfTab = FCFTab(tabControl)
        self._revenueTab = RevenueTab(tabControl)
        self._sensitivityTab = SensitivityTab(tabControl, None)  # Controller will be set later



        # Sets tabs in place
        suitabilityTab = ttk.Frame(tabControl)
        valuationTab = self._valuationTab.getValuationTab()
        discountTab = self._discountTab.getDiscountTab()
        profitabilityTab = self._profitabilityTab.getProfitabilityTab()
        fcfTab = self._fcfTab.getFCFTab()
        revenueTab = self._revenueTab.getRevenueTab()
        parametersTab = getParametersTab(tabControl)
        sensitivityTab = self._sensitivityTab.frame
        
        tabControl.add(suitabilityTab, text ='Suitability')
        tabControl.add(valuationTab, text ='Valuation')
        tabControl.add(discountTab, text ='Discount')
        tabControl.add(profitabilityTab, text ='Profitability')
        tabControl.add(fcfTab, text ='FCF')
        tabControl.add(revenueTab, text ='Revenue')
        tabControl.add(parametersTab, text ='Parameters')
        tabControl.add(sensitivityTab, text ='Sensitivity Analysis')

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
        self._profitabilityTab.registerController(controllerObj)
        self._fcfTab.registerController(controllerObj)
        self._revenueTab.registerController(controllerObj)
        self._sensitivityTab.controller = controllerObj
        # Update sensitivity tab status after controller is set (defensively)
        try:
            self._sensitivityTab.refresh_status()
        except Exception:
            # Ignore errors during initialization
            pass

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
        # Refresh sensitivity tab status when valuation is updated (defensively)
        try:
            self._sensitivityTab.refresh_status()
        except Exception:
            # Ignore errors if sensitivity tab not ready
            pass

    def getControllerObj(self):
        return self._controllerObj

    def setSharesOutstanding(self, value):
        self._valuationTab.setSharesOutstanding(value)

