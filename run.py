
import numpy as np
import glob
import os

# Personal package import
from BlockData import BlockData
from bumpFindFit import bumpFindFit
from reportFn import genPeakReportCSV

from saveDimRedPack import save_1Dcsv

peakShape = 'Voigt'
numCurves = 2
fit_order = 2

savePath = '/home/sasha/Desktop/TiNiSn_500C_PeakData_0.01/'

csvFilepath = '/home/sasha/Desktop/TiNiSn_500C-20190604T152446Z-001/TiNiSn_500C/'

csvFiles = os.listdir(csvFilepath)
for f in csvFiles:
    file = os.path.join(csvFilepath,f)
    fileRoot = os.path.splitext(f)[0]

    print(file)
    data = np.genfromtxt(file, delimiter = ',')
    Qlist = data[:,0]
    IntAve = data[:,1]
    dataArray = np.array([Qlist, IntAve])

    dataIn = BlockData(dataArray, fit_order, .01, peakShape) # .5
    #### has various functions
    ##############################################################

    #dataIn.trimData(trimLen=1)

    dataIn.bkgdSub()

    hld = dataIn.subData
    sigmaGuess = np.std(hld[1][hld[1] <= np.median(hld[1])])

    dataIn.cellData = sigmaGuess * np.ones(len(dataIn.subData[0]))

    # incorporate block information into data struct
    dataIn.blockFinder()

    paramDict, litFWHM = bumpFindFit(dataIn, peakShape, numCurves)

    # Generate residual plot using stored optParams
    pctErr = dataIn.genResidPlot()

    genPeakReportCSV(savePath, fileRoot, litFWHM, pctErr)
