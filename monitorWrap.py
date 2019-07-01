import pyinotify
import os, sys
import numpy
import Tkinter, tkFileDialog
from monDimReduce import SAXSDimReduce
from peakBBA import peakFitBBA
from save_wafer_heatMap import FWHMmap
from input_file_parsing import parse_config

class EventProcessor(pyinotify.ProcessEvent):
    '''
    Event Processor.  use to customize reactions to files being created.
    '''
    _methods = ["IN_OPEN",
                "IN_ACCESS",
                "IN_ATTRIB",
                "IN_CLOSE_NOWRITE",
                "IN_CLOSE_WRITE",
                "IN_DELETE",
                "IN_DELETE_SELF",
                "IN_IGNORED",
                "IN_MODIFY",
                "IN_MOVE_SELF",
                "IN_MOVED_FROM",
                "IN_MOVED_TO",
                "IN_Q_OVERFLOW",
                "IN_UNMOUNT",
                "default"]
    def my_init(self, calibPath, config):
        '''
        Simply tracks calib path and config dictionary
        '''
        self.calibPath = calibPath
        self.config = config
        print('Initialized with calib file path: ' + self.calibPath)
        print('Initialized with config file:')
        print(config)
        print('waiting ----------------------------------')
    
    def process_IN_CREATE(self, event):
        print('file created: {0}'.format(event.pathname))
        filename = os.path.basename(event.pathname)
        fileRoot, ext = os.path.splitext(filename)
        if ext == '.tif':
            print(filename + ' detected, processing')
            ########## Begin data reduction scripts ###########################
            SAXSDimReduce(self.calibPath, event.pathname, self.config) #QRange=QRange, ChiRange=ChiRange)

            peakFitBBA(event.pathname, self.config)
            ########## Visualization #########################################
            # Pulling info from master CSV
            FWHMmap(event.pathname)
            contrastMap(event.pathname, self.config['highlightLimit'])

            print(event.pathname + ' completed')
            print('====================================================== Waiting...')
            print('\n')
    
    def process_CLOSE_WRITE(self, event):
        print('file finished writing: {0}'.format(event.pathname))
            
    def process_IN_MOVED_TO(self, event):
        print('file moved: {0}'.format(event.pathname))
    
def mainWrapper():
    # grab monitor folder
    root = Tkinter.Tk()
    root.withdraw()
    
    calibPath = tkFileDialog.askopenfilename(title='Select Calibration File')
    #calibPath = os.path.expanduser('~/monHiTp/testHold/8Nov17_calib_1.calib')
    if calibPath is '':
        print('No calibration path selected, aborting...')
        return

    #configPath = tkFileDialog.askopenfilename(title='Select Config File')
    configPath = os.path.expanduser('~/monHiTp/config')
    if configPath is '':
        print('No config file supplied, aborting...')
        return
    config = parse_config(configPath)
    
    monFoldPath = tkFileDialog.askdirectory(title='Select folder to watch')
    #monFoldPath = os.path.expanduser('~/monHiTp/testMon')
    if monFoldPath is '':
        print('No monitor folder selected, aborting...')
        return

    print('monitoring: ' + monFoldPath + '===================================')
    print('==================================================================')

    # Initialize monitor
    watchManager = pyinotify.WatchManager()
    #eventNotifier = pyinotify.Notifier(watchManager) # Enable to monitor all
    eventNotifier = pyinotify.Notifier(watchManager, 
        EventProcessor(calibPath=calibPath, config=config)) 
        # Enable to use custom event processor

    watchManager.add_watch(monFoldPath, pyinotify.ALL_EVENTS)
    # Begin loop and handle events
    eventNotifier.loop()


###### Run script ############
mainWrapper()


# Processing steps:
# Prompt for calibration file
# monitor for new tif images
# on new image
#       -run dimension reduction (Fang HITP script)
#       -run peak finding/fitting script (BBA)
# orgainize everything into attribute files
