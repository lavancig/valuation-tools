from .IncomeBase import IncomeBase
import pandas as pd
import numpy as np 
import copy

class ConstantMarginEBIT(IncomeBase):
    
    def __init__(self, pastRevenueStreams, pastEBITStreams):
        # Store original historical data for use in profitability calculations
        self._pastRevenueStreams = pastRevenueStreams.copy()
        self._pastEBITStreams = pastEBITStreams.copy()
        
        # Filter out NaN values to calculate margin only from valid data
        validRevenue = pastRevenueStreams.dropna()
        validEBIT = pastEBITStreams.dropna()
        
        # Only use dates that have both valid revenue and EBIT data
        commonDates = validRevenue.index.intersection(validEBIT.index)
        
        if len(commonDates) == 0:
            # Fallback to a reasonable margin if no valid data
            self._ebitMargin = 0.15  # 15% as fallback (typical EBIT margin)
            return
            
        nYears = 0
        ebitMarginSum = 0
        for date in commonDates:
            if pd.notna(pastRevenueStreams[date]) and pd.notna(pastEBITStreams[date]):
                nYears = nYears + 1
                ebitMarginSum = ebitMarginSum + pastEBITStreams[date]/pastRevenueStreams[date]
        
        if nYears > 0:
            self._ebitMargin = ebitMarginSum/nYears
        else:
            # Fallback to a reasonable margin if no valid data
            self._ebitMargin = 0.15  # 15% as fallback (typical EBIT margin)

    def setProfitability(self, profitability):
        self._ebitMargin = profitability

    def getEBITStreams(self, revenueStreams, pastEBITStreams):
        # First, calculate the profitability table
        profitabilityTable = self.calculateProfitabilityTable(revenueStreams, pastEBITStreams)
        
        # Then use profitability table to calculate EBIT
        return self.calculateEBITFromProfitability(revenueStreams, profitabilityTable, pastEBITStreams)
    
    def calculateProfitabilityTable(self, revenueStreams, pastEBITStreams):
        """Calculate profitability table with actual past values and projected future values"""
        profitabilityTable = pd.DataFrame([], columns=revenueStreams.columns.values, index=['EBIT Margin'])
        
        # Calculate average profitability from past years
        # Use input parameter for EBIT data and convert dates to end of year format
        validPastEBITStreams = pastEBITStreams.dropna()
        validPastRevenueStreams = revenueStreams.loc['Revenue'].dropna()
        
        # Convert dates to end of year format (December 31st)
        def convert_to_end_of_year(date_series):
            """Convert dates to end of year format"""
            if isinstance(date_series.index, pd.DatetimeIndex):
                # Convert to end of year (December 31st)
                end_of_year_dates = []
                for date in date_series.index:
                    year = date.year
                    end_of_year = pd.Timestamp(f"{year}-12-31")
                    end_of_year_dates.append(end_of_year)
                return pd.Series(date_series.values, index=end_of_year_dates)
            else:
                # If not datetime index, assume it's already in the right format
                return date_series
        
        # Convert both EBIT and revenue streams to end of year format
        validPastEBITStreams = convert_to_end_of_year(validPastEBITStreams)
        validPastRevenueStreams = convert_to_end_of_year(validPastRevenueStreams)
        
        # Find common dates with valid data
        commonDates = validPastEBITStreams.index.intersection(validPastRevenueStreams.index)
        
        if len(commonDates) > 0:
            # Calculate average profitability from historical data
            totalProfitability = 0
            validYears = 0
            for date in commonDates:
                if (pd.notna(validPastEBITStreams[date]) and 
                    pd.notna(validPastRevenueStreams[date]) and 
                    validPastRevenueStreams[date] != 0):
                    totalProfitability += validPastEBITStreams[date] / validPastRevenueStreams[date]
                    validYears += 1
            
            if validYears > 0:
                averageProfitability = totalProfitability / validYears
            else:
                averageProfitability = self._ebitMargin
        else:
            averageProfitability = self._ebitMargin
        
        # Fill profitability table
        for date in revenueStreams.columns.values:
            if date in validPastEBITStreams.index and date in validPastRevenueStreams.index:
                # Use actual historical profitability for past years
                if (pd.notna(validPastEBITStreams[date]) and 
                    pd.notna(validPastRevenueStreams[date]) and 
                    validPastRevenueStreams[date] != 0):
                    profitabilityTable.loc['EBIT Margin', date] = validPastEBITStreams[date] / validPastRevenueStreams[date]
                else:
                    profitabilityTable.loc['EBIT Margin', date] = averageProfitability
            else:
                # Use average profitability for future years
                profitabilityTable.loc['EBIT Margin', date] = averageProfitability
        
        return profitabilityTable
    
    def calculateEBITFromProfitability(self, revenueStreams, profitabilityTable, pastEBITStreams):
        """Calculate EBIT using profitability table and revenue streams"""
        # Filter out NaN values from past EBIT streams
        validPastEBITStreams = pastEBITStreams.dropna()
        
        if validPastEBITStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()

        # Start with historical EBIT data
        ebitStreamPredictions = pd.DataFrame([validPastEBITStreams.values], columns=validPastEBITStreams.index, index=['EBIT'])

        # Calculate future EBIT using profitability table
        for date in revenueStreams.columns.values:
            if date in validPastEBITStreams.index:
                continue  # Keep historical data as is
            # Use profitability from table to calculate EBIT
            profitability = profitabilityTable.loc['EBIT Margin', date]
            revenue = revenueStreams.loc['Revenue', date]
            ebitStreamPredictions.loc['EBIT', date] = revenue * profitability
            
        return ebitStreamPredictions

    def getProfitabilityTable(self, predictedRevenue, predictedEBIT):
        """Get profitability table - this method now just returns the pre-calculated profitability table"""
        # Use the same logic as calculateProfitabilityTable but with the predicted data
        return self.calculateProfitabilityTable(predictedRevenue, predictedEBIT)
