from .GrowthEstimatesBase import GrowthEstimatesBase
import pandas as pd
import numpy as np

class ConstantGrowthEstimates(GrowthEstimatesBase):
    """
    Growth estimates class that provides constant growth rates.
    """
    
    def __init__(self, growthRate, perpetualGrowthRate, timeNow):
        """
        Initialize with constant growth rate.
        
        Args:
            growthRate: constant growth rate to use
            perpetualGrowthRate: long-term perpetual growth rate
            timeNow: current time reference
        """
        self._growthRate = growthRate
        self._perpetualGrowthRate = perpetualGrowthRate
        self._timeNow = timeNow
    
    def getGrowthTable(self, timeSeries):
        """Get growth rates for the specified time series using constant growth rate"""
        # Ensure 'perpetual' is always included at the end
        if 'perpetual' not in timeSeries:
            timeSeries = timeSeries.union(['perpetual'])
        
        growthRates = pd.DataFrame(index=['Growth Rate'], columns=timeSeries)
        
        for col in timeSeries:
            if col == 'perpetual':
                growthRates.loc['Growth Rate', col] = round(self._perpetualGrowthRate, 3)
            else:
                growthRates.loc['Growth Rate', col] = round(self._growthRate, 3)
        
        return growthRates
    
    def getPessimisticGrowthTable(self, timeSeries):
        """Get pessimistic growth rates (lower than constant rate)"""
        # Ensure 'perpetual' is always included at the end
        if 'perpetual' not in timeSeries:
            timeSeries = timeSeries.union(['perpetual'])
        
        growthRates = pd.DataFrame(index=['Growth Rate'], columns=timeSeries)
        
        for col in timeSeries:
            if col == 'perpetual':
                growthRates.loc['Growth Rate', col] = round(self._perpetualGrowthRate * 0.7, 3)
            else:
                growthRates.loc['Growth Rate', col] = round(self._growthRate * 0.7, 3)
        
        return growthRates
    
    def getOptimisticGrowthTable(self, timeSeries):
        """Get optimistic growth rates (higher than constant rate)"""
        # Ensure 'perpetual' is always included at the end
        if 'perpetual' not in timeSeries:
            timeSeries = timeSeries.union(['perpetual'])
        
        growthRates = pd.DataFrame(index=['Growth Rate'], columns=timeSeries)
        
        for col in timeSeries:
            if col == 'perpetual':
                growthRates.loc['Growth Rate', col] = round(self._perpetualGrowthRate * 1.3, 3)
            else:
                growthRates.loc['Growth Rate', col] = round(self._growthRate * 1.3, 3)
        
        return growthRates
    
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
        return self._growthRate
    
    def getPessimisticGrowthRate(self, timePeriod, timeNow):
        """Get pessimistic growth rate for a specific time period"""
        if timePeriod == 'perpetual':
            return self._perpetualGrowthRate * 0.7
        return self._growthRate * 0.7
    
    def getOptimisticGrowthRate(self, timePeriod, timeNow):
        """Get optimistic growth rate for a specific time period"""
        if timePeriod == 'perpetual':
            return self._perpetualGrowthRate * 1.3
        return self._growthRate * 1.3
