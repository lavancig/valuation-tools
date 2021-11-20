import yfinance as yf
from src.revenue.ConstantGrowthRevenue import ConstantGrowthRevenue
from src.income.ConstantMarginIncome import ConstantMarginIncome
from src.discoundRate.ConstantDiscountRate import ConstantDiscountRate
from src.PresentValue import PresentValue
from datetime import date
import numpy as np
import pandas as pd




def mainFunction():
    companyData = yf.Ticker("AAPL") 
    financialDataYF = companyData.financials
    # Flips data because yahoo finance is stupid and the columns are ordered backwards
    financialData= pd.DataFrame(np.asarray(np.fliplr(financialDataYF.values)))
    financialData.columns = np.asarray(np.flip(financialDataYF.columns.values))
    financialData.index = financialDataYF.index

    today = financialData.columns[-1]
    finalPredictionDate = np.add(np.datetime64(today, 'ns'), np.timedelta64(5, 'Y'), casting="unsafe")

    revenueObj = ConstantGrowthRevenue(financialData.iloc[financialData.index == "Total Revenue"], 0.07, 0.025, 0.12)
    revenueTable = revenueObj.getRevenueStreams(finalPredictionDate)


    incomeObj = ConstantMarginIncome(financialData.iloc[financialData.index == "Total Revenue"], financialData.iloc[financialData.index == "Net Income From Continuing Ops"])
    incomeTable = incomeObj.getIncomeStreams(revenueTable, financialData.iloc[financialData.index == "Net Income From Continuing Ops"])

    discountRateObj = ConstantDiscountRate(0.12)
    discountRateTable = discountRateObj.getDiscountRates(incomeTable.columns)

    sharesOutstanding = companyData.info['sharesOutstanding']

    presentValueObj = PresentValue(today)
    presentValueTable = presentValueObj.getPresentValues(incomeTable, discountRateTable)


    print(presentValueObj.getPresentValues(incomeTable, discountRateTable))
    pricePerShare = presentValueObj.getPresentValue(incomeTable, discountRateTable) / sharesOutstanding
    print("Price per share: " + str(pricePerShare))

    # companyData.analysis.loc['0Y', 'Growth']

if __name__ == "__main__":
    mainFunction()