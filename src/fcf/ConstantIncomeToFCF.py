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
        lastValidFCFO = 0
        lastValidNetBorrowings = 0
        
        for date in predictedIncome.columns.values:
            if(date in cashFlows.columns.values):
                fcfo = cashFlows.loc['Operating Cash Flow', date] if pd.notna(cashFlows.loc['Operating Cash Flow', date]) else lastValidFCFO
                capex = cashFlows.loc['Capital Expenditure', date] if pd.notna(cashFlows.loc['Capital Expenditure', date]) else 0
                # Get net borrowings from the calculated data
                netBorrowings = cashFlows.loc['Net Borrowings', date] if 'Net Borrowings' in cashFlows.index and pd.notna(cashFlows.loc['Net Borrowings', date]) else lastValidNetBorrowings
                
                lastValidFCFO = fcfo
                lastValidNetBorrowings = netBorrowings
                
                fcfPredictions.loc['FCFE', date] = fcfo + capex + netBorrowings
                netBorrowingsTable.loc['Net Borrowings', date] = netBorrowings
                continue
            
            # For future years, estimate FCFE using the ratio and assume no net borrowings
            fcfPredictions.loc['FCFE', date] = predictedIncome.loc['Income', date] * self._cashFlowToNetIncomeRatio
            netBorrowingsTable.loc['Net Borrowings', date] = 0  # Assume no net borrowings for future years
        
        # Store net borrowings table for later use
        self._netBorrowingsTable = netBorrowingsTable
        return fcfPredictions

    def getCashFlowToNetIncomeRatio(self, predictedCashFlows, predictedIncome):
        cashFlowToNetIncomeRatio = pd.DataFrame([], columns=predictedIncome.columns.values, index=['Cash Flow To Net Income Ratio'])
        for date in cashFlowToNetIncomeRatio.columns.values:
            cashFlowToNetIncomeRatio.loc['Cash Flow To Net Income Ratio', date] = predictedCashFlows.loc['FCFE', date] / predictedIncome.loc['Income', date]
        return cashFlowToNetIncomeRatio
    
    def getNetBorrowingsTable(self):
        """Get the net borrowings table"""
        if hasattr(self, '_netBorrowingsTable'):
            return self._netBorrowingsTable
        else:
            return pd.DataFrame()