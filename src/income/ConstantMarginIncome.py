from .IncomeBase import IncomeBase
import pandas as pd
import numpy as np 
import copy

class ConstantMarginIncome(IncomeBase):
    
    def __init__(self, pastRevenueStreams, pastIncomeStreams):
        nYears = 0
        incomeMarginSum = 0
        for date in pastRevenueStreams.index:
            nYears = nYears + 1
            incomeMarginSum = incomeMarginSum + pastIncomeStreams[date]/pastRevenueStreams[date]
        self._incomeMargin = incomeMarginSum/nYears


    def getIncomeStreams(self, revenueStreams, pastIncomeStreams):

        incomeStreamPredictions = pd.DataFrame([pastIncomeStreams.values], columns=pastIncomeStreams.index, index=['Income'])

        for date in revenueStreams.columns.values:
            if(date in pastIncomeStreams):
                continue
            incomeStreamPredictions.loc['Income', date] = revenueStreams.loc['Revenue', date] * self._incomeMargin
            
        return incomeStreamPredictions


