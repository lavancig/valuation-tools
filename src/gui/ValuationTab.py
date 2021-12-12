
import tkinter as tk
from tkinter import ttk
import time
from pandastable import Table, TableModel
import numpy as np

from ..globals import saveGlobals, resetGlobals, setGlobal, getGlobal
from ..DCF_FCFE import DCF_FCFE

import threading

valuationTypes = ("FCFE", )
DEFAULT_PREDICTION_WINDOW = 5 #YEARS


class ValuationTab:
    def __init__(self, tabControl):
        self._tabControl = tabControl

    def fillTable(self, tree, tableData):
        tree.delete(*tree.get_children())
        tree['columns'] = tuple()
        tree['columns'] = tuple(" ") + tuple(tableData.columns.values)
        tree.heading(0, text=" ")
        tree.column(0, minwidth=0, width=100)
        for columnNo in range(0, len(tableData.columns.values)):
            if tableData.columns.values[columnNo] == 'perpetual':
                tree.heading(columnNo + 1, text=tableData.columns.values[columnNo] + " @ " + str(np.datetime64(tableData.columns.values[columnNo-1], 'Y') + np.timedelta64(1,'Y')) )
                tree.column(columnNo + 1, minwidth=0, width=100)
            else:
                tree.heading(columnNo + 1, text=np.datetime64(tableData.columns.values[columnNo], 'Y'))
                tree.column(columnNo + 1, minwidth=0, width=70)

        
        for rowNo in range(len(tableData.index.values)):
            data = []
            stringData = [str(tableData.index.values[rowNo])]
            if tableData.index.values[rowNo] == 'Revenue' or tableData.index.values[rowNo] == 'Income' or tableData.index.values[rowNo] == 'Present Value' or tableData.index.values[rowNo] == 'FCFE':
                data = tableData.iloc[rowNo].values / 1000000
                for idx in range(len(data)):
                    stringData.append("{:.0f}".format(data[idx]) + ' M')
            elif tableData.index.values[rowNo] == 'Discount Rate' or tableData.index.values[rowNo] == 'Profitability' or tableData.index.values[rowNo] == 'Cash Flow To Net Income Ratio':
                data = tableData.iloc[rowNo].values
                for idx in range(len(data)):
                    stringData.append("{:.4f}".format(data[idx]))
            else:
                for data in tableData.iloc[rowNo].values:
                    if np.isnan(data):
                        stringData.append(" ")
                    else:
                        stringData.append("{:.2f}".format(data))
            tree.insert('', tk.END, values=stringData)
        tree.grid(column = 0, row = 2, padx = 10, pady = 10, columnspan = 8, sticky = tk.W+tk.E)

        self._sharesOutstandinglabel.grid(column = 0, row = 1,  padx = 10, pady = 10)
        self._sharesOutstandinglabelEntry.grid(column = 1, row = 1, padx = 10, pady = 10)
        self._sharesOutstandinglabelButton.grid(column = 2, row = 1, padx = 10, pady = 10)

    def getValuationTab(self):
        self._valuationTab = ttk.Frame(self._tabControl)
        self._valuationTypeSelection = tk.StringVar(value=valuationTypes[0])

        ttk.Label(self._valuationTab,
            text ="Valuation Type: ").grid(column = 0,
                                        row = 0, 
                                        padx = 10,
                                        pady = 10)

        ttk.OptionMenu(self._valuationTab, self._valuationTypeSelection, *valuationTypes).grid(column = 1,
                                        row = 0, 
                                        padx = 10,
                                        pady = 10)

        # Prediction Window    
        ttk.Label(self._valuationTab, text ="Prediction Window: ").grid(column = 2,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

        self._predictionWindow = tk.StringVar(value=DEFAULT_PREDICTION_WINDOW)
        ttk.Entry(self._valuationTab, textvariable=self._predictionWindow).grid(column = 3,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)


        # Company Ticker
        ttk.Label(self._valuationTab, text ="Company Ticker: ").grid(column = 4,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

        self._ticker = tk.StringVar()
        ttk.Entry(self._valuationTab, textvariable=self._ticker).grid(column = 5,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

        self._loadingLabel = tk.StringVar()
        ttk.Label(self._valuationTab, textvariable=self._loadingLabel).grid(column = 7,
                                            row = 0, 
                                            padx = 10,
                                            pady = 10)

        # Shares Outstanding:
        self._sharesOutstandinglabel = ttk.Label(self._valuationTab, text ="Shares Outstanding: ")

        self._sharesOutstanding = tk.StringVar(value=1)
        self._sharesOutstandinglabelEntry = ttk.Entry(self._valuationTab, textvariable=self._sharesOutstanding)

        def onButtonPress():
            def thread_function():        
                self._controllerObj.setSharesOutstanding(float(self._sharesOutstanding.get()))
            buttonPressThread = threading.Thread(target=thread_function)
            buttonPressThread.start()

        self._sharesOutstandinglabelButton = ttk.Button ( self._valuationTab, text="Apply", command = onButtonPress)




        self._tree = ttk.Treeview(self._valuationTab, show='headings', height=8)

        def onButtonPress():
            def thread_function():
                self._tree.grid_forget()
                self.resetLoadingLabel()
                self._sharesOutstandinglabel.grid_forget()
                self._sharesOutstandinglabelEntry.grid_forget()
                self._sharesOutstandinglabelButton.grid_forget()
                self._controllerObj.calculateFairValueRequest(self._valuationTypeSelection.get(), self._predictionWindow.get(), self._ticker.get())
                
            buttonPressThread = threading.Thread(target=thread_function)
            buttonPressThread.start()

        
        ttk.Button ( self._valuationTab, text="Calculate", command = onButtonPress).grid(column = 6,
                                                                    row = 0, 
                                                                    padx = 10,
                                                                    pady = 10)



        return self._valuationTab


    def updateLoadingLabel(self, fairValue):
        self._loadingLabel.set('Calculated Fair Value: ' + "{:.2f}".format(fairValue))

    def resetLoadingLabel(self):
        self._loadingLabel.set('Loading data, please wait')
            
    def updateSummaryTable(self, tableData):
        self._tree.grid_forget()
        self._sharesOutstandinglabel.grid_forget()
        self._sharesOutstandinglabelEntry.grid_forget()
        self._sharesOutstandinglabelButton.grid_forget()
        self.fillTable(self._tree, tableData)
    
    def registerController(self, controllerObj):
        self._controllerObj = controllerObj

    def setSharesOutstanding(self, value):
        self._sharesOutstanding.set(value)