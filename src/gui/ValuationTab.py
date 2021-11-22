
import tkinter as tk
from tkinter import ttk
import time
from pandastable import Table, TableModel
import numpy as np

from ..globals import saveGlobals, resetGlobals, setGlobal, getGlobal
from ..DCF_FCFF import DCF_FCFF
import threading

valuationTypes = ["FCFF"]


def fillTable(tree, tableData):
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
        if tableData.index.values[rowNo] == 'Revenue' or tableData.index.values[rowNo] == 'Income' or tableData.index.values[rowNo] == 'Present Value':
            data = tableData.iloc[rowNo].values / 1000000
            for idx in range(len(data)):
                stringData.append("{:.0f}".format(data[idx]) + ' M')
        elif tableData.index.values[rowNo] == 'Discount Rate':
            data = tableData.iloc[rowNo].values
            for idx in range(len(data)):
                stringData.append("{:.4f}".format(data[idx]))
        else:
            data = tableData.iloc[rowNo].values
            nanEntries = np.isnan(data)
            for idx in range(len(data)):
                if nanEntries[idx]:
                    stringData.append(" ")
                else:
                    stringData.append("{:.2f}".format(data[idx]))
        tree.insert('', tk.END, values=stringData)
    tree.grid(column = 0, row = 1, padx = 10, pady = 10, columnspan = 6, sticky = tk.W+tk.E)




def getValuationTab(tabControl):
    valuationTab = ttk.Frame(tabControl)
    currSelection = tk.StringVar(value=valuationTypes[0])

    ttk.Label(valuationTab,
        text ="Valuation Type: ").grid(column = 0,
                                    row = 0, 
                                    padx = 10,
                                    pady = 10)

    ttk.OptionMenu(valuationTab, currSelection, valuationTypes).grid(column = 1,
                                    row = 0, 
                                    padx = 10,
                                    pady = 10)

    ttk.Label(valuationTab, text ="Company Ticker: ").grid(column = 2,
                                        row = 0, 
                                        padx = 10,
                                        pady = 10)

    ticker = tk.StringVar()
    ttk.Entry(valuationTab, textvariable=ticker).grid(column = 3,
                                        row = 0, 
                                        padx = 10,
                                        pady = 10)

    loadingLabel = tk.StringVar()
    ttk.Label(valuationTab, textvariable=loadingLabel).grid(column = 5,
                                        row = 0, 
                                        padx = 10,
                                        pady = 10)

    tree = ttk.Treeview(valuationTab, show='headings', height=8)

    dcfObj = []

    def onButtonPress():
        tree.grid_forget()
        def thread_function():
            dcfObj = DCF_FCFF(ticker.get())
            loadingLabel.set('Calculated Fair Value: ' + "{:.2f}".format(dcfObj.calculateFairValue(5)))
            tableData = dcfObj.getResultTable()
            fillTable(tree, tableData)
        buttonPressThread = threading.Thread(target=thread_function)
        loadingLabel.set('Loading data, please wait')
        buttonPressThread.start()

    
    ttk.Button ( valuationTab, text="Calculate", command = onButtonPress).grid(column = 4,
                                                                row = 0, 
                                                                padx = 10,
                                                                pady = 10)



    return valuationTab

