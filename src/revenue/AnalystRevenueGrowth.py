from pandas.core.indexes.base import Index
from .RevenueBase import RevenueBase
import pandas as pd
import numpy as np 
import copy

class AnalystRevenueGrowth(RevenueBase):
    
    def __init__(self, analystEstimates, perpetualGrowthRate, timeNow):
        self._analystEstimates = analystEstimates
        self._perpetualGrowthRate = perpetualGrowthRate
        self._timeNow = timeNow

    def getRevenueStreams(self, knownRevenueStreams, untilTime, perpetualDiscount):
        lastTime = knownRevenueStreams.index.values[-1]
        if untilTime <= lastTime:
            return knownRevenueStreams

        revenueStreamPredictions = pd.DataFrame([knownRevenueStreams.values], columns=knownRevenueStreams.index, index=['Revenue'])

        while True:
            lastTime = revenueStreamPredictions.columns.values[-1]
            nextTime = np.add(lastTime, np.timedelta64(1, 'Y'), casting="unsafe")
            if untilTime <= nextTime:
                break
            
            timeDistance = np.datetime64(nextTime, 'Y') - np.datetime64(self._timeNow, 'Y')
            growthRate = 0
            if timeDistance.astype(int) == 1:
                growthRate = self._analystEstimates.loc['0Y']
            elif timeDistance.astype(int) == 2:
                growthRate = self._analystEstimates.loc['+1Y']
            elif (timeDistance.astype(int) > 2) and (timeDistance.astype(int) <= 7):
                growthRate = self._analystEstimates.loc['+5Y']
            else:
                growthRate = self._perpetualGrowthRate
            lastRevenue = revenueStreamPredictions.loc['Revenue', lastTime]
            revenueStreamPredictions.loc['Revenue', nextTime] = lastRevenue * (1 + growthRate)
            
        lastTime = revenueStreamPredictions.columns.values[-1]
        lastRevenue = revenueStreamPredictions.loc['Revenue', lastTime]
        revenueStreamPredictions.loc['Revenue', 'perpetual'] = lastRevenue * (1 + self._perpetualGrowthRate) / ( perpetualDiscount - self._perpetualGrowthRate)
        return revenueStreamPredictions


