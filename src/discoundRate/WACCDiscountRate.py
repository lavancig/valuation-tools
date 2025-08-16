from datetime import date
from .DiscountRateBase import DiscountRateBase
from .ConstantDiscountRate import ConstantDiscountRate
import pandas as pd
import numpy as np 
import copy

DEFAULT_COST_OF_DEBT = 0.04

class WACCDiscountRate(DiscountRateBase):
    
    def __init__(self, companyFinancials, companyBalanceSheet, riskFreeInterestRate, marketReturnRate, companyBeta, sharesOutstanding=None, sharePrice=None):
        # Find the most recent year with valid interest expense data
        validTime = None
        for col in companyFinancials.columns:
            if pd.notna(companyFinancials.loc['Interest Expense', col]):
                validTime = col
                break
        
        if validTime is None:
            # If no valid interest expense data found, use default
            costOfDebt = DEFAULT_COST_OF_DEBT
            print(f"Warning: No valid interest expense data found. Using default cost of debt: {costOfDebt:.4f}")
        else:
            # Ensure interest expense is positive for calculation (financial statements often show it as negative)
            interestExpense = abs(companyFinancials.loc['Interest Expense', validTime])
            totalDebt = companyBalanceSheet.loc['Total Debt', validTime]
            
            if totalDebt <= 0:
                print(f"Warning: Total Liabilities ({totalDebt:.2f}) is not positive. Using default cost of debt.")
                costOfDebt = DEFAULT_COST_OF_DEBT
            else:
                costOfDebt = interestExpense / totalDebt
                print(f"Cost of debt calculated: {costOfDebt:.4f} (Interest: {interestExpense:.2f}, Liabilities: {totalDebt:.2f})")
        
        # Use the same valid time for tax rate calculation
        if validTime is not None:
            taxProvision = companyFinancials.loc['Tax Provision', validTime]
            pretaxIncome = companyFinancials.loc['Pretax Income', validTime]
            
            if pretaxIncome == 0 or pd.isna(pretaxIncome):
                print(f"Warning: Pretax Income is {pretaxIncome}. Using default tax rate.")
                taxRate = 0.25
            else:
                taxRate = abs(taxProvision) / abs(pretaxIncome)
                # Ensure tax rate is reasonable (between 0 and 1)
                taxRate = max(0.0, min(0.4, taxRate))
                print(f"Tax rate calculated: {taxRate:.4f} (Tax: {taxProvision:.2f}, Pretax: {pretaxIncome:.2f})")
        else:
            # Fallback tax rate if no valid data
            taxRate = 0.25  # 25% corporate tax rate as fallback
            print(f"Using fallback tax rate: {taxRate:.4f}")

        if(companyBeta == None): # Not enough data to calculate beta for the company
            companyBeta = 2
            print(f"Warning: No beta data. Using default beta: {companyBeta}")
        
        costOfEquity = riskFreeInterestRate + companyBeta * (marketReturnRate - riskFreeInterestRate)
        print(f"Cost of equity calculated: {costOfEquity:.4f} (Rf: {riskFreeInterestRate:.4f}, Beta: {companyBeta:.2f}, Rm: {marketReturnRate:.4f})")

        # Use the most recent year for balance sheet data (should have valid data)
        lastTime = companyBalanceSheet.columns.values[0]
        totalDebt = companyBalanceSheet.loc['Total Debt', lastTime]
        
        # Calculate total equity using shares outstanding times share price if available
        if sharesOutstanding is not None and sharePrice is not None:
            totalEquity = sharesOutstanding * sharePrice
            print(f"Total equity calculated from market data: {totalEquity:.2f} (Shares: {sharesOutstanding:.0f}, Price: {sharePrice:.2f})")
        else:
            # Fallback to balance sheet equity if market data not available
            totalEquity = companyBalanceSheet.loc['Common Stock Equity', lastTime]
            print(f"Total equity from balance sheet: {totalEquity:.2f}")
        
        # Ensure balance sheet values are positive
        if totalDebt <= 0 or totalEquity <= 0:
            print(f"Warning: Balance sheet values are not positive. Liabilities: {totalDebt:.2f}, Equity: {totalEquity:.2f}")
            print("Using simplified WACC calculation without debt component.")
            discountRate = costOfEquity
        else:
            totalCapital = totalDebt + totalEquity
            wDebt = totalDebt / totalCapital
            wEquity = totalEquity / totalCapital
            
            print(f"Weights calculated: Debt: {wDebt:.4f}, Equity: {wEquity:.4f}")
            print(f"Balance sheet: Liabilities: {totalDebt:.2f}, Equity: {totalEquity:.2f}")
            
            discountRate = wDebt * costOfDebt * (1 - taxRate) + wEquity * costOfEquity

        print(f"Final WACC calculated: {discountRate:.4f}")
        
        # Ensure discount rate is positive and reasonable
        if discountRate <= 0:
            print(f"Warning: Calculated WACC ({discountRate:.4f}) is not positive. Using cost of equity as fallback.")
            discountRate = costOfEquity
        elif discountRate > 1.0:
            print(f"Warning: Calculated WACC ({discountRate:.4f}) is unreasonably high. Capping at 50%.")
            discountRate = 0.50

        self._constantDiscountRateObj = ConstantDiscountRate(discountRate)


    def getDiscountRates(self, dates):
        return self._constantDiscountRateObj.getDiscountRates(dates)


    def getType():
        return "WACC"