from .IncomeBase import IncomeBase
import pandas as pd
import numpy as np 
import copy

class ConstantMarginIncome(IncomeBase):
    
    def __init__(self, pastRevenueStreams, pastIncomeStreams):
        # Filter out NaN values to calculate margin only from valid data
        validRevenue = pastRevenueStreams.dropna()
        validIncome = pastIncomeStreams.dropna()
        
        # Only use dates that have both valid revenue and income data
        commonDates = validRevenue.index.intersection(validIncome.index)
        
        if len(commonDates) == 0:
            # Fallback to a reasonable margin if no valid data
            self._incomeMargin = 0.25  # 25% as fallback
            return
            
        nYears = 0
        incomeMarginSum = 0
        for date in commonDates:
            if pd.notna(pastRevenueStreams[date]) and pd.notna(pastIncomeStreams[date]):
                nYears = nYears + 1
                incomeMarginSum = incomeMarginSum + pastIncomeStreams[date]/pastRevenueStreams[date]
        
        if nYears > 0:
            self._incomeMargin = incomeMarginSum/nYears
        else:
            # Fallback to a reasonable margin if no valid data
            self._incomeMargin = 0.25  # 25% as fallback

    def setProfitability(self, profitablity):
        self._incomeMargin = profitablity

    def getIncomeStreams(self, revenueStreams, pastIncomeStreams):
        # Filter out NaN values from past income streams to match the filtered revenue data
        validPastIncomeStreams = pastIncomeStreams.dropna()
        
        if validPastIncomeStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()

        incomeStreamPredictions = pd.DataFrame([validPastIncomeStreams.values], columns=validPastIncomeStreams.index, index=['Income'])

        for date in revenueStreams.columns.values:
            if(date in validPastIncomeStreams):
                continue
            incomeStreamPredictions.loc['Income', date] = revenueStreams.loc['Revenue', date] * self._incomeMargin
            
        return incomeStreamPredictions

    def getProfitabilityTable(self, predictedRevenue, predictedIncome):
        profitabilityPredictions = pd.DataFrame([], columns=predictedIncome.columns.values, index=['Profitability'])
        for date in predictedRevenue.columns.values:
            profitabilityPredictions.loc['Profitability', date] = predictedIncome.loc['Income', date] / predictedRevenue.loc['Revenue', date]
        return profitabilityPredictions