import pandas as pd
import numpy as np

class ConstantIncomeToFCF:
    def __init__(self, financialData, cashFlows):
        nYears = 0
        netIncomeToCashFlowSum = 0
        lastValidFCFO = 0
        
        # Filter out dates with NaN values in key financial data
        validDates = []
        for date in cashFlows.columns:
            if (pd.notna(cashFlows.loc['Operating Cash Flow', date]) and 
                pd.notna(cashFlows.loc['Capital Expenditure', date]) and
                pd.notna(financialData.loc['Net Income From Continuing Operation Net Minority Interest', date])):
                validDates.append(date)
        
        if len(validDates) == 0:
            # Fallback to reasonable ratio if no valid data
            self._cashFlowToNetIncomeRatio = 0.8  # 80% as fallback
            return
        
        for date in validDates:
            nYears = nYears + 1
            fcfo = cashFlows.loc['Operating Cash Flow', date]
            lastValidFCFO = fcfo
            # Include net borrowings in the calculation if available
            netBorrowings = 0
            if 'Net Borrowings' in cashFlows.index and pd.notna(cashFlows.loc['Net Borrowings', date]):
                netBorrowings = cashFlows.loc['Net Borrowings', date]
            
            netIncomeToCashFlowSum = netIncomeToCashFlowSum + (fcfo + cashFlows.loc['Capital Expenditure', date] + netBorrowings)/financialData.loc['Net Income From Continuing Operation Net Minority Interest', date]
        
        if nYears > 0:
            self._cashFlowToNetIncomeRatio = netIncomeToCashFlowSum/nYears
        else:
            # Fallback to reasonable ratio if no valid data
            self._cashFlowToNetIncomeRatio = 0.8  # 80% as fallback

    def setCashFlowToNetIncomeRatio(self, ratio):
        self._cashFlowToNetIncomeRatio = ratio

    def estimateFCFE(self, predictedIncome, cashFlows):
        fcfPredictions = pd.DataFrame([], columns=predictedIncome.columns.values, index=['FCFE'])
        netBorrowingsTable = pd.DataFrame([], columns=predictedIncome.columns.values, index=['Net Borrowings'])
        lastValidNetBorrowings = 0
        
        for date in predictedIncome.columns.values:
            if(date in cashFlows.columns.values):
                # Get net income for this date
                netIncome = cashFlows.loc['Net Income', date] if 'Net Income' in cashFlows.index and pd.notna(cashFlows.loc['Net Income', date]) else predictedIncome.loc['Income', date] if pd.notna(predictedIncome.loc['Income', date]) else 0
                
                # Get D&A (Depreciation & Amortization)
                da = cashFlows.loc['D&A', date] if 'D&A' in cashFlows.index and pd.notna(cashFlows.loc['D&A', date]) else 0
                
                # Get CapEx (Capital Expenditure)
                capex = cashFlows.loc['CapEx', date] if 'CapEx' in cashFlows.index and pd.notna(cashFlows.loc['CapEx', date]) else 0
                
                # Get ΔNWC (Change in Net Working Capital)
                deltaNWC = cashFlows.loc['Delta NWC', date] if 'Delta NWC' in cashFlows.index and pd.notna(cashFlows.loc['Delta NWC', date]) else 0
                
                # Get net borrowings from the calculated data
                netBorrowings = cashFlows.loc['Net Borrowings', date] if 'Net Borrowings' in cashFlows.index and pd.notna(cashFlows.loc['Net Borrowings', date]) else lastValidNetBorrowings
                
                lastValidNetBorrowings = netBorrowings
                
                # Calculate FCFE using the correct formula: FCFE = Net Income + D&A - CapEx - ΔNWC + Net Borrowings
                fcfPredictions.loc['FCFE', date] = netIncome + da - capex - deltaNWC + netBorrowings
                netBorrowingsTable.loc['Net Borrowings', date] = netBorrowings
                continue
            
            # For future years, estimate FCFE using the ratio and assume no net borrowings
            fcfPredictions.loc['FCFE', date] = predictedIncome.loc['Income', date] * self._cashFlowToNetIncomeRatio
            netBorrowingsTable.loc['Net Borrowings', date] = 0  # Assume no net borrowings for future years
        
        # Store net borrowings table for later use
        self._netBorrowingsTable = netBorrowingsTable
        return fcfPredictions

    def estimateFCFF(self, predictedEBIT, cashFlows, taxRateCalculator=None):
        """Estimate Free Cash Flow to Firm (FCFF) - same as FCFE but without net borrowings"""
        fcffPredictions = pd.DataFrame([], columns=predictedEBIT.columns.values, index=['FCFF'])
        taxRateTable = pd.DataFrame([], columns=predictedEBIT.columns.values, index=['Tax Rate'])
        
        for date in predictedEBIT.columns.values:
            if(date in cashFlows.columns.values):
                # Get EBIT for this date
                ebit = cashFlows.loc['EBIT', date] if 'EBIT' in cashFlows.index and pd.notna(cashFlows.loc['EBIT', date]) else predictedEBIT.loc['EBIT', date] if pd.notna(predictedEBIT.loc['EBIT', date]) else 0
                
                # Get D&A (Depreciation & Amortization)
                da = cashFlows.loc['D&A', date] if 'D&A' in cashFlows.index and pd.notna(cashFlows.loc['D&A', date]) else 0
                
                # Get CapEx (Capital Expenditure)
                capex = cashFlows.loc['CapEx', date] if 'CapEx' in cashFlows.index and pd.notna(cashFlows.loc['CapEx', date]) else 0
                
                # Get ΔNWC (Change in Net Working Capital)
                deltaNWC = cashFlows.loc['Delta NWC', date] if 'Delta NWC' in cashFlows.index and pd.notna(cashFlows.loc['Delta NWC', date]) else 0
                
                # Calculate tax rate using TaxRateCalculator
                taxRate = cashFlows.loc['Tax Rate', date]
 # Default tax rate if no calculator provided
                
                # Calculate FCFF using the formula: FCFF = EBIT * (1 - Tax Rate) + D&A - CapEx - ΔNWC
                # Note: FCFF does not include net borrowings (unlike FCFE)
                fcffPredictions.loc['FCFF', date] = ebit * (1 - taxRate) + da - capex - deltaNWC
                continue
        
            
            # fcffPredictions.loc['FCFF', date] = predictedEBIT.loc['EBIT', date] * self._cashFlowToNetIncomeRatio
        
        # Store tax rate table for later use
        return fcffPredictions

    def getCashFlowToNetIncomeRatio(self, predictedCashFlows, predictedIncome):
        cashFlowToNetIncomeRatio = pd.DataFrame([], columns=predictedIncome.columns.values, index=['Cash Flow To Net Income Ratio'])
        for date in cashFlowToNetIncomeRatio.columns.values:
            # Handle both FCFE and FCFF
            if 'FCFE' in predictedCashFlows.index:
                cashFlowToNetIncomeRatio.loc['Cash Flow To Net Income Ratio', date] = predictedCashFlows.loc['FCFE', date] / predictedIncome.loc['Income', date]
            elif 'FCFF' in predictedCashFlows.index:
                cashFlowToNetIncomeRatio.loc['Cash Flow To Net Income Ratio', date] = predictedCashFlows.loc['FCFF', date] / predictedIncome.loc['Income', date]
        return cashFlowToNetIncomeRatio
    
    def getNetBorrowingsTable(self):
        """Get the net borrowings table"""
        if hasattr(self, '_netBorrowingsTable'):
            return self._netBorrowingsTable
        else:
            return pd.DataFrame()
    
    def getTaxRateTable(self):
        """Get the tax rate table"""
        if hasattr(self, '_taxRateTable'):
            return self._taxRateTable
        else:
            return pd.DataFrame()