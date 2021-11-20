from .IncomeBase import IncomeBase
import pandas
import numpy as np 
import copy

class ConstantMarginIncome(IncomeBase):
    
    def __init__(self, pastRevenueStreams, pastIncomeStreams):
        nYears = 0
        incomeMarginSum = 0
        for date in pastRevenueStreams.columns:
            nYears = nYears + 1
            incomeMarginSum = incomeMarginSum + pastIncomeStreams.loc['Net Income From Continuing Ops', date]/pastRevenueStreams.loc['Total Revenue', date]
        self._incomeMargin = incomeMarginSum/nYears


    def getIncomeStreams(self, revenueStreams, pastIncomeStreams):
        incomeStreamPredictions = copy.deepcopy(pastIncomeStreams)

        for date in revenueStreams.columns:
            if(date in pastIncomeStreams):
                continue
            incomeStreamPredictions.loc['Net Income From Continuing Ops', date] = revenueStreams.loc['Total Revenue', date] * self._incomeMargin
            
        return incomeStreamPredictions


