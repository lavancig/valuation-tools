
import tkinter as tk
from tkinter import ttk

from .ParametersTab import getParametersTab
from .ValuationTab import getValuationTab

def guiMain():

    root = tk.Tk()

    root.geometry("1000x600")
    root.title("Valuation Tools")
    tabControl = ttk.Notebook(root)
    
    sutabilityTab = ttk.Frame(tabControl)
    valuationTab = getValuationTab(tabControl)
    parametersTab = getParametersTab(tabControl)
    
    tabControl.add(sutabilityTab, text ='Suitability')
    tabControl.add(valuationTab, text ='Valuation')
    tabControl.add(parametersTab, text ='Parameters')

    tabControl.pack(expand = 1, fill ="both")
    
    ttk.Label(sutabilityTab, 
            text ="Under Development").grid(column = 0, 
                                columnspan = 5,
                                row = 0,
                                padx = 10,
                                pady = 10, 
                                sticky = tk.W+tk.E)  



    root.mainloop()