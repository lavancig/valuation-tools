from datetime import date
from .DiscountRateBase import DiscountRateBase
from .ConstantDiscountRate import ConstantDiscountRate
import pandas as pd
import numpy as np 

class CostOfEquityDiscountRate(DiscountRateBase):
    
    def __init__(self, riskFreeInterestRate, marketReturnRate, companyBeta):
        """
        Calculate cost of equity using CAPM formula:
        Cost of Equity = Risk-Free Rate + Beta * (Market Return - Risk-Free Rate)
        
        Args:
            riskFreeInterestRate (float): Risk-free interest rate (e.g., 10-year Treasury yield)
            marketReturnRate (float): Expected market return (e.g., historical S&P 500 return)
            companyBeta (float): Company's beta coefficient (systematic risk measure)
        """
        
        if companyBeta is None:
            # Default beta if not available
            companyBeta = 1.0
            print(f"Warning: No beta data. Using default beta: {companyBeta}")
        
        # Calculate cost of equity using CAPM
        costOfEquity = riskFreeInterestRate + companyBeta * (marketReturnRate - riskFreeInterestRate)
        
        print(f"Cost of equity calculated: {costOfEquity:.4f}")
        print(f"  - Risk-free rate: {riskFreeInterestRate:.4f}")
        print(f"  - Market return: {marketReturnRate:.4f}")
        print(f"  - Beta: {companyBeta:.2f}")
        print(f"  - Market risk premium: {marketReturnRate - riskFreeInterestRate:.4f}")
        
        # Ensure cost of equity is reasonable
        if costOfEquity <= 0:
            print(f"Warning: Calculated cost of equity ({costOfEquity:.4f}) is not positive. Using 10% as fallback.")
            costOfEquity = 0.10
        elif costOfEquity > 1.0:
            print(f"Warning: Calculated cost of equity ({costOfEquity:.4f}) is unreasonably high. Capping at 50%.")
            costOfEquity = 0.50
        
        # Store the calculated cost of equity
        self._costOfEquity = costOfEquity
        
        # Create a constant discount rate object with the calculated cost of equity
        self._constantDiscountRateObj = ConstantDiscountRate(costOfEquity)

    def getDiscountRates(self, dates):
        """Return discount rates for all dates (same cost of equity for all periods)"""
        return self._constantDiscountRateObj.getDiscountRates(dates)
    
    def getCostOfEquity(self):
        """Get the calculated cost of equity"""
        return self._costOfEquity

    def getType():
        return "Cost of Equity"
