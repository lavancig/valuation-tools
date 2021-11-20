# Base class to return revenue streams

class RevenueBase:
    
    def __init__(self):
        pass

    def getRevenueStreams(self, timePeriod):
        raise NotImplementedError("Please implement getRevenueStreams method in concrete revenue class")