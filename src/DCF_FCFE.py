import numpy as np
import yfinance as yf
import pandas as pd
import copy 

from .globals import getGlobal

from .revenue.ConstantGrowthRevenue import ConstantGrowthRevenue
from .revenue.AnalystRevenueGrowth import AnalystRevenueGrowth

from .income.ConstantMarginIncome import ConstantMarginIncome

from .fcf.ConstantIncomeToFCF import ConstantIncomeToFCF

from .discoundRate.ConstantDiscountRate import ConstantDiscountRate
from .discoundRate.WACCDiscountRate import WACCDiscountRate

from .PresentValue import PresentValue

# Calculates fair value based on free cash flow to equity
class DCF_FCFE:
    def __init__(self, companyTicker):
        self._successful = False
        self.downloadCompanyData(companyTicker)
        if(not self._successful):
            return

        # Revenue Projection Object
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
        else:
            # Fallback to constant growth if no analyst estimates available
            growth_series = pd.Series({
                '0Y': getGlobal('economyGrowth'),
                '+1Y': getGlobal('economyGrowth'),
                '+5Y': getGlobal('economyGrowth')
            })
        
        self._revenueObj = AnalystRevenueGrowth(growth_series, getGlobal('economyGrowth'), self._timeNow)
        # self._revenueObj = ConstantGrowthRevenue(0.07, 0.025, 0.12)

        # Income Projection Object
        # Use the new yfinance API row names
        revenue_row = 'Total Revenue'  # This still exists
        net_income_row = 'Net Income From Continuing Operation Net Minority Interest'  # Updated row name
        
        self._incomeObj = ConstantMarginIncome(self._financialData.loc[revenue_row], self._financialData.loc[net_income_row])
        
        # Free cash flow object
        self._fcfObj = ConstantIncomeToFCF(self._financialData, self._cashFlowData)

        # Discount Rate Object
        costOfEquity = getGlobal('RiskFreeInterestRate') + self._companyInfo['beta'] * (getGlobal('marketReturn') - getGlobal('RiskFreeInterestRate'))
        
        # Get current share price for equity calculation
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
        # self._discountRateObj = ConstantDiscountRate(costOfEquity)

        # Present Value Object
        self._presentValueObj = PresentValue(self._timeNow)
            
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

        # Last known year (first column is now the most recent year)
        self._timeNow = self._financialData.columns[0]
    
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

    def calculateFairValue(self, timeIntoTheFuture):

        timeUntil = np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe")
        
        # Filter out years with NaN data to create clean time series for all calculations
        validRevenueData = self._financialData.loc['Total Revenue'].dropna()
        validIncomeData = self._financialData.loc['Net Income From Continuing Operation Net Minority Interest'].dropna()
        
        # Use only years with valid data for discount rate calculation
        validYears = validRevenueData.index.intersection(validIncomeData.index)
        
        # Create revenue table first to get the complete time series (historical + future)
        self._revenueTable = self.predictRevenue(timeIntoTheFuture, 0.10)  # Use temporary discount rate
        
        # Now create discount table for ALL years in the revenue table
        allYears = self._revenueTable.columns
        self._discountTable = self.getDiscountTable(allYears)
        
        # Update revenue table with the correct perpetual discount rate
        self._revenueTable = self.predictRevenue(timeIntoTheFuture, self._discountTable.loc['Discount Rate', 'perpetual'])
        self._incomeTable = self.predictIncome(self._revenueTable, validIncomeData)

        # Calculates FCFE
        # Filter cash flow data to only include years with valid data
        validCashFlowData = self._cashFlowData.loc[['Operating Cash Flow', 'Capital Expenditure']].dropna(axis=1)
        # Add calculated net borrowings
        netBorrowingsData = self._calculateNetBorrowings()
        validCashFlowData = pd.concat([validCashFlowData, netBorrowingsData], axis=0)
        self._fcfeTable = self._fcfObj.estimateFCFE(self._incomeTable, validCashFlowData)

        # Gets shares outstanding from company info
        if 'sharesOutstanding' in self._companyInfo:
            self._sharesOutstanding = self._companyInfo['sharesOutstanding']
        else:
            self._sharesOutstanding = 1
        # self._sharesOutstanding = self._balancesheetData.loc['Common Stock'][-1]

        self._presentValueTable = self.getPresentValueTable(self._fcfeTable, self._discountTable)
        self._pricePerShare = self._presentValueObj.getPresentValue(self._fcfeTable, self._discountTable) / self._sharesOutstanding
        return self._pricePerShare
    
    def calculateAllScenarios(self, timeIntoTheFuture):
        """Calculate fair value for all three scenarios: pessimistic, realistic, and optimistic"""
        
        # Calculate realistic scenario (current implementation)
        realisticValue = self.calculateFairValue(timeIntoTheFuture)
        
        # Calculate pessimistic scenario
        pessimisticValue = self._calculateScenarioValue(timeIntoTheFuture, 'pessimistic')
        
        # Calculate optimistic scenario
        optimisticValue = self._calculateScenarioValue(timeIntoTheFuture, 'optimistic')
        
        return {
            'pessimistic': pessimisticValue,
            'realistic': realisticValue,
            'optimistic': optimisticValue
        }
    
    def _calculateScenarioValue(self, timeIntoTheFuture, scenario):
        """Calculate fair value for a specific scenario"""
        
        # Filter out years with NaN data to create clean time series for all calculations
        validRevenueData = self._financialData.loc['Total Revenue'].dropna()
        validIncomeData = self._financialData.loc['Net Income From Continuing Operation Net Minority Interest'].dropna()
        
        # Use only years with valid data for discount rate calculation
        validYears = validRevenueData.index.intersection(validIncomeData.index)
        
        # Create revenue table first to get the complete time series (historical + future)
        if scenario == 'pessimistic':
            revenueTable = self._revenueObj.getPessimisticRevenueStreams(
                self._financialData.loc['Total Revenue'], 
                np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe"),
                0.10  # Use temporary discount rate
            )
        elif scenario == 'optimistic':
            revenueTable = self._revenueObj.getOptimisticRevenueStreams(
                self._financialData.loc['Total Revenue'], 
                np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe"),
                0.10  # Use temporary discount rate
            )
        else:
            revenueTable = self.predictRevenue(timeIntoTheFuture, 0.10)
        
        # Now create discount table for ALL years in the revenue table
        allYears = revenueTable.columns
        discountTable = self.getDiscountTable(allYears)
        
        # Update revenue table with the correct perpetual discount rate
        if scenario == 'pessimistic':
            revenueTable = self._revenueObj.getPessimisticRevenueStreams(
                self._financialData.loc['Total Revenue'], 
                np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe"),
                discountTable.loc['Discount Rate', 'perpetual']
            )
        elif scenario == 'optimistic':
            revenueTable = self._revenueObj.getOptimisticRevenueStreams(
                self._financialData.loc['Total Revenue'], 
                np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe"),
                discountTable.loc['Discount Rate', 'perpetual']
            )
        else:
            revenueTable = self.predictRevenue(timeIntoTheFuture, discountTable.loc['Discount Rate', 'perpetual'])
        
        incomeTable = self.predictIncome(revenueTable, validIncomeData)

        # Calculates FCFE
        validCashFlowData = self._cashFlowData.loc[['Operating Cash Flow', 'Capital Expenditure']].dropna(axis=1)
        # Add calculated net borrowings
        netBorrowingsData = self._calculateNetBorrowings()
        validCashFlowData = pd.concat([validCashFlowData, netBorrowingsData], axis=0)
        fcfeTable = self._fcfObj.estimateFCFE(incomeTable, validCashFlowData)

        # Gets shares outstanding from company info
        if 'sharesOutstanding' in self._companyInfo:
            sharesOutstanding = self._companyInfo['sharesOutstanding']
        else:
            sharesOutstanding = 1

        presentValueTable = self.getPresentValueTable(fcfeTable, discountTable)
        pricePerShare = self._presentValueObj.getPresentValue(fcfeTable, discountTable) / sharesOutstanding
        return pricePerShare

    def predictRevenue(self, timeIntoTheFuture, perpetualDiscount):
        finalPredictionDate = np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe")
        return self._revenueObj.getRevenueStreams(self._financialData.loc['Total Revenue'], finalPredictionDate, perpetualDiscount)       

    def predictIncome(self, predictedRevenueStreams, knownIncomeStreams):
        return self._incomeObj.getIncomeStreams(predictedRevenueStreams, knownIncomeStreams)

    
    def getDiscountTable(self, timeSeries):
        return self._discountRateObj.getDiscountRates(timeSeries)

    def getPresentValueTable(self, incomeTable, discountRateTable):
        return self._presentValueObj.getPresentValues(incomeTable, discountRateTable)

    def getTimeIndexes(self, currentTimeIndexes, untilTime):
        lastTime = currentTimeIndexes.values[-1]
        if untilTime <= lastTime:
            return currentTimeIndexes

        totalTimeIndexes = copy.deepcopy(currentTimeIndexes)

        while True:
            lastTime = totalTimeIndexes.values[-1]
            nextTime = np.add(lastTime, np.timedelta64(1, 'Y'), casting="unsafe")
            if untilTime <= nextTime:
                break
            totalTimeIndexes = totalTimeIndexes.union([nextTime])
        return totalTimeIndexes

    def getValuationSummaryTable(self):
        profitabilityTable = self._incomeObj.getProfitabilityTable(self._revenueTable, self._incomeTable)
        cashFlowToNetIncomeTable = self._fcfObj.getCashFlowToNetIncomeRatio(self._fcfeTable, self._incomeTable)
        netBorrowingsTable = self._fcfObj.getNetBorrowingsTable()
        
        # Get growth rates from revenue object
        growthRatesTable = self._revenueObj.getGrowthRates(self._revenueTable.columns)
        
        # Filter out empty DataFrames before concatenation to avoid deprecation warnings
        tables_to_concat = []
        for table in [self._revenueTable, growthRatesTable, self._incomeTable, profitabilityTable, netBorrowingsTable, self._fcfeTable, cashFlowToNetIncomeTable, self._discountTable, self._presentValueTable]:
            if table is not None and not table.empty and table.shape[1] > 0:
                tables_to_concat.append(table)
        
        if tables_to_concat:
            resultTable = pd.concat(tables_to_concat, axis=0)
        else:
            # Create an empty DataFrame if no valid tables
            resultTable = pd.DataFrame()
        resultTable.loc['Fair Value', self._timeNow] = self._pricePerShare
        return resultTable

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

    def setRevenueSpecialistEstimates(self):
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
        else:
            # Fallback to constant growth if no analyst estimates available
            growth_series = pd.Series({
                '0Y': getGlobal('economyGrowth'),
                '+1Y': getGlobal('economyGrowth'),
                '+5Y': getGlobal('economyGrowth')
            })
        
        self._revenueObj = AnalystRevenueGrowth(growth_series, getGlobal('economyGrowth'), self._timeNow)

    def setRevenueConstant(self, value):
        self._revenueObj = ConstantGrowthRevenue(value, getGlobal('economyGrowth'))
