import pandas as pd
import numpy as np

class ConstantRatioCapEx:
    
    def __init__(self, pastRevenueStreams, pastCapExStreams):
        # Filter out NaN values to calculate ratio only from valid data
        validRevenue = pastRevenueStreams.dropna()
        validCapEx = pastCapExStreams.dropna()
        
        # Only use dates that have both valid revenue and CapEx data
        commonDates = validRevenue.index.intersection(validCapEx.index)
        
        if len(commonDates) == 0:
            # Fallback to a reasonable ratio if no valid data
            self._capExRatio = 0.08  # 8% as fallback (typical CapEx to revenue ratio)
            return
            
        nYears = 0
        capExRatioSum = 0
        for date in commonDates:
            if pd.notna(pastRevenueStreams[date]) and pd.notna(pastCapExStreams[date]):
                nYears = nYears + 1
                # Calculate ratio of CapEx to revenue (CapEx is typically negative, so we use absolute value)
                capExRatioSum = capExRatioSum + abs(pastCapExStreams[date])/pastRevenueStreams[date]
        
        if nYears > 0:
            self._capExRatio = capExRatioSum/nYears
        else:
            # Fallback to a reasonable ratio if no valid data
            self._capExRatio = 0.08  # 8% as fallback (typical CapEx to revenue ratio)

    def setCapExRatio(self, ratio):
        self._capExRatio = ratio

    def getCapExStreams(self, revenueStreams, pastCapExStreams):
        # Filter out NaN values from past CapEx streams to match the filtered revenue data
        validPastCapExStreams = pastCapExStreams.dropna()
        
        if validPastCapExStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()

        # Handle both Series and DataFrame inputs
        if hasattr(validPastCapExStreams, 'values'):
            if len(validPastCapExStreams.values.shape) == 1:
                # It's a Series, use values directly
                capExStreamPredictions = pd.DataFrame([validPastCapExStreams.values], columns=validPastCapExStreams.index, index=['CapEx'])
            else:
                # It's a DataFrame, extract the first row
                capExStreamPredictions = pd.DataFrame([validPastCapExStreams.iloc[0].values], columns=validPastCapExStreams.columns, index=['CapEx'])
        else:
            # Fallback for other data types
            capExStreamPredictions = pd.DataFrame([validPastCapExStreams], columns=validPastCapExStreams.index, index=['CapEx'])

        for date in revenueStreams.columns.values:
            if(date in validPastCapExStreams):
                continue
            # Project CapEx based on revenue and historical ratio (CapEx is typically negative)
            capExStreamPredictions.loc['CapEx', date] = -revenueStreams.loc['Revenue', date] * self._capExRatio
            
        return capExStreamPredictions

    def getCapExRatioTable(self, predictedRevenue, predictedCapEx):
        ratioPredictions = pd.DataFrame([], columns=predictedCapEx.columns.values, index=['CapEx Ratio'])
        for date in predictedRevenue.columns.values:
            # CapEx ratio is typically positive (absolute value of CapEx to revenue)
            ratioPredictions.loc['CapEx Ratio', date] = abs(predictedCapEx.loc['CapEx', date]) / predictedRevenue.loc['Revenue', date]
        return ratioPredictions
