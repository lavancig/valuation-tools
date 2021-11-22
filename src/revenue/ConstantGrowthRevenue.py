from .RevenueBase import RevenueBase
import pandas as pd
import numpy as np 
import copy

class ConstantGrowthRevenue(RevenueBase):
    
    def __init__(self, growthRate, perpetualGrowthRate):
        self._growthRate = growthRate
        self._perpetualGrowthRate = perpetualGrowthRate

    def getRevenueStreams(self, revenueStreams, untilTime, perpetualDiscount):
        lastTime = revenueStreams.index.values[-1]
        if untilTime <= lastTime:
            return revenueStreams

        revenueStreamPredictions = copy.deepcopy(revenueStreams)

        while True:
            lastTime = revenueStreamPredictions.index.values[-1]
            nextTime = np.add(lastTime, np.timedelta64(1, 'Y'), casting="unsafe")
            if untilTime <= nextTime:
                break
            lastRevenue = revenueStreamPredictions[lastTime]
            revenueStreamPredictions[ nextTime] = lastRevenue * (1 + self._growthRate)
            
        lastTime = revenueStreamPredictions.index.values[-1]
        lastRevenue = revenueStreamPredictions[ lastTime]
        revenueStreamPredictions['perpetual'] = lastRevenue * (1 + self._perpetualGrowthRate) / ( perpetualDiscount - self._perpetualGrowthRate)
        return revenueStreamPredictions


