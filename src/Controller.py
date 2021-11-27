
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
