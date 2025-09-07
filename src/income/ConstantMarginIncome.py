from .IncomeBase import IncomeBase
import pandas as pd
import numpy as np 
import copy

class ConstantMarginIncome(IncomeBase):
    
    def __init__(self, pastRevenueStreams, pastIncomeStreams):
        # Store original historical data for use in profitability calculations
        self._pastRevenueStreams = pastRevenueStreams.copy()
        self._pastIncomeStreams = pastIncomeStreams.copy()
        
        # Filter out NaN values to calculate margin only from valid data
        validRevenue = pastRevenueStreams.dropna()
        validIncome = pastIncomeStreams.dropna()
        
        # Only use dates that have both valid revenue and income data
        commonDates = validRevenue.index.intersection(validIncome.index)
        
        if len(commonDates) == 0:
            # Fallback to a reasonable margin if no valid data
            self._incomeMargin = 0.25  # 25% as fallback
            return
            
        nYears = 0
        incomeMarginSum = 0
        for date in commonDates:
            if pd.notna(pastRevenueStreams[date]) and pd.notna(pastIncomeStreams[date]):
                nYears = nYears + 1
                incomeMarginSum = incomeMarginSum + pastIncomeStreams[date]/pastRevenueStreams[date]
        
        if nYears > 0:
            self._incomeMargin = incomeMarginSum/nYears
        else:
            # Fallback to a reasonable margin if no valid data
            self._incomeMargin = 0.25  # 25% as fallback

    def setProfitability(self, profitablity):
        self._incomeMargin = profitablity

    def getIncomeStreams(self, revenueStreams, pastIncomeStreams):
        # First, calculate the profitability table
        profitabilityTable = self.calculateProfitabilityTable(revenueStreams, pastIncomeStreams)
        
        # Then use profitability table to calculate income
        return self.calculateIncomeFromProfitability(revenueStreams, profitabilityTable, pastIncomeStreams)
    
    def calculateProfitabilityTable(self, revenueStreams, pastIncomeStreams):
        """Calculate profitability table with actual past values and projected future values"""
        profitabilityTable = pd.DataFrame([], columns=revenueStreams.columns.values, index=['Profitability'])
        
        # Calculate average profitability from past years
        # Use input parameter for income data and convert dates to end of year format
        validPastIncomeStreams = pastIncomeStreams.dropna()
        
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
        
        # Convert both income and revenue streams to end of year format
        validPastIncomeStreams = convert_to_end_of_year(validPastIncomeStreams)
        
        # Find common dates with valid data
        commonDates = validPastIncomeStreams.index.intersection(revenueStreams.columns)
        
        if len(commonDates) > 0:
            # Calculate average profitability from historical data
            totalProfitability = 0
            validYears = 0
            for date in commonDates:
                if (pd.notna(validPastIncomeStreams[date]) and 
                    pd.notna(revenueStreams[date]['Revenue']) and 
                    revenueStreams[date]['Revenue'] != 0):
                    totalProfitability += validPastIncomeStreams[date] / revenueStreams[date]['Revenue']
                    validYears += 1
            
            if validYears > 0:
                averageProfitability = totalProfitability / validYears
            else:
                averageProfitability = self._incomeMargin
        else:
            averageProfitability = self._incomeMargin
        
        # Fill profitability table
        for date in revenueStreams.columns.values:
            if date in validPastIncomeStreams.index and date in revenueStreams.columns:
                # Use actual historical profitability for past years
                if (pd.notna(validPastIncomeStreams[date]) and 
                    pd.notna(revenueStreams[date]['Revenue']) and 
                    revenueStreams[date]['Revenue'] != 0):
                    profitabilityTable.loc['Profitability', date] = validPastIncomeStreams[date] / revenueStreams[date]['Revenue']
                else:
                    profitabilityTable.loc['Profitability', date] = averageProfitability
            else:
                # Use average profitability for future years
                profitabilityTable.loc['Profitability', date] = averageProfitability
        
        return profitabilityTable
    
    def calculateIncomeFromProfitability(self, revenueStreams, profitabilityTable, pastIncomeStreams):
        """Calculate income using profitability table and revenue streams"""
        # Filter out NaN values from past income streams
        validPastIncomeStreams = pastIncomeStreams.dropna()
        
        if validPastIncomeStreams.empty:
            # If no valid data, return empty DataFrame
            return pd.DataFrame()

        # Convert dates to end of year format
        end_of_year_dates = []
        for date in validPastIncomeStreams.index:
            if hasattr(date, 'year'):
                # If it's already a datetime, set to end of year
                end_of_year_dates.append(pd.Timestamp(f"{date.year}-12-31"))
            else:
                # If it's a string or other format, try to parse and set to end of year
                try:
                    parsed_date = pd.Timestamp(date)
                    end_of_year_dates.append(pd.Timestamp(f"{parsed_date.year}-12-31"))
                except:
                    end_of_year_dates.append(date)  # Fallback to original date
        
        # Start with historical income data using end of year dates
        incomeStreamPredictions = pd.DataFrame([validPastIncomeStreams.values], columns=end_of_year_dates, index=['Income'])

        # Calculate future income using profitability table
        for date in revenueStreams.columns.values:
            # Convert date to end of year for consistency
            if hasattr(date, 'year'):
                end_of_year_date = pd.Timestamp(f"{date.year}-12-31")
            else:
                try:
                    parsed_date = pd.Timestamp(date)
                    end_of_year_date = pd.Timestamp(f"{parsed_date.year}-12-31")
                except:
                    end_of_year_date = date  # Fallback to original date
            
            if end_of_year_date in incomeStreamPredictions.columns:
                continue  # Keep historical data as is
            # Use profitability from table to calculate income
            profitability = profitabilityTable.loc['Profitability', date]
            revenue = revenueStreams.loc['Revenue', date]
            incomeStreamPredictions.loc['Income', end_of_year_date] = revenue * profitability
            
        return incomeStreamPredictions

    def getProfitabilityTable(self, predictedRevenue, predictedIncome):
        """Get profitability table - this method now just returns the pre-calculated profitability table"""
        # Use the same logic as calculateProfitabilityTable but with the predicted data
        return self.calculateProfitabilityTable(predictedRevenue, predictedIncome)