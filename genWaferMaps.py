import os, sys
import glob
from save_wafer_heatMap import FWHMmap, contrastMap
'''
Takes data path and generates heatmaps based on existing master files

Skips data analysis / image reduction

'''
############ INPUT PARAMETERS HERE ################
dataPath = os.path.expanduser('/home/b_mehta/data/bl2-2/MG/2293_new/')

threshFWHM = 0.57
########### END INPUT PARAMETERS ##################

# find single file for feeding into pre-existing functions
fileList = glob.glob(os.path.join(dataPath, '*.tiff'))
if len(fileList) == 0:
    sys.exit('No files found')

FWHMmap(fileList[0])                    # generates both normal FWHM and key maps
contrastMap(fileList[0], threshFWHM)    # generates contrast heatmap
