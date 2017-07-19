# -*- coding: utf-8 -*-

#MxZ_PUC

import numpy
import time
import magdynlab.instruments
import magdynlab.controlers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt

@ThD.gui_safe
def MyPlot(Data):
    f = plt.figure('ZxH', (5,4))
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    scale_factor = 10**-round(numpy.log10(numpy.abs(Data.ylim).max()))
    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.plot([],[],'r.-')
        ax.set_xlim(*Data.xlim)
        ax.set_ylim(*(numpy.array(Data.ylim)*scale_factor))
    line = ax.lines[-1]
    line.set_data(Data.dat[:,0], (Data.dat[:,1]-Data.dat[0,1])*scale_factor)
    line = ax.lines[-2]
    line.set_data(Data.dat[:,0], (Data.dat[:,2]-Data.dat[0,2])*scale_factor)
    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('DV x 10^-%d' % numpy.log10(scale_factor))
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()
    
@ThD.gui_safe
def MyPlotFreq(Data):
    f = plt.figure('Zxf', (5,4))
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    scale_factor = 10**-round(numpy.log10(numpy.abs(Data.ylim).max()))
    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.plot([],[],'r.-')
        ax.set_xlim(*Data.xlim)
        ax.set_ylim(*(numpy.array(Data.ylim)*scale_factor))
    line = ax.lines[-1]
    line.set_data(Data.dat[:,3]/1E3, Data.dat[:,1]*scale_factor)
    line = ax.lines[-2]
    line.set_data(Data.dat[:,3]/1E3, Data.dat[:,2]*scale_factor)
    ax.set_xlabel('Freq (kHz)')
    ax.set_ylabel('V x 10^-%d' % numpy.log10(scale_factor))
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()

class ZxH(object):
    def __init__(self):
        PowerSource = magdynlab.instruments.E3648A()
        LockIn = magdynlab.instruments.SRS_SR844()
        
        self.FC = magdynlab.controlers.FieldControlerPUC(PowerSource)
        self.VC = magdynlab.controlers.ZControler_PUC(LockIn)

        self.Data = magdynlab.data_types.Data2D()
        self.Data.reset(n=4)
        
    def _SaveData(self, file_name):
        self.Data.save(file_name)

    def PlotData(self, i = None):
        MyPlot(self.Data)
        
    @ThD.as_thread
    def FieldSweep(self, crv = [], file_name = None, freq = 'Auto',
                   meas_opts = [1, 0.5, 0.1], TC = 'Auto'):
        
        fields = numpy.asarray(crv)
        
        #Initialize data objects
        self.Data.reset(n=4)
        self.Data.xlim = [fields.min(), fields.max()]
        sen = self.VC.LockIn.SEN * 1.5
        self.Data.ylim = [-sen/100, sen/100]
        
        if TC != 'Auto':
            self.VC.LockIn.TC = TC
            
        if freq != 'Auto':
            self.VC.setFreq(freq)
        
        n_pts, iniDelay, measDelay = meas_opts
        
        #Loop for each field
        for i, h in enumerate(fields):
            self.FC.setField(h)
            #time.sleep(0.5)
            f, X, Y = self.VC.getFXY(n = n_pts, iniDelay = iniDelay, measDelay = measDelay)
            self.Data.addPoint(h, X, Y, f)
            MyPlot(self.Data)
            ThD.check_stop()
            
        if file_name != None:
            self._SaveData(file_name)
        self.FC.TurnOff()
        self.FC.BEEP()

    @ThD.as_thread
    def FreqSweep(self, crvf = [], file_name = None, field = 'Auto',
                  turnFieldOff = True,
                  meas_opts = [1, 0.5, 0.1], TC = 'Auto'):
        
        freqs = numpy.asarray(crvf)
        
        #Initialize data objects
        self.Data.reset(n=4)
        self.Data.xlim = [freqs.min()/1E3, freqs.max()/1E3]
        sen = self.VC.LockIn.SEN * 1.5
        self.Data.ylim = [-sen, sen]
        
        if TC != 'Auto':
            self.VC.LockIn.TC = TC
            
        if field != 'Auto':
            self.FC.setField(field)
        h = self.FC.getField()
        
        n_pts, iniDelay, measDelay = meas_opts
        
        #Loop for each freq
        for i, f in enumerate(freqs):
            self.VC.setFreq(f)
            #time.sleep(0.5)
            f, X, Y = self.VC.getFXY(n = n_pts, iniDelay = iniDelay, measDelay = measDelay)
            self.Data.addPoint(h, X, Y, f)
            MyPlotFreq(self.Data)
            ThD.check_stop()
            
        if file_name != None:
            self._SaveData(file_name)
        if turnFieldOff:
            self.FC.TurnOff()
        self.FC.BEEP()        
        
    def Stop(self, TurnOff = True):
        print('Stoping...')
        self.FC.BEEP()
        self.FieldSweep.Stop()
        self.FreqSweep.Stop()
        if self.FieldSweep.thread is not None:
            self.FieldSweep.thread.join()
        if self.FreqSweep.thread is not None:
            self.FreqSweep.thread.join()
        print('DONE')
        time.sleep(1)
        self.FC.BEEP()
        time.sleep(0.1)
        self.FC.BEEP()
        if TurnOff:
            print('Turning field OFF')
            self.FC.setField(0)
            print('DONE')
