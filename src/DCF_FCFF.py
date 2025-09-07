import numpy as np
import yfinance as yf
import pandas as pd
import copy 

# Handle both relative and absolute imports
try:
    from .globals import getGlobal
    from .revenue.ConstantGrowthRevenue import ConstantGrowthRevenue
    from .revenue.AnalystRevenueGrowth import RevenueForecast
    from .growth.AnalystGrowthEstimates import AnalystGrowthEstimates
    from .growth.ConstantGrowthEstimates import ConstantGrowthEstimates
    from .income.ConstantMarginIncome import ConstantMarginIncome
    from .income.ConstantRatioEBIT import ConstantRatioEBIT
    from .fcf.ConstantIncomeToFCF import ConstantIncomeToFCF
    from .fcf.ConstantRatioDandA import ConstantRatioDandA
    from .fcf.ConstantRatioCapEx import ConstantRatioCapEx
    from .fcf.ConstantRatioDeltaNWC import ConstantRatioDeltaNWC
    from .fcf.ConstantRatioNetBorrowings import ConstantRatioNetBorrowings
    from .discoundRate.ConstantDiscountRate import ConstantDiscountRate
    from .discoundRate.WACCDiscountRate import WACCDiscountRate
    from .discoundRate.CostOfEquityDiscountRate import CostOfEquityDiscountRate
    from .PresentValue import PresentValue
    from .tax.TaxRateCalculator import TaxRateCalculator
except ImportError:
    # Fallback to absolute imports when running as script
    from globals import getGlobal
    from revenue.ConstantGrowthRevenue import ConstantGrowthRevenue
    from revenue.AnalystRevenueGrowth import RevenueForecast
    from growth.AnalystGrowthEstimates import AnalystGrowthEstimates
    from growth.ConstantGrowthEstimates import ConstantGrowthEstimates
    from income.ConstantMarginIncome import ConstantMarginIncome
    from income.ConstantRatioEBIT import ConstantRatioEBIT
    from fcf.ConstantIncomeToFCF import ConstantIncomeToFCF
    from fcf.ConstantRatioDandA import ConstantRatioDandA
    from fcf.ConstantRatioCapEx import ConstantRatioCapEx
    from fcf.ConstantRatioDeltaNWC import ConstantRatioDeltaNWC
    from fcf.ConstantRatioNetBorrowings import ConstantRatioNetBorrowings
    from discoundRate.ConstantDiscountRate import ConstantDiscountRate
    from discoundRate.WACCDiscountRate import WACCDiscountRate
    from discoundRate.CostOfEquityDiscountRate import CostOfEquityDiscountRate
    from PresentValue import PresentValue
    from tax.TaxRateCalculator import TaxRateCalculator

