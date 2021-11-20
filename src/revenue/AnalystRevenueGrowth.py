from .RevenueBase import RevenueBase
import pandas as pd
import numpy as np 
import copy

class ConstantGrowthRevenue(RevenueBase):
    
    def __init__(self, knownRevenueStreams, analystEstimates, perpetualGrowthRate, perpetualDiscount):
        self._knownRevenueStreams = knownRevenueStreams
        self._analystEstimates = analystEstimates
        self._perpetualGrowthRate = perpetualGrowthRate
        self._perpetualDiscount = perpetualDiscount

    def getRevenueStreams(self, untilTime):
        lastTime = self._knownRevenueStreams.columns.values[-1]
        if untilTime <= lastTime:
            return self._knownRevenueStreams

        revenueStreamPredictions = copy.deepcopy(self._knownRevenueStreams)

        while True:
            nextTime = np.add(lastTime, np.timedelta64(1, 'Y'), casting="unsafe")
            if untilTime <= nextTime:
                break
            lastTime = revenueStreamPredictions.columns.values[-1]
            lastRevenue = revenueStreamPredictions.loc['Total Revenue', lastTime]
            revenueStreamPredictions.loc['Total Revenue', nextTime] = lastRevenue * (1 + self._growthRate)
            
        lastTime = revenueStreamPredictions.columns.values[-1]
        lastRevenue = revenueStreamPredictions.loc['Total Revenue', lastTime]
        revenueStreamPredictions.loc['Total Revenue','perpetual'] = lastRevenue * (1 + self._perpetualGrowthRate) / ( self._perpetualDiscount - self._perpetualGrowthRate)
        return revenueStreamPredictions


