from .GrowthEstimatesBase import GrowthEstimatesBase
import pandas as pd
import numpy as np

class AnalystGrowthEstimates(GrowthEstimatesBase):
    """
    Growth estimates class that extracts and manages analyst growth estimates from Yahoo Finance.
    Provides realistic, pessimistic, and optimistic growth scenarios.
    """
    
    def __init__(self, analystEstimates, perpetualGrowthRate, timeNow):
        """
        Initialize with analyst estimates and perpetual growth rate.
        
        Args:
            analystEstimates: pandas Series with analyst growth estimates
            perpetualGrowthRate: long-term perpetual growth rate
            timeNow: current time reference
        """
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
    
    def getGrowthTable(self, timeSeries):
        """Get growth rates for the specified time series using realistic estimates"""
        return self._getGrowthTableWithEstimates(timeSeries, self._analystEstimates)
    
    def getPessimisticGrowthTable(self, timeSeries):
        """Get pessimistic growth rates for the specified time series"""
        return self._getGrowthTableWithEstimates(timeSeries, self._pessimisticEstimates)
    
    def getOptimisticGrowthTable(self, timeSeries):
        """Get optimistic growth rates for the specified time series"""
        return self._getGrowthTableWithEstimates(timeSeries, self._optimisticEstimates)
    
    def _getGrowthTableWithEstimates(self, timeSeries, estimates):
        """
        Helper method to get growth rates with specific estimates.
        
        Args:
            timeSeries: pandas Index or list of time periods
            estimates: pandas Series with growth estimates to use
            
        Returns:
            pandas DataFrame with growth rates for each time period
        """
        # Ensure 'perpetual' is always included at the end
        if 'perpetual' not in timeSeries:
            timeSeries = timeSeries.union(['perpetual'])
        
        growthRates = pd.DataFrame(index=['Growth Rate'], columns=timeSeries)
        
        for col in timeSeries:
            if col == 'perpetual':
                growthRates.loc['Growth Rate', col] = round(self._perpetualGrowthRate, 3)
            else:
                # Calculate time distance from current time
                timeDistance = np.datetime64(col, 'Y') - np.datetime64(self._timeNow, 'Y')
                growthRate = self._getGrowthRateForTimeDistance(timeDistance, estimates)
                growthRates.loc['Growth Rate', col] = round(growthRate, 3)
        
        return growthRates
    
    def _getGrowthRateForTimeDistance(self, timeDistance, estimates, yearsInTransition=4):
        """
        Get growth rate based on time distance from current time.
        
        Args:
            timeDistance: numpy timedelta64 representing time distance
            estimates: pandas Series with growth estimates
            
        Returns:
            float: growth rate for the specified time distance
        """
        timeDistanceInt = timeDistance.astype(int)
        
        if timeDistanceInt == 0:
            return estimates.loc['0Y']
        elif timeDistanceInt == 1:
            return estimates.loc['+1Y']
        elif (timeDistanceInt >= 2) and (timeDistanceInt <= 5):
            # Linear reduction from +1Y to perpetual over years 3-7
            startGrowthRate = estimates.loc['+1Y']
            endGrowthRate = self._perpetualGrowthRate
            # yearsInTransition = 5  # Years 3-7 (5 years total)
            currentYearInTransition = timeDistanceInt - 2  # Year 3 = 1, Year 4 = 2, etc.
            
            # Linear interpolation
            reductionFactor = currentYearInTransition / yearsInTransition
            return startGrowthRate - (startGrowthRate - endGrowthRate) * reductionFactor
        elif (timeDistanceInt > 7):
            return self._perpetualGrowthRate
        else:
            return 0

    
    def getGrowthRate(self, timePeriod, timeNow):
        """
        Get growth rate for a specific time period.
        
        Args:
            timePeriod: specific time period
            timeNow: current time reference (unused, kept for interface compatibility)
            
        Returns:
            float: growth rate for the specified period
        """
        if timePeriod == 'perpetual':
            return self._perpetualGrowthRate
        
        timeDistance = np.datetime64(timePeriod, 'Y') - np.datetime64(self._timeNow, 'Y')
        return self._getGrowthRateForTimeDistance(timeDistance, self._analystEstimates)
    
    def getPessimisticGrowthRate(self, timePeriod, timeNow):
        """Get pessimistic growth rate for a specific time period"""
        if timePeriod == 'perpetual':
            return self._perpetualGrowthRate * 0.7
        
        timeDistance = np.datetime64(timePeriod, 'Y') - np.datetime64(self._timeNow, 'Y')
        return self._getGrowthRateForTimeDistance(timeDistance, self._pessimisticEstimates)
    
    def getOptimisticGrowthRate(self, timePeriod, timeNow):
        """Get optimistic growth rate for a specific time period"""
        if timePeriod == 'perpetual':
            return self._perpetualGrowthRate * 1.3
        
        timeDistance = np.datetime64(timePeriod, 'Y') - np.datetime64(self._timeNow, 'Y')
        return self._getGrowthRateForTimeDistance(timeDistance, self._optimisticEstimates)