# Calculates fair value based on free cash flow to firm
class DCF_FCFF:
    def __init__(self, companyTicker):
        self._successful = False
        self.downloadCompanyData(companyTicker)
        if(not self._successful):
            return

        # Revenue Projection Object
        # Extract growth estimates from the new yfinance API structure
        # growth_estimates = self._analysis.growth_estimates
        # if growth_estimates is not None and not growth_estimates.empty:
        #     # Create a Series with the expected index format
        #     growth_data = {}
        #     if '0y' in growth_estimates.index:
        #         growth_data['0Y'] = growth_estimates.loc['0y', 'stockTrend']
        #     if '+1y' in growth_estimates.index:
        #         growth_data['+1Y'] = growth_estimates.loc['+1y', 'stockTrend']
        #     if 'LTG' in growth_estimates.index and pd.notna(growth_estimates.loc['LTG', 'stockTrend']):
        #         growth_data['+5Y'] = growth_estimates.loc['LTG', 'stockTrend']
        #     else:
        #         # Fallback to a reasonable estimate if LTG is not available
        #         growth_data['+5Y'] = getGlobal('economyGrowth')
            
        #     growth_series = pd.Series(growth_data)
        # else:
        #     # Fallback to constant growth if no analyst estimates available
        #     growth_series = pd.Series({
        #         '0Y': getGlobal('economyGrowth'),
        #         '+1Y': getGlobal('economyGrowth'),
        #         '+5Y': getGlobal('economyGrowth')
        #     })

        # Initialize growth estimates object first
        self.setGrowthEstimates()
        
        # Initialize revenue object (will be updated to use growth estimates)
        self.setRevenueSpecialistEstimates()

        # Income Projection Object
        # Use the new yfinance API row names
        revenue_row = 'Total Revenue'  # This still exists
        net_income_row = 'Net Income From Continuing Operation Net Minority Interest'  # Updated row name
        
        self._incomeObj = ConstantMarginIncome(self._financialData.loc[revenue_row], self._financialData.loc[net_income_row])
        
        # EBIT Projection Object
        # Find EBIT data from income statement
        ebit_rows = ['EBIT', 'Operating Income', 'Operating Income Loss']
        ebit_row = None
        for row in ebit_rows:
            if row in self._financialData.index:
                ebit_row = row
                break
        
        if ebit_row is not None:
            self._ebitObj = ConstantRatioEBIT(self._financialData.loc[revenue_row], self._financialData.loc[ebit_row])
        else:
            # Create dummy EBIT data if not found
            dummy_ebit = pd.Series([0] * len(self._financialData.columns), index=self._financialData.columns)
            self._ebitObj = ConstantRatioEBIT(self._financialData.loc[revenue_row], dummy_ebit)
            self._dummy_ebit = dummy_ebit
        
        # Free cash flow to firm object
        self._fcfObj = ConstantIncomeToFCF(self._financialData, self._cashFlowData)
        
        # Forecasting objects for additional metrics
        # Handle missing data gracefully by checking if rows exist
        dandA_row = 'Depreciation And Amortization'
        if dandA_row not in self._cashFlowData.index:
            dandA_row = 'Depreciation'
        if dandA_row not in self._cashFlowData.index:
            dandA_row = 'Depreciation & Amortization'
        if dandA_row not in self._cashFlowData.index:
            # Create a dummy series if no D&A data found
            dandA_row = None
            dummy_da = pd.Series([0] * len(self._financialData.columns), index=self._financialData.columns)
        
        capex_row = 'Capital Expenditure'
        if capex_row not in self._cashFlowData.index:
            capex_row = 'Purchase of PP&E'
        if capex_row not in self._cashFlowData.index:
            capex_row = 'Capital Expenditures'
        if capex_row not in self._cashFlowData.index:
            # Create a dummy series if no CapEx data found
            capex_row = None
            dummy_capex = pd.Series([0] * len(self._financialData.columns), index=self._financialData.columns)
        
        # Create forecasting objects with proper error handling
        if dandA_row is not None:
            self._dandAObj = ConstantRatioDandA(self._financialData.loc[revenue_row], self._cashFlowData.loc[dandA_row])
        else:
            self._dandAObj = ConstantRatioDandA(self._financialData.loc[revenue_row], dummy_da)
            
        if capex_row is not None:
            self._capExObj = ConstantRatioCapEx(self._financialData.loc[revenue_row], self._cashFlowData.loc[capex_row])
        else:
            self._capExObj = ConstantRatioCapEx(self._financialData.loc[revenue_row], dummy_capex)
            
        self._deltaNWCObj = ConstantRatioDeltaNWC(self._financialData.loc[revenue_row], self._calculateDeltaNWC().iloc[0])
        self._netBorrowingsObj = ConstantRatioNetBorrowings(self._financialData.loc[revenue_row], self._calculateNetBorrowings().iloc[0])
        
        # Store row names for use in other methods
        self._dandA_row = dandA_row
        self._capex_row = capex_row
        self._ebit_row = ebit_row
        
        # Store dummy data if needed
        if dandA_row is None:
            self._dummy_da = dummy_da
        if capex_row is None:
            self._dummy_capex = dummy_capex

        # Discount Rate Object
        self._costOfEquity = getGlobal('RiskFreeInterestRate') + self._companyInfo['beta'] * (getGlobal('marketReturn') - getGlobal('RiskFreeInterestRate'))
        
        # Get current share price for equity calculation
        currentSharePrice = self._getCurrentSharePrice()
        sharesOutstanding = self._companyInfo.get('sharesOutstanding', 1)
        
        self.setDiscountWACC()
        # self.setDiscountCostOfEquity()


        # Present Value Object
        # self._presentValueObj = PresentValue(self._timeNow)
        
        # Tax Rate Calculator
        self._taxRateCalculator = TaxRateCalculator(self._financialData)
            
    def downloadCompanyData(self, ticker):
        try:
            self._companyData = yf.Ticker(ticker)
            self._successful = True
        except:
            self._successful = False
            return
        financialDataYF = self._companyData.financials
        # Yahoo Finance now provides data in correct order (newest to oldest)
        self._financialData = financialDataYF.copy()

        balancesheetDataYF = self._companyData.balancesheet
        self._balancesheetData = balancesheetDataYF.copy()

        cashFlowDataYF = self._companyData.cashflow
        self._cashFlowData = cashFlowDataYF.copy()
        
        # Debug: Print available cash flow rows to see what's available
        print(f"Available cash flow rows for {ticker}:")
        print(self._cashFlowData.index.tolist())
        print(f"Cash flow data shape: {self._cashFlowData.shape}")

        # analysis data
        self._analysis = self._companyData._analysis

        # company info
        self._companyInfo = self._companyData.info

        # Last known year (first column is now the most recent year) - convert to end of year
        current_date = self._financialData.columns[0]
        if hasattr(current_date, 'year'):
            self._timeNow = pd.Timestamp(f"{current_date.year}-12-31")
        else:
            try:
                parsed_date = pd.Timestamp(current_date)
                self._timeNow = pd.Timestamp(f"{parsed_date.year}-12-31")
            except:
                self._timeNow = current_date
        
                # Present Value Object
        self._presentValueObj = PresentValue(self._timeNow)
    
    def _getCurrentSharePrice(self):
        """Get the current share price from Yahoo Finance"""
        try:
            # Get current market data
            currentPrice = self._companyData.info.get('regularMarketPrice')
            if currentPrice is not None and currentPrice > 0:
                print(f"Current share price: ${currentPrice:.2f}")
                return currentPrice
            
            # Fallback to previous close if current price not available
            previousClose = self._companyData.info.get('previousClose')
            if previousClose is not None and previousClose > 0:
                print(f"Using previous close price: ${previousClose:.2f}")
                return previousClose
            
            # Final fallback to a reasonable default
            print("Warning: No share price data available. Using default price of $100.")
            return 100.0
            
        except Exception as e:
            print(f"Error getting share price: {e}. Using default price of $100.")
            return 100.0

    def getCurrentPrice(self):
        """Get the current share price (public method)"""
        return self._getCurrentSharePrice()
    
    def _calculateInvestedCapital(self):
        """Calculate invested capital using proper operating vs non-operating liability formula"""
        try:
            def _sum_rows(bs, row_names):
                """Helper function to sum multiple rows from balance sheet"""
                total = pd.Series([0] * len(bs.columns), index=bs.columns)
                for name in row_names:
                    if name in bs.index:
                        # Fill NaN values with 0 before adding
                        row_data = bs.loc[name].fillna(0)
                        total += row_data
                    else:
                        raise Exception(f"Row {name} not found in balance sheet")
                return total
            
            def _convert_to_end_of_year(values, dates):
                """Convert values to end-of-year (December 31st) by adjusting for time periods"""
                end_of_year_values = pd.Series(index=dates, dtype=float)
                
                for i, date in enumerate(dates):
                    # Convert date to December 31st of the same year
                    if hasattr(date, 'year'):
                        eoy_date = pd.Timestamp(f"{date.year}-12-31")
                    else:
                        try:
                            # Try to parse the date and extract year
                            parsed_date = pd.Timestamp(date)
                            eoy_date = pd.Timestamp(f"{parsed_date.year}-12-31")
                        except:
                            # Fallback to original date if parsing fails
                            eoy_date = date
                    
                    # Use the value as-is (balance sheet data is typically already end-of-year)
                    end_of_year_values[date] = values.iloc[i]
                
                return end_of_year_values
            
            # Get total assets
            total_assets = self._balancesheetData.loc['Total Assets'] if 'Total Assets' in self._balancesheetData.index else pd.Series([0] * len(self._balancesheetData.columns), index=self._balancesheetData.columns)
            total_assets = total_assets.fillna(0)
            
            # ----- Operating (non-interest-bearing) liabilities to subtract -----
            ap = _sum_rows(self._balancesheetData, ['Accounts Payable'])
            accruals = _sum_rows(self._balancesheetData, ['Payables And Accrued Expenses', 'Other Current Liabilities'])
            taxes_payable = _sum_rows(self._balancesheetData, ['Income Tax Payable', 'Total Tax Payable'])
            def_rev_curr = _sum_rows(self._balancesheetData, ['Current Deferred Revenue', 'Current Deferred Liabilities'])
            def_rev_nc = _sum_rows(self._balancesheetData, ['Non Current Deferred Assets', 'Non Current Deferred Taxes Assets'])
            
            # Remove interest-bearing items (do NOT subtract these here)
            # These are already excluded by not using a blanket "Total Current Liabilities"
            st_debt = _sum_rows(self._balancesheetData, ['Current Debt', 'Commercial Paper', 'Other Current Borrowings'])
            cpltd = _sum_rows(self._balancesheetData, ['Current Debt And Capital Lease Obligation', 'Current Capital Lease Obligation'])
            
            operating_liabilities = ap + accruals + taxes_payable + def_rev_curr + def_rev_nc
            
            # Invested Capital = Total Assets - Operating Liabilities
            invested_capital = total_assets - operating_liabilities
            
            # Convert to end-of-year values
            invested_capital_eoy = _convert_to_end_of_year(invested_capital, self._balancesheetData.columns)
            
            # Remove NaN values and ensure non-negative values
            invested_capital_eoy = invested_capital_eoy.fillna(0).clip(lower=0)
            
            return invested_capital_eoy
            
        except Exception as e:
            print(f"Error calculating invested capital: {e}")
            return pd.Series([0] * len(self._balancesheetData.columns), index=self._balancesheetData.columns)

    def _calculateDeltaNWC(self):
        """Calculate change in net working capital from balance sheet data"""
        deltaNWC = pd.DataFrame(index=['Delta NWC'], columns=self._balancesheetData.columns)
        
        # Calculate NWC for each year
        current_assets_rows = ['Total Current Assets', 'Current Assets']
        current_liabilities_rows = ['Total Current Liabilities', 'Current Liabilities']
        
        current_assets = None
        current_liabilities = None
        
        for row in current_assets_rows:
            if row in self._balancesheetData.index:
                current_assets = self._balancesheetData.loc[row]
                break
        
        for row in current_liabilities_rows:
            if row in self._balancesheetData.index:
                current_liabilities = self._balancesheetData.loc[row]
                break
        
        if current_assets is not None and current_liabilities is not None:
            # Calculate NWC for each year
            nwc = current_assets - current_liabilities
            
            # Calculate delta NWC (change from previous year)
            for i, col in enumerate(self._balancesheetData.columns):
                if i == 0:
                    # First year, no change
                    deltaNWC.loc['Delta NWC', col] = 0
                else:
                    # Change from previous year
                    prev_col = self._balancesheetData.columns[i-1]
                    deltaNWC.loc['Delta NWC', col] = nwc[col] - nwc[prev_col]
        
        return deltaNWC

    def _calculateNetBorrowings(self):
        """Calculate net borrowings from available cash flow data"""
        netBorrowings = pd.DataFrame(index=['Net Borrowings'], columns=self._cashFlowData.columns)
        
        # Common row names for debt-related cash flows in Yahoo Finance
        debt_related_rows = [
            'Long Term Debt Issuance',
            'Long Term Debt Paydown',
            'Short Term Debt Issuance',
            'Short Term Debt Paydown',
            'Debt Issuance',
            'Debt Repayment',
            'Proceeds From Borrowings',
            'Repayment Of Borrowings',
            'Net Issuance (Payments) of Debt Securities',
            'Net Issuance (Payments) of Debt'
        ]
        
        for col in self._cashFlowData.columns:
            net_borrowings_value = 0
            
            # Check for debt issuance (positive cash flow)
            for row in debt_related_rows:
                if row in self._cashFlowData.index:
                    value = self._cashFlowData.loc[row, col]
                    if pd.notna(value):
                        # Issuance is typically positive, repayment is negative
                        if 'issuance' in row.lower() or 'proceeds' in row.lower():
                            net_borrowings_value += value
                        elif 'paydown' in row.lower() or 'repayment' in row.lower() or 'payments' in row.lower():
                            net_borrowings_value -= abs(value)  # Make sure it's negative
                        else:
                            # For ambiguous names, assume positive is issuance
                            net_borrowings_value += value
            
            # If no specific debt rows found, try to calculate from financing activities
            if net_borrowings_value == 0:
                financing_rows = [
                    'Financing Cash Flow',
                    'Net Cash Flow From Financing Activities'
                ]
                for row in financing_rows:
                    if row in self._cashFlowData.index:
                        value = self._cashFlowData.loc[row, col]
                        if pd.notna(value):
                            # Financing cash flow includes debt, equity, dividends
                            # We'll use a portion as debt (this is an approximation)
                            net_borrowings_value = value * 0.3  # Assume 30% is debt-related
                            break
            
            netBorrowings.loc['Net Borrowings', col] = net_borrowings_value
        
        return netBorrowings


    def calculateFairValue(self, timeIntoTheFuture, parameter_weights=None, storeResults=False):
        """
        Calculate fair value with parameter adjustments.

        Args:
            timeIntoTheFuture: Number of years to project
            parameter_weights: Dictionary with parameter adjustment percentages
                Keys: 'discount_rate', 'perpetual_growth', 'prediction_window_growth', 'profitability', 'capex', 'nwc', 'net_borrowings'
                Values: Percentage change (e.g., 0.1 for 10% increase, -0.05 for 5% decrease)
            storeResults: If True, store results in instance variables
        """
        # Default parameter weights (no change)
        if parameter_weights is None:
            parameter_weights = {}

        timeUntil = np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe")
        
        # Filter out years with NaN data to create clean time series for all calculations
        validRevenueData = self._financialData.loc['Total Revenue'].dropna()
        validIncomeData = self._financialData.loc['Net Income From Continuing Operation Net Minority Interest'].dropna()
        
        # Use only years with valid data for discount rate calculation
        validYears = validRevenueData.index.intersection(validIncomeData.index)
        
        # Get growth estimates table
        timeUntil = np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe")
        tempTimeSeries = self.getTimeIndexes(validRevenueData.index, timeUntil)
        growthTable = self.getGrowthTable(tempTimeSeries)
        
        # Apply perpetual growth weights explicitly
        if 'perpetual_growth' in parameter_weights:
            # perpetual_growth_adjustment = 1 + parameter_weights['perpetual_growth']
            # Apply only to perpetual growth rate
            if 'perpetual' in growthTable.columns:
                growthTable.loc['Growth Rate', 'perpetual'] = growthTable.loc['Growth Rate', 'perpetual'] + parameter_weights['perpetual_growth']
        
        # Apply prediction window growth weights explicitly
        if 'prediction_window_growth' in parameter_weights:
            # prediction_growth_adjustment = 1 + parameter_weights['prediction_window_growth']
            # Apply to all non-perpetual growth rates (prediction window)
            for col in growthTable.columns:
                if col != 'perpetual':  # Apply to annual growth rates within prediction window
                    growthTable.loc['Growth Rate', col] = growthTable.loc['Growth Rate', col] + parameter_weights['prediction_window_growth']
        
        # Create discount table first to get the proper discount rates
        discountTable = self.getDiscountTable(tempTimeSeries)
        
        # Apply discount rate weights explicitly
        if 'discount_rate' in parameter_weights:
            # discount_adjustment = 1 + parameter_weights['discount_rate']
            # Apply to all discount rates in the table
            for col in discountTable.columns:
                discountTable.loc['Discount Rate', col] = discountTable.loc['Discount Rate', col] + parameter_weights['discount_rate']
        
        # Create revenue table using the calculated discount rate
        perpetualDiscountRate = discountTable.loc['Discount Rate', 'perpetual']
        revenueTable = self.predictRevenue(timeIntoTheFuture, perpetualDiscountRate, validRevenueData, growthTable)
        profitabilityTable = self.predictProfitability(revenueTable, validIncomeData)
        
        # Apply profitability weights explicitly
        if 'profitability' in parameter_weights:
            # profit_adjustment = 1 + parameter_weights['profitability']
            # Apply to all profitability values in the table
            for col in profitabilityTable.columns:
                profitabilityTable.loc['Profitability', col] = profitabilityTable.loc['Profitability', col] + parameter_weights['profitability']
        
        incomeTable = self.predictIncome(revenueTable, profitabilityTable)
        
        # Create EBIT prediction table
        if self._ebit_row is not None:
            ebitProfitabilityTable = self.predictEBITProfitability(revenueTable, self._financialData.loc[self._ebit_row])
            ebitTable = self.predictEBIT(revenueTable, ebitProfitabilityTable)
        else:
            ebitProfitabilityTable = self.predictEBITProfitability(revenueTable, self._dummy_ebit)
            ebitTable = self.predictEBIT(revenueTable, ebitProfitabilityTable)
        
        # Create prediction tables for additional metrics
        if self._dandA_row is not None:
            dandATable = self.predictDandA(revenueTable, self._cashFlowData.loc[self._dandA_row])
        else:
            dandATable = self.predictDandA(revenueTable, self._dummy_da)
            
        if self._capex_row is not None:
            capExTable = self.predictCapEx(revenueTable, self._cashFlowData.loc[self._capex_row])
        else:
            capExTable = self.predictCapEx(revenueTable, self._dummy_capex)
        
        # Apply CapEx weights explicitly
        if 'capex' in parameter_weights:
            capex_adjustment = 1 + parameter_weights['capex']
            # Apply to all CapEx values in the table
            for col in capExTable.columns:
                capExTable.loc['CapEx', col] = capExTable.loc['CapEx', col] * capex_adjustment
            
        deltaNWCTable = self.predictDeltaNWC(revenueTable, self._calculateDeltaNWC().iloc[0])
        
        # Apply NWC weights explicitly
        if 'nwc' in parameter_weights:
            nwc_adjustment = 1 + parameter_weights['nwc']
            # Apply to all NWC values in the table
            for col in deltaNWCTable.columns:
                deltaNWCTable.loc['Delta NWC', col] = deltaNWCTable.loc['Delta NWC', col] * nwc_adjustment
        
        netBorrowingsTable = self.predictNetBorrowings(revenueTable, self._calculateNetBorrowings().iloc[0])
        
        # Apply Net Borrowings weights explicitly
        if 'net_borrowings' in parameter_weights:
            borrowings_adjustment = 1 + parameter_weights['net_borrowings']
            # Apply to all Net Borrowings values in the table
            for col in netBorrowingsTable.columns:
                netBorrowingsTable.loc['Net Borrowings', col] = netBorrowingsTable.loc['Net Borrowings', col] * borrowings_adjustment

        # Get tax rate table from TaxRateCalculator
        taxRateTable = self._taxRateCalculator.getTaxRateTable(revenueTable.columns)

        # Calculates FCFF using the already calculated tables
        # Create a comprehensive cash flow table with all the components
        comprehensiveCashFlowData = pd.DataFrame(index=['EBIT', 'D&A', 'CapEx', 'Delta NWC', 'Net Borrowings', 'Tax Rate', 'Invested Capital'], columns=revenueTable.columns)
        
        # Fill in the data from our calculated tables
        comprehensiveCashFlowData.loc['EBIT'] = ebitTable.loc['EBIT']
        comprehensiveCashFlowData.loc['D&A'] = dandATable.loc['D&A']
        comprehensiveCashFlowData.loc['CapEx'] = capExTable.loc['CapEx']
        comprehensiveCashFlowData.loc['Delta NWC'] = deltaNWCTable.loc['Delta NWC']
        comprehensiveCashFlowData.loc['Net Borrowings'] = netBorrowingsTable.loc['Net Borrowings']
        comprehensiveCashFlowData.loc['Tax Rate'] = taxRateTable.loc['Tax Rate']
        
        # Add invested capital data
        investedCapitalData = self._calculateInvestedCapital()
        comprehensiveCashFlowData.loc['Invested Capital'] = investedCapitalData
        # Tax rate will be calculated by the FCFF method
        
        fcffTable = self._fcfObj.estimateFCFF(ebitTable, comprehensiveCashFlowData, self._taxRateCalculator)

        # Gets shares outstanding from company info
        if 'sharesOutstanding' in self._companyInfo:
            sharesOutstanding = self._companyInfo['sharesOutstanding']
        else:
            sharesOutstanding = 1

        presentValueTable = self.getPresentValueTable(fcffTable, discountTable)
        pricePerShare = self._presentValueObj.getPresentValue(fcffTable, discountTable, "FCFF") / sharesOutstanding
    
        
        # Create summary table for this scenario
        summaryTable = self._createSummaryTable(
            growthTable, discountTable, revenueTable, profitabilityTable, 
            incomeTable, ebitProfitabilityTable, ebitTable, dandATable, 
            capExTable, deltaNWCTable, netBorrowingsTable, fcffTable, 
            taxRateTable, presentValueTable, pricePerShare
        )
        
        # Store results in instance variables only if requested (typically for realistic scenario)
        if storeResults:
            self._growthTable = growthTable
            self._discountTable = discountTable
            self._revenueTable = revenueTable
            self._profitabilityTable = profitabilityTable
            self._incomeTable = incomeTable
            self._ebitProfitabilityTable = ebitProfitabilityTable
            self._ebitTable = ebitTable
            self._dandATable = dandATable
            self._capExTable = capExTable
            self._deltaNWCTable = deltaNWCTable
            self._netBorrowingsTable = netBorrowingsTable
            self._fcffTable = fcffTable
            self._taxRateTable = taxRateTable
            self._presentValueTable = presentValueTable
            self._sharesOutstanding = sharesOutstanding
            self._pricePerShare = pricePerShare
            self._taxRateTable = taxRateTable
            
            # Print individual fair value estimate
            self._printIndividualFairValue("custom", pricePerShare)
        
        return pricePerShare, summaryTable
    
    def _createSummaryTable(self, growthTable, discountTable, revenueTable, profitabilityTable, 
                           incomeTable, ebitProfitabilityTable, ebitTable, dandATable, 
                           capExTable, deltaNWCTable, netBorrowingsTable, fcffTable, 
                           taxRateTable, presentValueTable, pricePerShare):
        """Create comprehensive valuation summary table with all financial metrics"""
        # Get the years from revenue table (includes both historical and projected)
        years = revenueTable.columns
        
        # Initialize the comprehensive metrics table
        metrics_data = {}
        
        # 1. Revenue (already in revenueTable)
        # 2. Revenue growth rate (from growth estimates object, includes perpetual growth rate)
        if growthTable is not None and not growthTable.empty:
            growthRatesTable = growthTable
        else:
            # Fallback to revenue object method if growth table not available
            growthRatesTable = self._revenueObj.getGrowthRates(revenueTable.columns)
        
        # 3. Profitability (use provided profitability table)
        profitabilityTable = profitabilityTable
        
        # 4. Income (already in incomeTable)
        
        # 5. EBIT/Revenue rate (use provided EBIT profitability table)
        if ebitProfitabilityTable is not None and not ebitProfitabilityTable.empty:
            ebitRatioTable = ebitProfitabilityTable
        else:
            ebitRatioTable = pd.DataFrame(index=['EBIT/Revenue Rate'], columns=years)
        
        # 6. EBIT (use raw numeric data for concatenation)
        # 7. D&A (use raw numeric data for concatenation)
        # 8. CapEx (use raw numeric data for concatenation)
        # 9. Delta NWC (use raw numeric data for concatenation)
        
        # 10. Net Borrowings (already in netBorrowingsTable)
        
        # 11. FCFF (already in fcffTable)
        
        # 12. Cash flow to net income (from FCF object)
        cashFlowToNetIncomeTable = self._fcfObj.getCashFlowToNetIncomeRatio(fcffTable, incomeTable)
        
        # 13. Tax rate (from TaxRateCalculator)
        taxRateTable = self._taxRateCalculator.getTaxRateTable(revenueTable.columns)
        
        # 14. Discount rate (already in discountTable)
        
        # 15. Present value (already in presentValueTable)
        
        # Filter out empty DataFrames before concatenation to avoid deprecation warnings
        # Reorder tables to start with: Growth estimates, Discount rate, Revenue
        tables_to_concat = []
        for table in [growthRatesTable, discountTable, revenueTable, profitabilityTable, incomeTable, ebitRatioTable, ebitTable, dandATable, capExTable, deltaNWCTable, netBorrowingsTable, fcffTable, cashFlowToNetIncomeTable, taxRateTable, presentValueTable]:
            if table is not None and not table.empty and table.shape[1] > 0:
                # Ensure all tables have the same column structure
                if not table.empty and hasattr(table, 'columns'):
                    # Reindex to match the revenue table columns (which should be the master time series)
                    table = table.reindex(columns=revenueTable.columns)
                tables_to_concat.append(table)
        
        if tables_to_concat:
            resultTable = pd.concat(tables_to_concat, axis=0)
        else:
            # Create an empty DataFrame if no valid tables
            resultTable = pd.DataFrame()
        
        # Add fair value row at the end
        if pricePerShare is not None:
            # Create fair value row - show the fair value only in the current year (last column)
            fairValueRow = pd.DataFrame(index=['Fair Value (per share)'], columns=revenueTable.columns)
            # Set all values to empty except the last column (current year)
            
            fairValueRow.loc['Fair Value (per share)', self._timeNow] = pricePerShare
            
            # Add the fair value row to the result table
            if not resultTable.empty:
                resultTable = pd.concat([resultTable, fairValueRow], axis=0)
        else:
                resultTable = fairValueRow
        
        # Format specific rows to show values in millions with 'M' suffix
        # Convert to object dtype to allow mixed data types
        resultTable = resultTable.astype(object)
        
        return resultTable
    
    def calculateAllScenarios(self, timeIntoTheFuture):
        """Calculate fair value for all three scenarios: pessimistic, realistic, and optimistic"""
        
        # Define parameter weights for different scenarios
        pessimistic_weights = {
            'discount_rate': 0,              # 15% increase in discount rate
            'perpetual_growth': 0,           # 20% decrease in perpetual growth rate
            'prediction_window_growth': -0.03,   # 20% decrease in prediction window growth
            'profitability': -0.01,              # 10% decrease in profitability
            'capex': 0,                       # 10% increase in CapEx
            'nwc': 0,                         # 10% increase in NWC
            'net_borrowings': 0              # 10% decrease in net borrowings
        }
        
        realistic_weights = {}  # No adjustments for realistic scenario
        
        optimistic_weights = {
            'discount_rate': 0,              # 10% decrease in discount rate
            'perpetual_growth': 0,            # 20% increase in perpetual growth rate
            'prediction_window_growth': 0.03,    # 20% increase in prediction window growth
            'profitability': 0.01,               # 10% increase in profitability
            'capex': 0,                      # 10% decrease in CapEx
            'nwc': 0,                        # 10% decrease in NWC
            'net_borrowings': 0               # 10% increase in net borrowings
        }
        
        # Calculate all scenarios independently - only store results for realistic scenario
        pessimisticValue, pessimisticSummary = self.calculateFairValue(timeIntoTheFuture, pessimistic_weights, storeResults=False)
        realisticValue, realisticSummary = self.calculateFairValue(timeIntoTheFuture, realistic_weights, storeResults=True)
        optimisticValue, optimisticSummary = self.calculateFairValue(timeIntoTheFuture, optimistic_weights, storeResults=False)
        
        # Store scenario values for later access
        self._scenarioValues = {
            'pessimistic': {'value': pessimisticValue, 'summary': pessimisticSummary},
            'realistic': {'value': realisticValue, 'summary': realisticSummary},
            'optimistic': {'value': optimisticValue, 'summary': optimisticSummary}
        }
        
        # Print fair value estimates
        self._printFairValueEstimates(pessimisticValue, realisticValue, optimisticValue)
        
        # Print summary table as text
        self.printSummaryTableAsText()
        
        return self._scenarioValues
    
    def _printFairValueEstimates(self, pessimisticValue, realisticValue, optimisticValue):
        """Print fair value estimates for all scenarios"""
        # Ensure values are numeric
        try:
            pessimisticValue = float(pessimisticValue) if pessimisticValue is not None else 0.0
            realisticValue = float(realisticValue) if realisticValue is not None else 0.0
            optimisticValue = float(optimisticValue) if optimisticValue is not None else 0.0
        except (ValueError, TypeError) as e:
            print(f"Error converting values to float: {e}")
            print(f"Pessimistic: {pessimisticValue}, Realistic: {realisticValue}, Optimistic: {optimisticValue}")
            return
        
        print("\n" + "="*60)
        print("FAIR VALUE ESTIMATES")
        print("="*60)
        print(f"Pessimistic Scenario: ${pessimisticValue:.2f}")
        print(f"Realistic Scenario:  ${realisticValue:.2f}")
        print(f"Optimistic Scenario: ${optimisticValue:.2f}")
        print("="*60)
        
        # Calculate the range
        min_value = min(pessimisticValue, realisticValue, optimisticValue)
        max_value = max(pessimisticValue, realisticValue, optimisticValue)
        range_value = max_value - min_value
        
        print(f"Value Range: ${min_value:.2f} - ${max_value:.2f} (Range: ${range_value:.2f})")
        print("="*60 + "\n")
    
    def _printIndividualFairValue(self, scenario, pricePerShare):
        """Print individual fair value estimate for a single scenario"""
        try:
            pricePerShare = float(pricePerShare) if pricePerShare is not None else 0.0
            print(f"\n{scenario.capitalize()} Scenario Fair Value: ${pricePerShare:.2f}")
        except (ValueError, TypeError) as e:
            print(f"Error converting price to float: {e}")
            print(f"Price value: {pricePerShare}")
    
    def getFairValueEstimatesString(self, pessimisticValue, realisticValue, optimisticValue):
        """Get formatted string of fair value estimates for all scenarios"""
        try:
            # Ensure values are numeric
            pessimisticValue = float(pessimisticValue) if pessimisticValue is not None else 0.0
            realisticValue = float(realisticValue) if realisticValue is not None else 0.0
            optimisticValue = float(optimisticValue) if optimisticValue is not None else 0.0
            
            min_value = min(pessimisticValue, realisticValue, optimisticValue)
            max_value = max(pessimisticValue, realisticValue, optimisticValue)
            range_value = max_value - min_value
            
            estimates_text = f"""
                FAIR VALUE ESTIMATES
                ==================
                Pessimistic Scenario: ${pessimisticValue:.2f}
                Realistic Scenario:  ${realisticValue:.2f}
                Optimistic Scenario: ${optimisticValue:.2f}
                ==================
                Value Range: ${min_value:.2f} - ${max_value:.2f} (Range: ${range_value:.2f})
                ==================
                """
            return estimates_text
        except (ValueError, TypeError) as e:
            return f"Error formatting estimates: {e}\nValues: Pessimistic={pessimisticValue}, Realistic={realisticValue}, Optimistic={optimisticValue}"
    
    def printSummaryTableAsText(self, summaryTable=None):
        """Print the summary table as comma-separated text that can be easily converted to pandas DataFrame"""
        if summaryTable is None:
            # Use the stored summary table from realistic scenario
            if hasattr(self, '_growthTable') and hasattr(self, '_discountTable') and hasattr(self, '_revenueTable'):
                summaryTable = self._createSummaryTable(
                    self._growthTable, self._discountTable, self._revenueTable, self._profitabilityTable,
                    self._incomeTable, self._ebitProfitabilityTable, self._ebitTable, self._dandATable,
                    self._capExTable, self._deltaNWCTable, self._netBorrowingsTable, self._fcffTable,
                    self._taxRateTable, self._presentValueTable, self._pricePerShare
                )
            else:
                print("No summary table available. Please run a valuation calculation first.")
                return
        
        if summaryTable is None or summaryTable.empty:
            print("Summary table is empty.")
            return
        
        print("\n" + "="*80)
        print("SUMMARY TABLE (CSV FORMAT)")
        print("="*80)
        
        # Print header row (column names)
        columns = summaryTable.columns.tolist()
        header = "Metric," + ",".join([str(col) for col in columns])
        print(header)
        
        # Print data rows
        for index, row in summaryTable.iterrows():
            # Create row data with metric name and values
            row_data = [str(index)]
            for col in columns:
                value = row[col]
                if pd.isna(value):
                    row_data.append("")
                else:
                    # Convert to string and handle different data types
                    if isinstance(value, (int, float)):
                        row_data.append(str(value))
                    else:
                        row_data.append(str(value))
            
            print(",".join(row_data))
        
        print("="*80)
        print("END OF SUMMARY TABLE")
        print("="*80 + "\n")
    
    def getSummaryTableAsCSV(self, summaryTable=None):
        """Get the summary table as CSV string that can be easily converted to pandas DataFrame"""
        if summaryTable is None:
            # Use the stored summary table from realistic scenario
            if hasattr(self, '_growthTable') and hasattr(self, '_discountTable') and hasattr(self, '_revenueTable'):
                summaryTable = self._createSummaryTable(
                    self._growthTable, self._discountTable, self._revenueTable, self._profitabilityTable,
                    self._incomeTable, self._ebitProfitabilityTable, self._ebitTable, self._dandATable,
                    self._capExTable, self._deltaNWCTable, self._netBorrowingsTable, self._fcffTable,
                    self._taxRateTable, self._presentValueTable, self._pricePerShare
                )
            else:
                return "No summary table available. Please run a valuation calculation first."
        
        if summaryTable is None or summaryTable.empty:
            return "Summary table is empty."
        
        # Create CSV content
        csv_lines = []
        
        # Add header row
        columns = summaryTable.columns.tolist()
        header = "Metric," + ",".join([str(col) for col in columns])
        csv_lines.append(header)
        
        # Add data rows
        for index, row in summaryTable.iterrows():
            row_data = [str(index)]
            for col in columns:
                value = row[col]
                if pd.isna(value):
                    row_data.append("")
                else:
                    if isinstance(value, (int, float)):
                        row_data.append(str(value))
                    else:
                        row_data.append(str(value))
            
            csv_lines.append(",".join(row_data))
        
        return "\n".join(csv_lines)
    
    def getSummaryTableAsDataFrame(self, summaryTable=None):
        """Get the summary table as a pandas DataFrame"""
        if summaryTable is None:
            # Use the stored summary table from realistic scenario
            if hasattr(self, '_growthTable') and hasattr(self, '_discountTable') and hasattr(self, '_revenueTable'):
                summaryTable = self._createSummaryTable(
                    self._growthTable, self._discountTable, self._revenueTable, self._profitabilityTable,
                    self._incomeTable, self._ebitProfitabilityTable, self._ebitTable, self._dandATable,
                    self._capExTable, self._deltaNWCTable, self._netBorrowingsTable, self._fcffTable,
                    self._taxRateTable, self._presentValueTable, self._pricePerShare
                )
            else:
                return None
        
        return summaryTable
    
    def getCurrentFairValueEstimates(self):
        """Get current fair value estimates if they have been calculated"""
        if hasattr(self, '_scenarioValues') and self._scenarioValues:
            return {
                'pessimistic': self._scenarioValues['pessimistic']['value'],
                'realistic': self._scenarioValues['realistic']['value'],
                'optimistic': self._scenarioValues['optimistic']['value']
            }
        else:
            return None

    def getGrowthTable(self, timeSeries):
        """Get growth rates table for the specified time series"""
        return self._growthEstimatesObj.getGrowthTable(timeSeries)
    
    def getPessimisticGrowthTable(self, timeSeries):
        """Get pessimistic growth rates table for the specified time series"""
        return self._growthEstimatesObj.getPessimisticGrowthTable(timeSeries)
    
    def getOptimisticGrowthTable(self, timeSeries):
        """Get optimistic growth rates table for the specified time series"""
        return self._growthEstimatesObj.getOptimisticGrowthTable(timeSeries)

    def predictRevenue(self, timeIntoTheFuture, perpetualDiscount, pastRevenueStreams, growthTable):
        """
        Predict revenue streams with explicit parameters.
        
        Args:
            timeIntoTheFuture: Number of years to project into the future
            perpetualDiscount: Discount rate for perpetual value calculation
            pastRevenueStreams: Historical revenue data
            growthTable: Growth estimates table for each time period
        """
        finalPredictionDate = np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe")
        return self._revenueObj.getRevenueStreams(pastRevenueStreams, finalPredictionDate, perpetualDiscount, growthTable)       

    def predictProfitability(self, predictedRevenueStreams, knownIncomeStreams):
        """Calculate profitability table with actual past values and projected future values"""
        return self._incomeObj.calculateProfitabilityTable(predictedRevenueStreams, knownIncomeStreams)
    
    def predictIncome(self, predictedRevenueStreams, profitabilityTable):
        """Calculate income using profitability table and revenue streams"""
        return self._incomeObj.calculateIncomeFromProfitability(predictedRevenueStreams, profitabilityTable, self._financialData.loc['Net Income From Continuing Operation Net Minority Interest'])
    
    def predictEBITProfitability(self, predictedRevenueStreams, knownEBITStreams):
        """Calculate EBIT profitability table with actual past values and projected future values"""
        return self._ebitObj.calculateProfitabilityTable(predictedRevenueStreams, knownEBITStreams)
    
    def predictEBIT(self, predictedRevenueStreams, ebitProfitabilityTable):
        """Calculate EBIT using profitability table and revenue streams"""
        return self._ebitObj.calculateEBITFromProfitability(predictedRevenueStreams, ebitProfitabilityTable, self._financialData.loc[self._ebit_row] if self._ebit_row is not None else self._dummy_ebit)
    
    def predictDandA(self, predictedRevenueStreams, knownDandAStreams):
        return self._dandAObj.getDandAStreams(predictedRevenueStreams, knownDandAStreams)
    
    def predictCapEx(self, predictedRevenueStreams, knownCapExStreams):
        return self._capExObj.getCapExStreams(predictedRevenueStreams, knownCapExStreams)
    
    def predictDeltaNWC(self, predictedRevenueStreams, knownDeltaNWCStreams):
        return self._deltaNWCObj.getDeltaNWCStreams(predictedRevenueStreams, knownDeltaNWCStreams)
    
    def predictNetBorrowings(self, predictedRevenueStreams, knownNetBorrowingsStreams):
        return self._netBorrowingsObj.getNetBorrowingsStreams(predictedRevenueStreams, knownNetBorrowingsStreams)

    
    def getDiscountTable(self, timeSeries):
        return self._discountRateObj.getDiscountRates(timeSeries)

    def getPresentValueTable(self, incomeTable, discountRateTable):
        return self._presentValueObj.getPresentValues(incomeTable, discountRateTable, "FCFF")

    def getTimeIndexes(self, currentTimeIndexes, untilTime):
        """Create a clean time series with one entry per year in chronological order"""
        # Get all unique years from historical data
        historicalYears = set()
        for time in currentTimeIndexes:
            year = pd.Timestamp(time).year
            historicalYears.add(year)
        
        # Get the range of years we need
        minYear = min(historicalYears)
        untilYear = pd.Timestamp(untilTime).year
        
        # Create sequential years from earliest historical to target year
        allYears = []
        for year in range(minYear, untilYear + 1):
            allYears.append(pd.Timestamp(f"{year}-12-31"))
        
        # Create clean DatetimeIndex and sort to ensure chronological order
        timeIndex = pd.DatetimeIndex(allYears)
        return timeIndex.sort_values()

    def _formatMillions(self, table, row_name):
        """Format a specific row in a table to show values in millions with 'M' suffix"""
        if table is not None and not table.empty and row_name in table.index:
            formatted_table = table.copy()
            # Convert to object dtype to allow string values
            formatted_table = formatted_table.astype(object)
            for col in formatted_table.columns:
                value = formatted_table.loc[row_name, col]
                if pd.notna(value) and value != 0:
                    formatted_table.loc[row_name, col] = f"{value / 1000000:.2f}M"
                elif pd.notna(value):
                    formatted_table.loc[row_name, col] = "0.00M"
                else:
                    formatted_table.loc[row_name, col] = "N/A"
            return formatted_table
        return table

    def getValuationSummaryTable(self):
        """Get the stored valuation summary table from the realistic scenario"""
        # Use the stored results from the realistic scenario
        if hasattr(self, '_growthTable') and hasattr(self, '_discountTable') and hasattr(self, '_revenueTable'):
            return self._createSummaryTable(
                self._growthTable, self._discountTable, self._revenueTable, self._profitabilityTable,
                self._incomeTable, self._ebitProfitabilityTable, self._ebitTable, self._dandATable,
                self._capExTable, self._deltaNWCTable, self._netBorrowingsTable, self._fcffTable,
                self._taxRateTable, self._presentValueTable, self._pricePerShare
            )
        else:
            # Fallback: return empty DataFrame if no stored results
            return pd.DataFrame()



    def getFairValue(self):
        return self._pricePerShare

    def setDiscountWACC(self):
        # Get current share price and shares outstanding for equity calculation
        currentSharePrice = self._getCurrentSharePrice()
        sharesOutstanding = self._companyInfo.get('sharesOutstanding', 1)
        
        self._discountRateObj = WACCDiscountRate(
            self._financialData, 
            self._balancesheetData, 
            getGlobal('RiskFreeInterestRate'), 
            getGlobal('marketReturn'), 
            self._companyInfo['beta'],
            sharesOutstanding,
            currentSharePrice
        )

    def setDiscountConstant(self, value):
        self._discountRateObj = ConstantDiscountRate(value)
    
    def setDiscountCostOfEquity(self):
        """Set discount rate to cost of equity using CAPM"""
        self._discountRateObj = CostOfEquityDiscountRate(
            getGlobal('RiskFreeInterestRate'), 
            getGlobal('marketReturn'), 
            self._companyInfo['beta']
        )

    def setProfitabilityConstant(self, value):
        self._incomeObj.setProfitability(value)

    def setProfitabilityLastYearsAverage(self):
        self._incomeObj = ConstantMarginIncome(self._financialData.loc['Total Revenue'], self._financialData.loc['Net Income From Continuing Operation Net Minority Interest'])

    def setSharesOutstanding(self, number):
        self._sharesOutstanding = number

    def getSharesOutstanding(self):
        return self._sharesOutstanding

    def setFCFConstant(self, value):
        self._fcfObj.setCashFlowToNetIncomeRatio(value)

    def setFCFLastYearsAverage(self):
        self._fcfObj = ConstantIncomeToFCF(self._financialData, self._cashFlowData)

    def setGrowthEstimates(self):
        """Initialize growth estimates object with analyst data"""
        # Extract growth estimates from the new yfinance API structure
        growth_estimates = self._analysis.growth_estimates
        if growth_estimates is not None and not growth_estimates.empty:
            # Create a Series with the expected index format
            growth_data = {}
            if '0y' in growth_estimates.index:
                growth_data['0Y'] = growth_estimates.loc['0y', 'stockTrend']
            if '+1y' in growth_estimates.index:
                growth_data['+1Y'] = growth_estimates.loc['+1y', 'stockTrend']
            if 'LTG' in growth_estimates.index and pd.notna(growth_estimates.loc['LTG', 'stockTrend']):
                growth_data['+5Y'] = growth_estimates.loc['LTG', 'stockTrend']
            else:
                # Fallback to a reasonable estimate if LTG is not available
                growth_data['+5Y'] = getGlobal('economyGrowth')
            
            growth_series = pd.Series(growth_data)
            self._growthEstimatesObj = AnalystGrowthEstimates(growth_series, getGlobal('economyGrowth'), self._timeNow)
        else:
            # Fallback to constant growth if no analyst estimates available
            growth_series = pd.Series({
                '0Y': getGlobal('economyGrowth'),
                '+1Y': getGlobal('economyGrowth'),
                '+5Y': getGlobal('economyGrowth')
            })
            self._growthEstimatesObj = AnalystGrowthEstimates(growth_series, getGlobal('economyGrowth'), self._timeNow)

    def setRevenueSpecialistEstimates(self):
        """Initialize revenue object using growth estimates"""
        # Use the growth estimates object to create revenue predictions
        self._revenueObj = RevenueForecast()

    def setRevenueConstant(self, value):
        self._revenueObj = ConstantGrowthRevenue(value, getGlobal('economyGrowth'))
    
    def setGrowthEstimatesConstant(self, value):
        """Set growth estimates to constant value"""
        self._growthEstimatesObj = ConstantGrowthEstimates(value, getGlobal('economyGrowth'), self._timeNow)
        # Update revenue object to use new growth estimates
        self.setRevenueSpecialistEstimates()
    
    def setGrowthEstimatesAnalyst(self):
        """Set growth estimates to analyst estimates"""
        self.setGrowthEstimates()
        # Update revenue object to use new growth estimates
        self.setRevenueSpecialistEstimates()
