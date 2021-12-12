import pandas as pd
import numpy as np

class ConstantIncomeToFCF:
    def __init__(self, financialData, cashFlows):
        nYears = 0
        netIncomeToCashFlowSum = 0
        lastValidFCFO = 0
        for date in cashFlows.columns:
            nYears = nYears + 1
            fcfo = cashFlows.loc['Total Cash From Operating Activities', date] if not np.isnan(cashFlows.loc['Total Cash From Operating Activities', date]) else lastValidFCFO
            lastValidFCFO = fcfo
            netIncomeToCashFlowSum = netIncomeToCashFlowSum + (fcfo + cashFlows.loc['Capital Expenditures', date])/financialData.loc['Net Income From Continuing Ops', date]
        self._cashFlowToNetIncomeRatio = netIncomeToCashFlowSum/nYears

    def setCashFlowToNetIncomeRatio(self, ratio):
        self._cashFlowToNetIncomeRatio = ratio

    def estimateFCFE(self, predictedIncome, cashFlows):
        fcfPredictions = pd.DataFrame([], columns=predictedIncome.columns.values, index=['FCFE'])
        lastValidFCFO = 0
        for date in predictedIncome.columns.values:
            if(date in cashFlows.columns.values):
                fcfo = cashFlows.loc['Total Cash From Operating Activities', date] if not np.isnan(cashFlows.loc['Total Cash From Operating Activities', date]) else lastValidFCFO
                lastValidFCFO = fcfo
                fcfPredictions.loc['FCFE', date] = fcfo + cashFlows.loc['Capital Expenditures', date]
                continue
            fcfPredictions.loc['FCFE', date] = predictedIncome.loc['Income', date] * self._cashFlowToNetIncomeRatio
        return fcfPredictions

    def getCashFlowToNetIncomeRatio(self, predictedCashFlows, predictedIncome):
        cashFlowToNetIncomeRatio = pd.DataFrame([], columns=predictedIncome.columns.values, index=['Cash Flow To Net Income Ratio'])
        for date in cashFlowToNetIncomeRatio.columns.values:
            cashFlowToNetIncomeRatio.loc['Cash Flow To Net Income Ratio', date] = predictedCashFlows.loc['FCFE', date] / predictedIncome.loc['Income', date]
        return cashFlowToNetIncomeRatio