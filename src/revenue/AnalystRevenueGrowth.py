from pandas.core.indexes.base import Index
from .RevenueBase import RevenueBase
import pandas as pd
import numpy as np 
import copy

class AnalystRevenueGrowth(RevenueBase):
    
    def __init__(self, analystEstimates, perpetualGrowthRate, timeNow):
        self._analystEstimates = analystEstimates
        self._perpetualGrowthRate = perpetualGrowthRate
        self._timeNow = timeNow
        
        # Create pessimistic and optimistic growth estimates
        self._pessimisticEstimates = self._createPessimisticEstimates()
        self._optimisticEstimates = self._createOptimisticEstimates()
    
    def _createPessimisticEstimates(self):
        """Create pessimistic growth estimates (lower than analyst estimates)"""
        pessimistic = {}
        if '0Y' in self._analystEstimates.index:
            pessimistic['0Y'] = self._analystEstimates.loc['0Y'] * 0.7  # 30% lower
        if '+1Y' in self._analystEstimates.index:
            pessimistic['+1Y'] = self._analystEstimates.loc['+1Y'] * 0.7  # 30% lower
        if '+5Y' in self._analystEstimates.index:
            pessimistic['+5Y'] = self._analystEstimates.loc['+5Y'] * 0.7  # 30% lower
        
        # Fill missing values with economy growth
        if '0Y' not in pessimistic:
            pessimistic['0Y'] = self._perpetualGrowthRate * 0.7
        if '+1Y' not in pessimistic:
            pessimistic['+1Y'] = self._perpetualGrowthRate * 0.7
        if '+5Y' not in pessimistic:
            pessimistic['+5Y'] = self._perpetualGrowthRate * 0.7
            
        return pd.Series(pessimistic)
    
    def _createOptimisticEstimates(self):
        """Create optimistic growth estimates (higher than analyst estimates)"""
        optimistic = {}
        if '0Y' in self._analystEstimates.index:
            optimistic['0Y'] = self._analystEstimates.loc['0Y'] * 1.3  # 30% higher
        if '+1Y' in self._analystEstimates.index:
            optimistic['+1Y'] = self._analystEstimates.loc['+1Y'] * 1.3  # 30% higher
        if '+5Y' in self._analystEstimates.index:
            optimistic['+5Y'] = self._analystEstimates.loc['+5Y'] * 1.3  # 30% higher
        
        # Fill missing values with economy growth
        if '0Y' not in optimistic:
            optimistic['0Y'] = self._perpetualGrowthRate * 1.3
        if '+1Y' not in optimistic:
            optimistic['+1Y'] = self._perpetualGrowthRate * 1.3
        if '+5Y' not in optimistic:
            optimistic['+5Y'] = self._perpetualGrowthRate * 1.3
            
        return pd.Series(optimistic)

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
            
            timeDistance = np.datetime64(nextTime, 'Y') - np.datetime64(self._timeNow, 'Y')
            growthRate = 0
            if timeDistance.astype(int) == 1:
                growthRate = self._analystEstimates.loc['0Y']
            elif timeDistance.astype(int) == 2:
                growthRate = self._analystEstimates.loc['+1Y']
            elif (timeDistance.astype(int) > 2) and (timeDistance.astype(int) <= 7):
                growthRate = self._analystEstimates.loc['+5Y']
            else:
                growthRate = self._perpetualGrowthRate
            
            lastRevenue = revenueStreamPredictions.loc['Revenue', currentTime]
            revenueStreamPredictions.loc['Revenue', nextTime] = lastRevenue * (1 + growthRate)
            currentTime = nextTime
            
        # Add perpetual value with safety checks
        lastRevenue = revenueStreamPredictions.loc['Revenue', currentTime]
        
        # Ensure perpetual growth rate is less than discount rate for valid calculation
        if perpetualDiscount <= self._perpetualGrowthRate:
            # If growth rate >= discount rate, use a capped growth rate
            safeGrowthRate = perpetualDiscount * 0.9  # Use 90% of discount rate
            print(f"Warning: Perpetual growth rate ({self._perpetualGrowthRate:.4f}) >= discount rate ({perpetualDiscount:.4f}). Using safe growth rate: {safeGrowthRate:.4f}")
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
    
    def getPessimisticRevenueStreams(self, knownRevenueStreams, untilTime, perpetualDiscount):
        """Get revenue streams using pessimistic growth estimates"""
        return self._getRevenueStreamsWithEstimates(knownRevenueStreams, untilTime, perpetualDiscount, self._pessimisticEstimates)
    
    def getOptimisticRevenueStreams(self, knownRevenueStreams, untilTime, perpetualDiscount):
        """Get revenue streams using optimistic growth estimates"""
        return self._getRevenueStreamsWithEstimates(knownRevenueStreams, untilTime, perpetualDiscount, self._optimisticEstimates)
    
    def _getRevenueStreamsWithEstimates(self, knownRevenueStreams, untilTime, perpetualDiscount, estimates):
        """Helper method to get revenue streams with specific growth estimates"""
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
            
            timeDistance = np.datetime64(nextTime, 'Y') - np.datetime64(self._timeNow, 'Y')
            growthRate = 0
            if timeDistance.astype(int) == 1:
                growthRate = estimates.loc['0Y']
            elif timeDistance.astype(int) == 2:
                growthRate = estimates.loc['+1Y']
            elif (timeDistance.astype(int) > 2) and (timeDistance.astype(int) <= 7):
                growthRate = estimates.loc['+5Y']
            else:
                growthRate = self._perpetualGrowthRate
            
            lastRevenue = revenueStreamPredictions.loc['Revenue', currentTime]
            revenueStreamPredictions.loc['Revenue', nextTime] = lastRevenue * (1 + growthRate)
            currentTime = nextTime
            
        # Add perpetual value with safety checks
        lastRevenue = revenueStreamPredictions.loc['Revenue', currentTime]
        
        # Ensure perpetual growth rate is less than discount rate for valid calculation
        if perpetualDiscount <= self._perpetualGrowthRate:
            # If growth rate >= discount rate, use a capped growth rate
            safeGrowthRate = perpetualDiscount * 0.9  # Use 90% of discount rate
            print(f"Warning: Perpetual growth rate ({self._perpetualGrowthRate:.4f}) >= discount rate ({perpetualDiscount:.4f}). Using safe growth rate: {safeGrowthRate:.4f}")
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
                # Calculate time distance from current time
                timeDistance = np.datetime64(col, 'Y') - np.datetime64(self._timeNow, 'Y')
                if timeDistance.astype(int) == 1:
                    growthRates.loc['Revenue Growth Rate', col] = self._analystEstimates.loc['0Y']
                elif timeDistance.astype(int) == 2:
                    growthRates.loc['Revenue Growth Rate', col] = self._analystEstimates.loc['+1Y']
                elif (timeDistance.astype(int) > 2) and (timeDistance.astype(int) <= 7):
                    growthRates.loc['Revenue Growth Rate', col] = self._analystEstimates.loc['+5Y']
                else:
                    growthRates.loc['Revenue Growth Rate', col] = self._perpetualGrowthRate
        
        return growthRates


