from .RevenueBase import RevenueBase
import pandas as pd
import numpy as np 
import copy

class ConstantGrowthRevenue(RevenueBase):
    
    def __init__(self, growthRate, perpetualGrowthRate):
        self._growthRate = growthRate
        self._perpetualGrowthRate = perpetualGrowthRate

    def getRevenueStreams(self, knownRevenueStreams, untilTime, perpetualDiscount):
        # Filter out years with NaN values to avoid propagating NaN through calculations
        validRevenueStreams = knownRevenueStreams.dropna()
        
        if validRevenueStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()
        
        # Create a proper chronological sequence: historical years first, then future years
        # Start with the most recent historical year (first column)
        startTime = validRevenueStreams.index.values[0]
        
        if untilTime <= startTime:
            return validRevenueStreams

        # Create DataFrame with historical data in chronological order (oldest to newest)
        historicalData = validRevenueStreams.sort_index(ascending=True)
        revenueStreamPredictions = pd.DataFrame([historicalData.values], columns=historicalData.index, index=['Revenue'])

        # Add future years starting from the year after the most recent historical year
        currentTime = startTime
        while True:
            nextTime = np.add(currentTime, np.timedelta64(1, 'Y'), casting="unsafe")
            if untilTime <= nextTime:
                break
            
            lastRevenue = revenueStreamPredictions.loc['Revenue', currentTime]
            revenueStreamPredictions.loc['Revenue', nextTime] = lastRevenue * (1 + self._growthRate)
            currentTime = nextTime
            
        # Add perpetual value with safety checks
        lastRevenue = revenueStreamPredictions.loc['Revenue', currentTime]
        
        # Ensure perpetual growth rate is less than discount rate for valid calculation
        if perpetualDiscount <= self._perpetualGrowthRate:
            # If growth rate >= discount rate, use a capped growth rate
            safeGrowthRate = perpetualDiscount * 0.9  # Use 90% of discount rate
            print(f"Warning: Perpetual growth rate ({self._perpetualGrowthRate:.3f}) >= discount rate ({perpetualDiscount:.3f}). Using safe growth rate: {safeGrowthRate:.3f}")
        else:
            safeGrowthRate = self._perpetualGrowthRate
        
        # Calculate perpetual value with safe parameters
        perpetualValue = lastRevenue * (1 + safeGrowthRate) / (perpetualDiscount - safeGrowthRate)
        
        # Ensure perpetual value is positive
        if perpetualValue <= 0:
            print(f"Warning: Calculated perpetual value is {perpetualValue:.2f}. Using last revenue as fallback.")
            perpetualValue = lastRevenue
        
        revenueStreamPredictions.loc['Revenue', 'perpetual'] = perpetualValue
        return revenueStreamPredictions

    def getGrowthRates(self, timeSeries):
        """Get the growth rates used for each time period"""
        growthRates = pd.DataFrame(index=['Revenue Growth Rate'], columns=timeSeries)
        
        for col in timeSeries:
            if col == 'perpetual':
                growthRates.loc['Revenue Growth Rate', col] = self._perpetualGrowthRate
            else:
                growthRates.loc['Revenue Growth Rate', col] = self._growthRate
        
        return growthRates


