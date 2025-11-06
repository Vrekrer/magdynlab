# -*- coding: utf-8 -*-

#MxH_Helmholtz_AGFM

import numpy
import time
import magdynlab.instruments
import magdynlab.controllers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt
import os

@ThD.gui_safe
def Plot_dpdh_vs_H(Data):
    f = plt.figure('dpdh_vs_H', (5,4))
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim(*Data.xlim)
        ax.set_ylim(*Data.ylim)
    line = ax.lines[-1]
    line.set_data(Data['h'], Data['dpdh'])
    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('Amp (V)')
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()
    
@ThD.gui_safe
def Plot_dpdh_vs_f(Data):
    f = plt.figure('dpdh_vs_f', (5,4))
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim(*Data.xlim)
        ax.set_ylim(*Data.ylim)
    line = ax.lines[-1]
    line.set_data(Data['f']/1E9, Data['dpdh'])
    ax.set_xlabel('freq (GHz)')
    ax.set_ylabel('Amp (V)')
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()

class FMR_LockIn(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')
        
        defaultRN = dict(RN_Kepco = 'GPIB0::6::INSTR',
                         RN_LockIn = 'GPIB0::8::INSTR',
                         RN_SignalGen = 'TCPIP::192.168.13.4::INSTR')
        defaultRN.update(ResouceNames)
        RN_Kepco = defaultRN['RN_Kepco']
        RN_LockIn = defaultRN['RN_LockIn']
        RN_SignalGen = defaultRN['RN_SignalGen']
        
        PowerSource = magdynlab.instruments.KEPCO_BOP(ResourceName=RN_Kepco,
                                                      logFile=logFile)
        LockIn = magdynlab.instruments.SRS_SR830(ResourceName=RN_LockIn,
                                                 logFile=logFile)
        SignalGen = magdynlab.instruments.RS_SMF(ResourceName=RN_SignalGen,
                                                 logFile=logFile)

        self.FC = magdynlab.controllers.FieldController(PowerSource)
        self.VC = magdynlab.controllers.LockIn_Mag_Controller(LockIn)
        self.SG = SignalGen

        #This is used to plot
        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()

    @ThD.as_thread
    def Measure_vs_H(self, fields, file_name=None, meas_opts=[1, 0.05, 0.05]):
        fields = numpy.asarray(fields)
        
        #Initialize data objects
        self.Data['h'] = fields
        self.Data['dpdh'] = numpy.zeros_like(fields) + numpy.nan
        self.Data['error_dpdh'] = numpy.zeros_like(fields) + numpy.nan
        self.Data.xlim = [fields.min(), fields.max()]
        sen = self.VC.LockIn.SEN * 1.5
        self.Data.ylim = [-sen, sen]
        self.Data.file_id = '.dpdhxh' #dpdh vs h
        
        n_pts, iniDelay, measDelay = meas_opts
        
        self.SG.output = 'ON'
        # Loop for each field
        for i, h in enumerate(fields):
            self.FC.setField(h)
            A, eA = self.VC.getMagnetization(n=n_pts, 
                                             iniDelay=iniDelay, 
                                             measDelay=measDelay)
            self.Data['dpdh'][i] = A
            self.Data['error_dpdh'][i] = eA
            Plot_dpdh_vs_H(self.Data)
            ThD.check_stop()
            
        if file_name != None:
            self.Data.savetxt(file_name, keys=['h', 'dpdh', 'error_dpdh'])
        self.SG.output = 'OFF'
        self.FC.TurnOff()
        self.FC.Kepco.BEEP()
        
    @ThD.as_thread
    def Measure_vs_F(self, freqs, file_name=None, meas_opts=[1, 0.05, 0.05]):
        freqs = numpy.asarray(freqs)
        
        #Initialize data objects
        self.Data['f'] = freqs
        self.Data['dpdh'] = numpy.zeros_like(freqs) + numpy.nan
        self.Data['error_dpdh'] = numpy.zeros_like(freqs) + numpy.nan
        self.Data.xlim = [freqs.min()/1E9, freqs.max()/1E9]
        sen = self.VC.LockIn.SEN * 1.5
        self.Data.ylim = [-sen, sen]
        self.Data.file_id = '.dpdhxf' #dpdh vs f
        
        n_pts, iniDelay, measDelay = meas_opts
        
        self.SG.output = 'ON'
        # Loop for each field
        for i, f in enumerate(freqs):
            self.SG.frequency = f
            A, eA = self.VC.getMagnetization(n=n_pts, 
                                             iniDelay=iniDelay, 
                                             measDelay=measDelay)
            self.Data['dpdh'][i] = A
            self.Data['error_dpdh'][i] = eA
            Plot_dpdh_vs_f(self.Data)
            ThD.check_stop()
            
        if file_name != None:
            self.Data.savetxt(file_name, keys=['f', 'dpdh', 'error_dpdh'])
        self.SG.output = 'OFF'
        self.FC.TurnOff()
        self.FC.Kepco.BEEP()

    def Stop(self, TurnOff = True):
        print('Stoping...')
        self.FC.BEEP()
        self.Measure.stop()
        self.FreqCurve.stop()
        if self.Measure.thread is not None:
            self.Measure.thread.join()
        if self.FreqCurve.thread is not None:
            self.FreqCurve.thread.join()
        print('DONE')
        time.sleep(1)
        self.FC.BEEP()
        time.sleep(0.1)
        self.FC.BEEP()
        if TurnOff:
            print('Turning field OFF')
            self.FC.setField(0)
            print('DONE')

