# Base class for growth estimates

import pandas as pd
import numpy as np

class GrowthEstimatesBase:
    """
    Base class for handling growth rate estimates.
    Provides interface for getting growth rates for different time periods.
    """
    
    def __init__(self):
        pass
    
    def getGrowthTable(self, timeSeries):
        """
        Get growth rates for the specified time series.
        
        Args:
            timeSeries: pandas Index or list of time periods
            
        Returns:
            pandas DataFrame with growth rates for each time period
        """
        raise NotImplementedError("Please implement getGrowthTable method in concrete growth estimates class")
    
    def getGrowthRate(self, timePeriod, timeNow):
        """
        Get growth rate for a specific time period.
        
        Args:
            timePeriod: specific time period
            timeNow: current time reference
            
        Returns:
            float: growth rate for the specified period
        """
        raise NotImplementedError("Please implement getGrowthRate method in concrete growth estimates class")
    
    def getPessimisticGrowthTable(self, timeSeries):
        """
        Get pessimistic growth rates for the specified time series.
        
        Args:
            timeSeries: pandas Index or list of time periods
            
        Returns:
            pandas DataFrame with pessimistic growth rates for each time period
        """
        raise NotImplementedError("Please implement getPessimisticGrowthTable method in concrete growth estimates class")
    
    def getOptimisticGrowthTable(self, timeSeries):
        """
        Get optimistic growth rates for the specified time series.
        
        Args:
            timeSeries: pandas Index or list of time periods
            
        Returns:
            pandas DataFrame with optimistic growth rates for each time period
        """
        raise NotImplementedError("Please implement getOptimisticGrowthTable method in concrete growth estimates class")
