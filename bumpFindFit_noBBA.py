import numpy as np
from peakFitResidIter import peakFit, calcFWHM
from peakFitResidIter2 import peakFitVar

def bumpFindFit(dat, peakShape, numCurves, config, savePath = None, filename = None):
    ''' Separate data into peaks and fit them.  Plot fitted peaks and plot output.
    *Use hill climbing to find local max
    *Incorporate blocks that climbed to bump as peaks
    *Fit bumps using desired curve and number per peak

    input: data array (x,y), desired peak shape, num curves per peak, save info
    output: peak data dictionary
            #: Array of arrays [numCurves x numParamsPerCurve]
    '''

    #numBlocks = len(dat.rateVec)
    # add beginning and ending changePoints

    #cpUse = np.concatenate(([1], dat.changePoints, [len(dat.subData[1])]))
    #dat.changePoints = cpUse
    fullData = dat.data
    numBlocks = len(fullData)

    # Find maxima defining watersheds, scan for 
    # highest neighbor of each block
    idMax = np.zeros(len(fullData))

    idMax[ idMax > numBlocks] = len(fullData) 
    idMax[ idMax < 0] = 0

    # Implement hill climbing (HOP algorithm)
    hopIndex = np.array(range(len(fullData))) # init: all blocks point to self
    hopIndex = hopIndex.astype(int)  # cast all as int
    ctr = 0
    while ctr <= 10000000:
        newIndex = idMax[hopIndex]  # Point each to highest neighbor

        if np.array_equal(newIndex, hopIndex):
            break
        else:
            hopIndex = newIndex.astype(int)
            
        ctr += 1
        
        if ctr == 10000000:
            print('Hill climbing did not converge...?')

    idMax = np.unique(hopIndex)
    numMax = len(idMax)
    print('number of points: {}'.format(len(fullData)))
    ###################################################################
    # collect data for each bump (peak).
    iCntMax = 0

    paramDict = {'numCurves': numCurves, 'peakShape': peakShape}
    dat.litFWHM = {}
    dat.peakDomains = {}  # Datum for each peak
    dat.optParams = {}    # Optimized params for each peak

    # For each peak
    for k in range(numMax):
        optParamFWHM = []
        currMax = idMax[k] 

        # find info on current max block
        maxBumpInd = np.fix((idLeftVec[currMax] 
                             + idRightVec[currMax]) / 2) # center of block
        currVec = np.where(hopIndex == currMax)[0] # vector of blocks contributing to currMax
        currNumBlocks = len(currVec)
        
        # indices for start and end of bump
        leftDatum  = idLeftVec[currVec[0]] - 1
        rightDatum = idRightVec[currVec[currNumBlocks-1]] - 1
       
        ############################################################################## 
        # Get parameters from peak fit
        if (savePath != None) and (filename != None):
            if config['fitMode'] == 'var':
                optParam, FWHM = peakFitVar(dat.subData, leftDatum, rightDatum, 
                                    peakShape, numCurves, savePath, filename)
            else: #Default action=fit with set number of peaks
                optParam, FWHM = peakFit(dat.subData, leftDatum, rightDatum, 
                                    peakShape, numCurves, savePath, filename)
        else:
            optParam, FWHM = peakFit(dat.subData, leftDatum, rightDatum, 
                                peakShape, numCurves)


        # Append FWHM to larger optimized parameters list
        for j in range(len(optParam)):
            optParamFWHM.append(np.append(optParam[j], FWHM[j]))

        ############################################################################## 
        # add to dictionary
        paramDict[k] = optParamFWHM
        dat.peakDomains[k] = (leftDatum, rightDatum)
        dat.optParams[k] = optParam
        
        ############################################################################## 
        # Calculate FWHM in a literal sense

        dat.litFWHM[k] = calcFWHM(dat.subData, leftDatum, rightDatum)
        
    return paramDict, dat.litFWHM
