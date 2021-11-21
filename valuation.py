import yfinance as yf

from src.revenue.ConstantGrowthRevenue import ConstantGrowthRevenue
from src.revenue.AnalystRevenueGrowth import AnalystRevenueGrowth

from src.income.ConstantMarginIncome import ConstantMarginIncome

from src.discoundRate.ConstantDiscountRate import ConstantDiscountRate
from src.discoundRate.WACCDiscountRate import WACCDiscountRate

from src.PresentValue import PresentValue

from datetime import date
import numpy as np
import pandas as pd




def mainFunction():
    RISK_FREE_INTEREST_RATE = 0.0232
    MARKET_RETURN = 0.1

    companyData = yf.Ticker("MU") 
    financialDataYF = companyData.financials
    # Flips data because yahoo finance is stupid and the columns are ordered backwards
    financialData= pd.DataFrame(np.asarray(np.fliplr(financialDataYF.values)))
    financialData.columns = np.asarray(np.flip(financialDataYF.columns.values))
    financialData.index = financialDataYF.index

    # Flips data because yahoo finance is stupid and the columns are ordered backwards
    balancesheetDataYF = companyData.balancesheet
    balancesheetData = pd.DataFrame(np.asarray(np.fliplr(balancesheetDataYF.values)))
    balancesheetData.columns = np.asarray(np.flip(balancesheetDataYF.columns.values))
    balancesheetData.index = balancesheetDataYF.index

    timeNow = financialData.columns[-1]
    finalPredictionDate = np.add(np.datetime64(timeNow, 'ns'), np.timedelta64(5, 'Y'), casting="unsafe")

    # revenueObj = ConstantGrowthRevenue(0.07, 0.025, 0.12)
    revenueObj = AnalystRevenueGrowth(companyData.analysis['Growth'], 0.025, 0.12, timeNow)
    revenueTable = revenueObj.getRevenueStreams(financialData.iloc[financialData.index == "Total Revenue"], finalPredictionDate)


    incomeObj = ConstantMarginIncome(financialData.iloc[financialData.index == "Total Revenue"], financialData.iloc[financialData.index == "Net Income From Continuing Ops"])
    incomeTable = incomeObj.getIncomeStreams(revenueTable, financialData.iloc[financialData.index == "Net Income From Continuing Ops"])

    # discountRateObj = ConstantDiscountRate(0.12)
    discountRateObj = WACCDiscountRate(financialData, balancesheetData, RISK_FREE_INTEREST_RATE, MARKET_RETURN, companyData.info['beta'])
    discountRateTable = discountRateObj.getDiscountRates(incomeTable.columns)

    sharesOutstanding = companyData.info['sharesOutstanding']

    presentValueObj = PresentValue(timeNow)
    presentValueTable = presentValueObj.getPresentValues(incomeTable, discountRateTable)



    print(presentValueObj.getPresentValues(incomeTable, discountRateTable))
    pricePerShare = presentValueObj.getPresentValue(incomeTable, discountRateTable) / sharesOutstanding
    print("Price per share: " + str(pricePerShare))

    # companyData.analysis.loc['0Y', 'Growth']


    # financialData.loc['Interest Expense']
    # companyData.financials.loc['Total Liab']


    # Cost of debt = -financialData.loc['Interest Expense']/companyData.financials.loc['Total Liab']


    # Tax Rate = financialData.loc['Income Tax Expense'] / financialData.loc['Income Before Tax']

    # beta = companyData.info['beta']

    # weight Debt = companyData.financials.loc['Total Liab'] / (companyData.financials.loc['Total Liab'] + companyData.financials.loc['Total Stockholder Equity'])
    # weight Equity = companyData.financials.loc['Total Stockholder Equity'] / (companyData.financials.loc['Total Liab'] + companyData.financials.loc['Total Stockholder Equity'])


if __name__ == "__main__":
    mainFunction()