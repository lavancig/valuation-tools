import pandas as pd
import numpy as np

class ConstantRatioDeltaNWC:
    
    def __init__(self, pastRevenueStreams, pastDeltaNWCStreams):
        # Filter out NaN values to calculate ratio only from valid data
        validRevenue = pastRevenueStreams.dropna()
        validDeltaNWC = pastDeltaNWCStreams.dropna()
        
        # Only use dates that have both valid revenue and deltaNWC data
        commonDates = validRevenue.index.intersection(validDeltaNWC.index)
        
        if len(commonDates) == 0:
            # Fallback to a reasonable ratio if no valid data
            self._deltaNWCRatio = 0.05  # 5% as fallback (typical deltaNWC to revenue ratio)
            return
            
        nYears = 0
        deltaNWCRatioSum = 0
        for date in commonDates:
            if pd.notna(pastRevenueStreams[date]) and pd.notna(pastDeltaNWCStreams[date]):
                nYears = nYears + 1
                # Calculate ratio of deltaNWC to revenue
                deltaNWCRatioSum = deltaNWCRatioSum + pastDeltaNWCStreams[date]/pastRevenueStreams[date]
        
        if nYears > 0:
            self._deltaNWCRatio = deltaNWCRatioSum/nYears
        else:
            # Fallback to a reasonable ratio if no valid data
            self._deltaNWCRatio = 0.05  # 5% as fallback (typical deltaNWC to revenue ratio)

    def setDeltaNWCRatio(self, ratio):
        self._deltaNWCRatio = ratio

    def getDeltaNWCStreams(self, revenueStreams, pastDeltaNWCStreams):
        # Filter out NaN values from past deltaNWC streams to match the filtered revenue data
        validPastDeltaNWCStreams = pastDeltaNWCStreams.dropna()
        
        if validPastDeltaNWCStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()

        # Handle both Series and DataFrame inputs
        if hasattr(validPastDeltaNWCStreams, 'values'):
            if len(validPastDeltaNWCStreams.values.shape) == 1:
                # It's a Series, use values directly
                deltaNWCStreamPredictions = pd.DataFrame([validPastDeltaNWCStreams.values], columns=validPastDeltaNWCStreams.index, index=['Delta NWC'])
            else:
                # It's a DataFrame, extract the first row
                deltaNWCStreamPredictions = pd.DataFrame([validPastDeltaNWCStreams.iloc[0].values], columns=validPastDeltaNWCStreams.columns, index=['Delta NWC'])
        else:
            # Fallback for other data types
            deltaNWCStreamPredictions = pd.DataFrame([validPastDeltaNWCStreams], columns=validPastDeltaNWCStreams.index, index=['Delta NWC'])

        for date in revenueStreams.columns.values:
            if(date in validPastDeltaNWCStreams):
                continue
            # Project deltaNWC based on revenue and historical ratio
            deltaNWCStreamPredictions.loc['Delta NWC', date] = revenueStreams.loc['Revenue', date] * self._deltaNWCRatio
            
        return deltaNWCStreamPredictions

    def getDeltaNWCRatioTable(self, predictedRevenue, predictedDeltaNWC):
        ratioPredictions = pd.DataFrame([], columns=predictedDeltaNWC.columns.values, index=['Delta NWC Ratio'])
        for date in predictedRevenue.columns.values:
            ratioPredictions.loc['Delta NWC Ratio', date] = predictedDeltaNWC.loc['Delta NWC', date] / predictedRevenue.loc['Revenue', date]
        return ratioPredictions
