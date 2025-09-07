import pandas as pd
import numpy as np

class TaxRateCalculator:
    """Calculate tax rates from historical financial data"""
    
    def __init__(self, financialData):
        """
        Initialize with financial data
        
        Args:
            financialData: DataFrame containing financial statements data
        """
        # Convert dates to end of year format
        self._financialData = self._convertDatesToEndOfYear(financialData)
        self._averageTaxRate = self._calculateAverageTaxRate()
    
    def _convertDatesToEndOfYear(self, financialData):
        """Convert all dates in the financial data to end of year format"""
        # Create a copy of the financial data
        converted_data = financialData.copy()
        
        # Convert column names (dates) to end of year
        end_of_year_columns = []
        for date in financialData.columns:
            if hasattr(date, 'year'):
                # If it's already a datetime, set to end of year
                end_of_year_columns.append(pd.Timestamp(f"{date.year}-12-31"))
            else:
                # If it's a string or other format, try to parse and set to end of year
                try:
                    parsed_date = pd.Timestamp(date)
                    end_of_year_columns.append(pd.Timestamp(f"{parsed_date.year}-12-31"))
                except:
                    end_of_year_columns.append(date)  # Fallback to original date
        
        # Update the column names
        converted_data.columns = end_of_year_columns
        
        return converted_data
    
    def _calculateAverageTaxRate(self):
        """Calculate average tax rate from historical data"""
        taxRates = []
        
        for date in self._financialData.columns:
            try:
                taxProvision = self._financialData.loc['Tax Provision', date]
                pretaxIncome = self._financialData.loc['Pretax Income', date]
                
                if (pretaxIncome != 0 and 
                    not pd.isna(pretaxIncome) and 
                    not pd.isna(taxProvision) and
                    pretaxIncome > 0):  # Only consider positive pretax income
                    
                    taxRate = abs(taxProvision) / abs(pretaxIncome)
                    # Ensure tax rate is reasonable (between 0 and 1)
                    taxRate = max(0.0, min(0.4, taxRate))
                    taxRates.append(taxRate)
                    
            except (KeyError, ZeroDivisionError):
                continue  # Skip this year if data is missing
        
        if taxRates:
            return np.mean(taxRates)
        else:
            # Fallback to reasonable default if no valid data
            return 0.25  # 25% corporate tax rate as fallback
    
    def getAverageTaxRate(self):
        """Get the calculated average tax rate"""
        return self._averageTaxRate
    
    def getTaxRateTable(self, timeSeries):
        """
        Get tax rate table for a given time series
        
        Args:
            timeSeries: DatetimeIndex or list of dates
            
        Returns:
            DataFrame with tax rates for each date
        """
        taxRateTable = pd.DataFrame(index=['Tax Rate'], columns=timeSeries)
        
        for date in timeSeries:
            # Convert date to end of year format
            if hasattr(date, 'year'):
                end_of_year_date = pd.Timestamp(f"{date.year}-12-31")
            else:
                try:
                    parsed_date = pd.Timestamp(date)
                    end_of_year_date = pd.Timestamp(f"{parsed_date.year}-12-31")
                except:
                    end_of_year_date = date  # Fallback to original date
            
            # For historical dates, try to get actual tax rate
            if end_of_year_date in self._financialData.columns:
                try:
                    taxProvision = self._financialData.loc['Tax Provision', end_of_year_date]
                    pretaxIncome = self._financialData.loc['Pretax Income', end_of_year_date]
                    
                    if (pretaxIncome != 0 and 
                        not pd.isna(pretaxIncome) and 
                        not pd.isna(taxProvision) and
                        pretaxIncome > 0):
                        
                        taxRate = abs(taxProvision) / abs(pretaxIncome)
                        taxRate = max(0.0, min(0.4, taxRate))
                        taxRateTable.loc['Tax Rate', date] = taxRate
                    else:
                        # Use average if no valid data for this year
                        taxRateTable.loc['Tax Rate', date] = self._averageTaxRate
                        
                except (KeyError, ZeroDivisionError):
                    # Use average if data is missing
                    taxRateTable.loc['Tax Rate', date] = self._averageTaxRate
            else:
                # For future dates, use average tax rate
                taxRateTable.loc['Tax Rate', date] = self._averageTaxRate
        
        return taxRateTable
    
    def getTaxRateForDate(self, date):
        """
        Get tax rate for a specific date
        
        Args:
            date: Date to get tax rate for
            
        Returns:
            float: Tax rate for the date
        """
        # Convert input date to end of year format
        if hasattr(date, 'year'):
            end_of_year_date = pd.Timestamp(f"{date.year}-12-31")
        else:
            try:
                parsed_date = pd.Timestamp(date)
                end_of_year_date = pd.Timestamp(f"{parsed_date.year}-12-31")
            except:
                end_of_year_date = date  # Fallback to original date
        
        if end_of_year_date in self._financialData.columns:
            try:
                taxProvision = self._financialData.loc['Tax Provision', end_of_year_date]
                pretaxIncome = self._financialData.loc['Pretax Income', end_of_year_date]
                
                if (pretaxIncome != 0 and 
                    not pd.isna(pretaxIncome) and 
                    not pd.isna(taxProvision) and
                    pretaxIncome > 0):
                    
                    taxRate = abs(taxProvision) / abs(pretaxIncome)
                    return max(0.0, min(0.4, taxRate))
                else:
                    return self._averageTaxRate
                    
            except (KeyError, ZeroDivisionError):
                return self._averageTaxRate
        else:
            # For future dates, use average tax rate
            return self._averageTaxRate
