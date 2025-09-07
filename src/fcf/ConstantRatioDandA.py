import pandas as pd
import numpy as np

class ConstantRatioDandA:
    
    def __init__(self, pastRevenueStreams, pastDandAStreams):
        # Filter out NaN values to calculate ratio only from valid data
        validRevenue = pastRevenueStreams.dropna()
        validDandA = pastDandAStreams.dropna()
        
        # Only use dates that have both valid revenue and D&A data
        commonDates = validRevenue.index.intersection(validDandA.index)
        
        if len(commonDates) == 0:
            # Fallback to a reasonable ratio if no valid data
            self._dandARatio = 0.06  # 6% as fallback (typical D&A to revenue ratio)
            return
            
        nYears = 0
        dandARatioSum = 0
        for date in commonDates:
            if pd.notna(pastRevenueStreams[date]) and pd.notna(pastDandAStreams[date]):
                nYears = nYears + 1
                # Calculate ratio of D&A to revenue
                dandARatioSum = dandARatioSum + pastDandAStreams[date]/pastRevenueStreams[date]
        
        if nYears > 0:
            self._dandARatio = dandARatioSum/nYears
        else:
            # Fallback to a reasonable ratio if no valid data
            self._dandARatio = 0.06  # 6% as fallback (typical D&A to revenue ratio)

    def setDandARatio(self, ratio):
        self._dandARatio = ratio

    def getDandAStreams(self, revenueStreams, pastDandAStreams):
        # Filter out NaN values from past D&A streams to match the filtered revenue data
        validPastDandAStreams = pastDandAStreams.dropna()
        
        if validPastDandAStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()

        # Handle both Series and DataFrame inputs
        if hasattr(validPastDandAStreams, 'values'):
            if len(validPastDandAStreams.values.shape) == 1:
                # It's a Series, use values directly
                dandAStreamPredictions = pd.DataFrame([validPastDandAStreams.values], columns=validPastDandAStreams.index, index=['D&A'])
            else:
                # It's a DataFrame, extract the first row
                dandAStreamPredictions = pd.DataFrame([validPastDandAStreams.iloc[0].values], columns=validPastDandAStreams.columns, index=['D&A'])
        else:
            # Fallback for other data types
            dandAStreamPredictions = pd.DataFrame([validPastDandAStreams], columns=validPastDandAStreams.index, index=['D&A'])

        for date in revenueStreams.columns.values:
            if(date in validPastDandAStreams):
                continue
            # Project D&A based on revenue and historical ratio
            dandAStreamPredictions.loc['D&A', date] = revenueStreams.loc['Revenue', date] * self._dandARatio
            
        return dandAStreamPredictions

    def getDandARatioTable(self, predictedRevenue, predictedDandA):
        ratioPredictions = pd.DataFrame([], columns=predictedDandA.columns.values, index=['D&A Ratio'])
        for date in predictedRevenue.columns.values:
            ratioPredictions.loc['D&A Ratio', date] = predictedDandA.loc['D&A', date] / predictedRevenue.loc['Revenue', date]
        return ratioPredictions
