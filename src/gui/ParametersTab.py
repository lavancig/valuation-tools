
import tkinter as tk
from tkinter import ttk

from ..globals import saveGlobals, resetGlobals, setGlobal, getGlobal


def getParametersTab(tabControl):
    parametersTab = ttk.Frame(tabControl)

    # Risk Free Interest Rate
    ttk.Label(parametersTab,
            text ="Risk Free Interest Rate").grid(column = 0,
                                        row = 0, 
                                        padx = 10,
                                        pady = 10)


    interestRate = tk.StringVar(value=str(getGlobal('RiskFreeInterestRate')))

    def registerRiskFreeRate(*args):
        try:
            float(interestRate.get())
        except:
            interestRate.set(str(getGlobal('RiskFreeInterestRate')))
        setGlobal('RiskFreeInterestRate', float(interestRate.get()))
        saveGlobals()

    interestRate.trace_add('write', registerRiskFreeRate)
    ttk.Entry(parametersTab, textvariable=interestRate).grid(column = 1,
                                        row = 0, 
                                        padx = 10,
                                        pady = 10)



    # Market Average Return
    ttk.Label(parametersTab,
            text ="Market Average Return").grid(column = 0,
                                        row = 1, 
                                        padx = 10,
                                        pady = 10)

    marketReturn = tk.StringVar(value=str(getGlobal('marketReturn')))

    def registerMarketReturn(*args):
        try:
            float(marketReturn.get())
        except:
            marketReturn.set(str(getGlobal('marketReturn')))
        setGlobal('marketReturn', float(marketReturn.get()))
        saveGlobals()

    marketReturn.trace_add('write', registerMarketReturn)
    ttk.Entry(parametersTab, textvariable=marketReturn).grid(column = 1,
                                        row = 1, 
                                        padx = 10,
                                        pady = 10)

    def onButtonPress():
        resetGlobals()
        interestRate.set(str(getGlobal('RiskFreeInterestRate')))
        marketReturn.set(str(getGlobal('marketReturn')))
    
    # Economy Average Growth Rate
    ttk.Label(parametersTab,
            text ="Economy Average Growth Rate").grid(column = 0,
                                        row = 2, 
                                        padx = 10,
                                        pady = 10)

    avgGrowth = tk.StringVar(value=str(getGlobal('economyGrowth')))

    def registerAvgGrowth(*args):
        try:
            float(avgGrowth.get())
        except:
            avgGrowth.set(str(getGlobal('economyGrowth')))
        setGlobal('economyGrowth', float(avgGrowth.get()))
        saveGlobals()

    avgGrowth.trace_add('write', registerAvgGrowth)
    ttk.Entry(parametersTab, textvariable=avgGrowth).grid(column = 1,
                                        row = 2, 
                                        padx = 10,
                                        pady = 10)

    def onButtonPress():
        resetGlobals()
        interestRate.set(str(getGlobal('RiskFreeInterestRate')))
        marketReturn.set(str(getGlobal('marketReturn')))
        avgGrowth.set(str(getGlobal('economyGrowth')))

    # Reset Button
    ttk.Button ( parametersTab, text="Reset to Defaults", command = onButtonPress).grid(column = 0,
                                                                row = 3, 
                                                                padx = 10,
                                                                pady = 10)

                    

    return parametersTab

