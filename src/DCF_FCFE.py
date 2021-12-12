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
        self._revenueObj = AnalystRevenueGrowth(self._analysis['Growth'], getGlobal('economyGrowth'), self._timeNow)
        # self._revenueObj = ConstantGrowthRevenue(0.07, 0.025, 0.12)

        # Income Projection Object
        self._incomeObj = ConstantMarginIncome(self._financialData.loc['Total Revenue'], self._financialData.loc['Net Income From Continuing Ops'])
        
        # Free cash flow object
        self._fcfObj = ConstantIncomeToFCF(self._financialData, self._cashFlowData)

        # Discount Rate Object
        self._discountRateObj = WACCDiscountRate(self._financialData, self._balancesheetData, getGlobal('RiskFreeInterestRate'), getGlobal('marketReturn'), self._companyInfo['beta'])
        # discountRateObj = ConstantDiscountRate(0.12)

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
        # Flips data because yahoo finance is stupid and the columns are ordered backwards
        self._financialData = pd.DataFrame(np.asarray(np.fliplr(financialDataYF.values)))
        self._financialData.columns = np.asarray(np.flip(financialDataYF.columns.values))
        self._financialData.index = financialDataYF.index

        # Flips data because yahoo finance is stupid and the columns are ordered backwards
        balancesheetDataYF = self._companyData.balancesheet
        self._balancesheetData = pd.DataFrame(np.asarray(np.fliplr(balancesheetDataYF.values)))
        self._balancesheetData.columns = np.asarray(np.flip(balancesheetDataYF.columns.values))
        self._balancesheetData.index = balancesheetDataYF.index

        # Flips data because yahoo finance is stupid and the columns are ordered backwards
        cashFlowDataYF = self._companyData.cashflow
        self._cashFlowData = pd.DataFrame(np.asarray(np.fliplr(cashFlowDataYF.values)))
        self._cashFlowData.columns = np.asarray(np.flip(cashFlowDataYF.columns.values))
        self._cashFlowData.index = cashFlowDataYF.index

        # analysis data
        self._analysis = self._companyData.analysis

        # company info
        self._companyInfo = self._companyData.info

        # Last known year
        self._timeNow = self._financialData.columns[-1]

    def calculateFairValue(self, timeIntoTheFuture):

        timeUntil = np.add(np.datetime64(self._timeNow, 'ns'), np.timedelta64(timeIntoTheFuture, 'Y'), casting="unsafe")
        self._discountTable = self.getDiscountTable(self.getTimeIndexes(self._financialData.columns, timeUntil))

        self._revenueTable = self.predictRevenue(timeIntoTheFuture, self._discountTable.loc['Discount Rate', 'perpetual'])
        self._incomeTable = self.predictIncome(self._revenueTable, self._financialData.loc['Net Income From Continuing Ops'])

        # Calculates FCFE
        self._fcfeTable = self._fcfObj.estimateFCFE(self._incomeTable, self._cashFlowData)

        # Gets shares outstanding from company info
        if 'sharesOutstanding' in self._companyInfo:
            self._sharesOutstanding = self._companyInfo['sharesOutstanding']
        else:
            self._sharesOutstanding = 1
        # self._sharesOutstanding = self._balancesheetData.loc['Common Stock'][-1]

        self._presentValueTable = self.getPresentValueTable(self._fcfeTable, self._discountTable)
        self._pricePerShare = self._presentValueObj.getPresentValue(self._fcfeTable, self._discountTable) / self._sharesOutstanding
        return self._pricePerShare

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
        resultTable = pd.concat([self._revenueTable, self._incomeTable, profitabilityTable, self._fcfeTable, cashFlowToNetIncomeTable, self._discountTable, self._presentValueTable])
        resultTable.loc['Fair Value', self._timeNow] = self._pricePerShare
        return resultTable

    def getFairValue(self):
        return self._pricePerShare

    def setDiscountWACC(self):
        self._discountRateObj = WACCDiscountRate(self._financialData, self._balancesheetData, getGlobal('RiskFreeInterestRate'), getGlobal('marketReturn'), self._companyInfo['beta'])

    def setDiscountConstant(self, value):
        self._discountRateObj = ConstantDiscountRate(value)

    def setProfitabilityConstant(self, value):
        self._incomeObj.setProfitability(value)

    def setProfitabilityLastYearsAverage(self):
        self._incomeObj = ConstantMarginIncome(self._financialData.loc['Total Revenue'], self._financialData.loc['Net Income From Continuing Ops'])

    def setSharesOutstanding(self, number):
        self._sharesOutstanding = number

    def getSharesOutstanding(self):
        return self._sharesOutstanding

    def setFCFConstant(self, value):
        self._fcfObj.setCashFlowToNetIncomeRatio(value)

    def setFCFLastYearsAverage(self):
        self._fcfObj = ConstantIncomeToFCF(self._financialData, self._cashFlowData)

    def setRevenueSpecialistEstimates(self):
        self._revenueObj = AnalystRevenueGrowth(self._analysis['Growth'], getGlobal('economyGrowth'), self._timeNow)

    def setRevenueConstant(self, value):
        self._revenueObj = ConstantGrowthRevenue(value, getGlobal('economyGrowth'))
