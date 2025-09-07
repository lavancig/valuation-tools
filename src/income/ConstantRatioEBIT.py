import pandas as pd
import numpy as np

class ConstantRatioEBIT:
    
    def __init__(self, pastRevenueStreams, pastEBITStreams):
        # Store original historical data for use in profitability calculations
        self._pastRevenueStreams = pastRevenueStreams.copy()
        self._pastEBITStreams = pastEBITStreams.copy()
        
        # Filter out NaN values to calculate ratio only from valid data
        validRevenue = pastRevenueStreams.dropna()
        validEBIT = pastEBITStreams.dropna()
        
        # Only use dates that have both valid revenue and EBIT data
        commonDates = validRevenue.index.intersection(validEBIT.index)
        
        if len(commonDates) == 0:
            # Fallback to a reasonable ratio if no valid data
            self._ebitRatio = 0.15  # 15% as fallback (typical EBIT to revenue ratio)
            return
            
        nYears = 0
        ebitRatioSum = 0
        for date in commonDates:
            if pd.notna(pastRevenueStreams[date]) and pd.notna(pastEBITStreams[date]):
                nYears = nYears + 1
                # Calculate ratio of EBIT to revenue
                ebitRatioSum = ebitRatioSum + pastEBITStreams[date]/pastRevenueStreams[date]
        
        if nYears > 0:
            self._ebitRatio = ebitRatioSum/nYears
        else:
            # Fallback to a reasonable ratio if no valid data
            self._ebitRatio = 0.15  # 15% as fallback (typical EBIT to revenue ratio)

    def setEBITRatio(self, ratio):
        self._ebitRatio = ratio

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
                averageProfitability = self._ebitRatio
        else:
            averageProfitability = self._ebitRatio
        
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

        # Handle both Series and DataFrame inputs
        if hasattr(validPastEBITStreams, 'values'):
            if len(validPastEBITStreams.values.shape) == 1:
                # It's a Series, use values directly
                # Convert dates to end of year
                end_of_year_dates = []
                for date in validPastEBITStreams.index:
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
                
                ebitStreamPredictions = pd.DataFrame([validPastEBITStreams.values], columns=end_of_year_dates, index=['EBIT'])
            else:
                # It's a DataFrame, extract the first row
                # Convert dates to end of year
                end_of_year_dates = []
                for date in validPastEBITStreams.columns:
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
                
                ebitStreamPredictions = pd.DataFrame([validPastEBITStreams.iloc[0].values], columns=end_of_year_dates, index=['EBIT'])
        else:
            # Fallback for other data types
            # Convert dates to end of year
            end_of_year_dates = []
            for date in validPastEBITStreams.index:
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
            
            ebitStreamPredictions = pd.DataFrame([validPastEBITStreams], columns=end_of_year_dates, index=['EBIT'])

        # Calculate future EBIT using profitability table
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
            
            if end_of_year_date in ebitStreamPredictions.columns:
                continue  # Keep historical data as is
            # Use profitability from table to calculate EBIT
            profitability = profitabilityTable.loc['EBIT Margin', date]
            revenue = revenueStreams.loc['Revenue', date]
            ebitStreamPredictions.loc['EBIT', end_of_year_date] = revenue * profitability
            
        return ebitStreamPredictions

    def getEBITRatioTable(self, predictedRevenue, predictedEBIT):
        """Get EBIT ratio table - this method now just returns the pre-calculated profitability table"""
        # Use the same logic as calculateProfitabilityTable but with the predicted data
        return self.calculateProfitabilityTable(predictedRevenue, predictedEBIT)
