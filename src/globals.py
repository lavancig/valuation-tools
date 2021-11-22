import os
from os.path import exists
import pickle


GLOBAL_VAR_DEFAULTS = {"RiskFreeInterestRate" : 0.0232,
    "marketReturn": 0.1,
    "economyGrowth": 0.0293}
globalVars = GLOBAL_VAR_DEFAULTS


def getGlobals():
    return globalVars

def getGlobal(tag):
    return globalVars[tag]

def setGlobal(tag, value):
    globalVars[tag] = value

def saveGlobals():
    global globalVars
    dirname = os.path.dirname(__file__)
    globalVarPickleFilename = os.path.join(dirname,"../usr/global.p")
    pickle.dump( globalVars, open( globalVarPickleFilename, "wb" ) )

def loadGlobals():
    global globalVars
    dirname = os.path.dirname(__file__)
    globalVarPickleFilename = os.path.join(dirname,"../usr/global.p")
    if( exists(globalVarPickleFilename )):
        globalVars = pickle.load( open( globalVarPickleFilename, "rb" ) ) 

def resetGlobals():
    global globalVars
    globalVars = GLOBAL_VAR_DEFAULTS
    saveGlobals()
