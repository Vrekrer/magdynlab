# -*- coding: utf-8 -*-

import numpy
import time
import os
import magdynlab.instruments as instruments
import magdynlab.controllers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt

def Plot_ColorMap(Data):
    f = plt.figure('ZxH', (5, 4))

    extent = numpy.array([Data['h'].min(),
                          Data['h'].max(),
                          Data['f'].min()/1E6,
                          Data['f'].max()/1E6])

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    ax.clear()
    ax.imshow(Data['ColorMap'].T,
              aspect='auto',
              origin='lower',
              extent=extent)

    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('Freq (MHz)')
    f.tight_layout()
    f.canvas.draw()

class ZxH(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')
        
        defaultRN = dict(RN_Analizer = 'GPIB0::17::INSTR',
                         RN_SourceMeter = 'GPIB0::28::INSTR')
        defaultRN.update(ResouceNames)
        RN_Analizer = defaultRN['RN_Analizer']
        RN_SourceMeter = defaultRN['RN_SourceMeter']
        
        SourceMeter = instruments.KEITHLEY_2400(ResourceName=RN_SourceMeter,
                                                logFile=logFile)
        self.Analizer = instruments.HP_4395A(ResourceName=RN_Analizer,
                                             logFile=logFile)

        self.FC = magdynlab.controllers.FieldController_SM(SourceMeter)

        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.ZxH_Raw' #Z vs hs vs fs

        self.ColorMapData = magdynlab.data_types.DataContainer()
        self.ColorMapData.file_id = '.ZxH_ColorMap' #|Z| vs hs vs fs

        self.SaveFormat = 'npy'
        self.Info = ''
        self.PlotFunct = numpy.abs

    def PlotColorMap(self, i=None):
        Z_ref = self.PlotFunct(self.Data['Ref'])
        if i is not None:
            # Update up to i column
            for j in range(i+1):
                Z = self.PlotFunct(self.Data['Z'][j])
                if self.Data['h'][0] > self.Data['h'][-1]:
                    j = -1 - j
                self.ColorMapData['ColorMap'][j] = Z - Z_ref
        else:
            Z = self.PlotFunct(self.Data['Z'])
            self.ColorMapData['ColorMap'] = Z - Z_ref[None,:]
            if self.Data['h'][0] > self.Data['h'][-1]:
                self.ColorMapData['ColorMap'] = Z[::-1]
        Plot_ColorMap(self.ColorMapData)

    def MeasureRef(self):
        self.Data['Ref'] = self.Analizer.get_Z(True)

    @ThD.as_thread
    def Measure(self, fields, file_name, hold_time=0.0):

        self.Data['h'] = fields
        self.Data['f'] = self.Analizer.get_sweep_parameter()
        data_shape = (len(self.Data['h']), len(self.Data['f']))
        self.Data['Z'] = numpy.zeros(data_shape, dtype=complex)
        self.Data.info = self.Info
        
        self.ColorMapData['h'] = self.Data['h']
        self.ColorMapData['f'] = self.Data['f']
        self.ColorMapData['ColorMap'] = numpy.zeros(data_shape, dtype=float)
        self.ColorMapData['ColorMap'] += numpy.nan
        self.ColorMapData.info = self.Info
        
        # Loop for each field
        for i, h in enumerate(fields):
            self.FC.setField(h)
            time.sleep(hold_time)
            self.Data['Z'][i] = self.Analizer.get_Z(True)
            self.PlotColorMap(i)
            ThD.check_stop()

        if file_name is not None:
            self.Data.save(file_name)
        self.FC.TurnOff()
        self.FC.BEEP()

    def Stop(self, TurnOff=True):
        print('Stoping...')
        self.FC.BEEP()
        self.Measure.stop()
        if self.Measure.thread is not None:
            self.Measure.thread.join()
        time.sleep(1)
        self.FC.BEEP()
        time.sleep(0.1)
        self.FC.BEEP()
        print('DONE')
        if TurnOff:
            print('Turning field OFF')
            self.FC.TurnOff()
            print('DONE')
