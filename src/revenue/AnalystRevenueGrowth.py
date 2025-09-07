from pandas.core.indexes.base import Index
from .RevenueBase import RevenueBase
import pandas as pd
import numpy as np 
import copy

class RevenueForecast(RevenueBase):
    """
    Simple revenue forecast class that applies growth estimates to predict revenue.
    Takes growth estimates from the growth class and applies them to historical revenue data.
    """
    
    def __init__(self):
        """Initialize the revenue forecast class"""
        pass

    def getRevenueStreams(self, knownRevenueStreams, untilTime, perpetualDiscount, growthEstimatesTable):
        """
        Get revenue streams based on growth estimates table.
        
        Args:
            knownRevenueStreams: Historical revenue data
            untilTime: End time for predictions
            perpetualDiscount: Discount rate for perpetual value calculation
            growthEstimatesTable: DataFrame with growth rates for each time period (required)
        """
        if growthEstimatesTable is None:
            raise ValueError("Growth estimates table is required for revenue forecasting")
        
        # Filter out years with NaN values to avoid propagating NaN through calculations
        validRevenueStreams = knownRevenueStreams.dropna()
        
        if validRevenueStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()
        
        # Create a proper chronological sequence: historical years first, then future years
        # Start with the most recent historical year (first column)
        startTime = validRevenueStreams.index.values[0]
        
        # Convert untilTime to pandas Timestamp for consistent comparison
        untilTime = pd.Timestamp(untilTime)
        
        if untilTime <= startTime:
            return validRevenueStreams

        # Create DataFrame with historical data in chronological order (oldest to newest)
        # Normalize historical dates to year-end for consistency
        historicalData = validRevenueStreams.sort_index(ascending=True)
        normalizedHistoricalData = {}
        for date, value in historicalData.items():
            year = pd.Timestamp(date).year
            normalizedDate = pd.Timestamp(f"{year}-12-31")
            normalizedHistoricalData[normalizedDate] = value
        
        revenueStreamPredictions = pd.DataFrame([list(normalizedHistoricalData.values())], 
                                              columns=list(normalizedHistoricalData.keys()), 
                                              index=['Revenue'])

        # Add future years starting from the year after the most recent historical year
        # Use the normalized start time (year-end of the most recent historical year)
        startTimeYear = pd.Timestamp(startTime).year
        currentTime = pd.Timestamp(f"{startTimeYear}-12-31")
        while True:
            # Add one year to current time using pandas
            nextTime = currentTime + pd.DateOffset(years=1)
            if untilTime <= nextTime:
                break
            
            # Normalize nextTime to year-end for consistent lookup
            nextTimeYear = pd.Timestamp(nextTime).year
            nextTimeNormalized = pd.Timestamp(f"{nextTimeYear}-12-31")
            
            # Get growth rate from growth estimates table using normalized date
            if nextTimeNormalized in growthEstimatesTable.columns:
                growthRate = growthEstimatesTable.loc['Growth Rate', nextTimeNormalized]
            else:
                raise ValueError(f"Growth rate not found for time period {nextTimeNormalized} in growth estimates table")
            
            lastRevenue = revenueStreamPredictions.loc['Revenue', currentTime]
            revenueStreamPredictions.loc['Revenue', nextTime] = lastRevenue * (1 + growthRate)
            currentTime = nextTime
            
        # Add perpetual value with safety checks
        lastRevenue = revenueStreamPredictions.loc['Revenue', currentTime]
        
        # Get perpetual growth rate from growth estimates table
        if 'perpetual' in growthEstimatesTable.columns:
            perpetualGrowthRate = growthEstimatesTable.loc['Growth Rate', 'perpetual']
        else:
            raise ValueError("Perpetual growth rate not found in growth estimates table")
        
        # Ensure perpetual growth rate is less than discount rate for valid calculation
        if perpetualDiscount <= perpetualGrowthRate:
            # If growth rate >= discount rate, use a capped growth rate
            safeGrowthRate = perpetualDiscount * 0.9  # Use 90% of discount rate
            print(f"Warning: Perpetual growth rate ({perpetualGrowthRate:.3f}) >= discount rate ({perpetualDiscount:.3f}). Using safe growth rate: {safeGrowthRate:.3f}")
        else:
            safeGrowthRate = perpetualGrowthRate
        
        # Calculate perpetual value with safe parameters
        perpetualValue = lastRevenue * (1 + safeGrowthRate) / (perpetualDiscount - safeGrowthRate)
        
        # Ensure perpetual value is positive
        if perpetualValue <= 0:
            print(f"Warning: Calculated perpetual value is {perpetualValue:.2f}. Using last revenue as fallback.")
            perpetualValue = lastRevenue
        
        revenueStreamPredictions.loc['Revenue', 'perpetual'] = perpetualValue
        return revenueStreamPredictions
    


