import pandas as pd
import numpy as np

class ConstantRatioNetBorrowings:
    
    def __init__(self, pastRevenueStreams, pastNetBorrowingsStreams):
        # Filter out NaN values to calculate ratio only from valid data
        validRevenue = pastRevenueStreams.dropna()
        validNetBorrowings = pastNetBorrowingsStreams.dropna()
        
        # Only use dates that have both valid revenue and net borrowings data
        commonDates = validRevenue.index.intersection(validNetBorrowings.index)
        
        if len(commonDates) == 0:
            # Fallback to a reasonable ratio if no valid data
            self._netBorrowingsRatio = 0.02  # 2% as fallback (typical net borrowings to revenue ratio)
            return
            
        nYears = 0
        netBorrowingsRatioSum = 0
        for date in commonDates:
            if pd.notna(pastRevenueStreams[date]) and pd.notna(pastNetBorrowingsStreams[date]):
                nYears = nYears + 1
                # Calculate ratio of net borrowings to revenue
                netBorrowingsRatioSum = netBorrowingsRatioSum + pastNetBorrowingsStreams[date]/pastRevenueStreams[date]
        
        if nYears > 0:
            self._netBorrowingsRatio = netBorrowingsRatioSum/nYears
        else:
            # Fallback to a reasonable ratio if no valid data
            self._netBorrowingsRatio = 0.02  # 2% as fallback (typical net borrowings to revenue ratio)

    def setNetBorrowingsRatio(self, ratio):
        self._netBorrowingsRatio = ratio

    def getNetBorrowingsStreams(self, revenueStreams, pastNetBorrowingsStreams):
        # Filter out NaN values from past net borrowings streams to match the filtered revenue data
        validPastNetBorrowingsStreams = pastNetBorrowingsStreams.dropna()
        
        if validPastNetBorrowingsStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()

        # Handle both Series and DataFrame inputs
        if hasattr(validPastNetBorrowingsStreams, 'values'):
            if len(validPastNetBorrowingsStreams.values.shape) == 1:
                # It's a Series, use values directly
                netBorrowingsStreamPredictions = pd.DataFrame([validPastNetBorrowingsStreams.values], columns=validPastNetBorrowingsStreams.index, index=['Net Borrowings'])
            else:
                # It's a DataFrame, extract the first row
                netBorrowingsStreamPredictions = pd.DataFrame([validPastNetBorrowingsStreams.iloc[0].values], columns=validPastNetBorrowingsStreams.columns, index=['Net Borrowings'])
        else:
            # Fallback for other data types
            netBorrowingsStreamPredictions = pd.DataFrame([validPastNetBorrowingsStreams], columns=validPastNetBorrowingsStreams.index, index=['Net Borrowings'])

        for date in revenueStreams.columns.values:
            if(date in validPastNetBorrowingsStreams):
                continue
            # Project net borrowings based on revenue and historical ratio
            netBorrowingsStreamPredictions.loc['Net Borrowings', date] = revenueStreams.loc['Revenue', date] * self._netBorrowingsRatio
            
        return netBorrowingsStreamPredictions

    def getNetBorrowingsRatioTable(self, predictedRevenue, predictedNetBorrowings):
        ratioPredictions = pd.DataFrame([], columns=predictedNetBorrowings.columns.values, index=['Net Borrowings Ratio'])
        for date in predictedRevenue.columns.values:
            ratioPredictions.loc['Net Borrowings Ratio', date] = predictedNetBorrowings.loc['Net Borrowings', date] / predictedRevenue.loc['Revenue', date]
        return ratioPredictions
