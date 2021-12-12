from datetime import date
from .DiscountRateBase import DiscountRateBase
from .ConstantDiscountRate import ConstantDiscountRate
import pandas as pd
import numpy as np 
import copy

DEFAULT_COST_OF_DEBT = 0.04

class WACCDiscountRate(DiscountRateBase):
    
    def __init__(self, companyFinancials, companyBalanceSheet, riskFreeInterestRate, marketReturnRate, companyBeta):
        lastTime = companyFinancials.columns.values[-1]

        if(companyFinancials.loc['Interest Expense', lastTime] == None):
            costOfDebt = DEFAULT_COST_OF_DEBT
        else:
            costOfDebt =  -companyFinancials.loc['Interest Expense', lastTime] / companyBalanceSheet.loc['Total Liab', lastTime]
        
        taxRate = companyFinancials.loc['Income Tax Expense', lastTime] / companyFinancials.loc['Income Before Tax', lastTime]

        if(companyBeta == None): # Not enough data to calculate beta for the company
            companyBeta = 2
        costOfEquity = riskFreeInterestRate + companyBeta * (marketReturnRate - riskFreeInterestRate)

        wDebt = companyBalanceSheet.loc['Total Liab', lastTime] / (companyBalanceSheet.loc['Total Liab', lastTime] + companyBalanceSheet.loc['Total Stockholder Equity', lastTime])

        wEquity = companyBalanceSheet.loc['Total Stockholder Equity', lastTime] / (companyBalanceSheet.loc['Total Liab', lastTime] + companyBalanceSheet.loc['Total Stockholder Equity', lastTime])

        discountRate = wDebt * costOfDebt * (1 - taxRate) + wEquity * costOfEquity

        self._constantDiscountRateObj = ConstantDiscountRate(discountRate)


    def getDiscountRates(self, dates):
        return self._constantDiscountRateObj.getDiscountRates(dates)


    def getType():
        return "WACC"