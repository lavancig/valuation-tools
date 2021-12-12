
from .ValuationModel import ValuationModel


class Controller:
    def __init__(self, guiObj, modelObj):
        self._guiObj = guiObj
        self._modelObj = modelObj

    def calculateFairValueRequest(self, type, predictionWindow, ticker):
        self._modelObj.requestFairValueCalculation(type, predictionWindow, ticker)
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())
        self._guiObj.setSharesOutstanding(self._modelObj.getSharesOutstanding())

    def setDiscountTypeWACC(self):
        self._modelObj.setDiscountTypeWACC()
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())


    def setDiscountTypeConstant(self, value):
        self._modelObj.setDiscountTypeConstant(value)
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())

    def setProfitabilityTypeAverage(self):
        self._modelObj.setProfitabilityTypeLastYearsAverage()
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())

    def setProfitabilityTypeConstant(self, value):
        self._modelObj.setProfitabilityTypeConstant(value)
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())

    def setSharesOutstanding(self, number):
        self._modelObj.setSharesOutstanding(number)
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())
        self._guiObj.setSharesOutstanding(number)

    def setFCFTypeConstant(self, value):
        self._modelObj.setFCFConstant(value)
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())
        self._guiObj.setSharesOutstanding(self._modelObj.getSharesOutstanding())
    
    def setFCFTypeLastYearsAverage(self):
        self._modelObj.setFCFLastYearsAverage()
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())
        self._guiObj.setSharesOutstanding(self._modelObj.getSharesOutstanding())


    def setRevenueTypeAverage(self):
        self._modelObj.setRevenueSpecialistEstimates()
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())
        self._guiObj.setSharesOutstanding(self._modelObj.getSharesOutstanding())

    def setRevenueTypeConstant(self, value):
        self._modelObj.setRevenueConstant(value)
        summaryTable = self._modelObj.getValuationSummaryTable()
        self._guiObj.updateValuationSummaryTable(summaryTable)
        self._guiObj.updteFairValue( self._modelObj.getFairValue())
        self._guiObj.setSharesOutstanding(self._modelObj.getSharesOutstanding())

