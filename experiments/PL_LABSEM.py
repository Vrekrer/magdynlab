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
def MyPlot(Data):
    f = plt.figure('PL Int vs wl', (5,4))
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim(*Data.xlim)
        ax.set_ylim(*Data.ylim)
    line = ax.lines[-1]
    line.set_data(Data.X, Data.Y)
    ax.set_xlabel('Wave Length (nm)')
    ax.set_ylabel('PL Int (V)')
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()
    
class PL(object):
    def __init__(self, 
                 com_port_monocromador = 3,
                 com_port_laser = None):
        logFile = os.path.expanduser('~/MagDynLab.log')
        MotorDriver = magdynlab.instruments.StepMotor_Renato(port = com_port_monocromador, 
                                                             logFile=logFile)
        LockIn = magdynlab.instruments.SRS_SR530(GPIB_Address=23,
                                                 logFile=logFile)

        if com_port_laser is not None:
            self.Laser = magdynlab.instruments.MatchBox2_Laser(port = com_port_laser,
                                                          logFile=logFile)

        self.MC = magdynlab.controllers.MonochromatorControler(MotorDriver)
        self.VC = magdynlab.controllers.LockIn_Controler(LockIn)

        #This is used to plot
        self.Data = magdynlab.data_types.Data2D()
        self.LockIn = self.VC.LockIn
        
    def _SaveData(self, file_name):
        self.Data.save(file_name)

    def PlotData(self, i = None):
        MyPlot(self.Data)

    def SetRef(self, MC_display_value):
        self.MC.setRefPosition(MC_display_value/5)
        
    @ThD.as_thread
    def Measure(self, crv = [], file_name = None,
                header = None,
                meas_opts = [5, 0.5, 0.1],
                stat_opts = [False, 0.05, 5],
                start_delay = 5):
        wave_lengths = numpy.asarray(crv)
        
        # Initialize data objects
        self.Data.reset(n = 3)
        self.Data.header = header
        self.Data.xlim = [wave_lengths.min(), wave_lengths.max()]
        sen = self.VC.LockIn.SEN * 1.5
        self.Data.ylim = [0, sen]
        
        n_pts, iniDelay, measDelay = meas_opts
        stat, tol, maxIts  = stat_opts

        self.MC.wave_length = wave_lengths[0]
        time.sleep(start_delay)
        
        # Loop for each field
        for i, wl in enumerate(wave_lengths):
            self.MC.wave_length = wl
            while True:
                amp, std = self.VC.getAmplitude(n = n_pts, 
                                                iniDelay = iniDelay, measDelay = measDelay,
                                                stat = stat, tol = tol/100.0, maxIts = maxIts
                                                )
                if amp > 0.95*self.VC.LockIn.SEN:
                    self.VC.LockIn.SEN = self.VC.LockIn.SEN * 3.0
                else:
                    break
            acutal_wl = self.MC.wave_length
            self.Data.addPoint(acutal_wl, amp, std)
            MyPlot(self.Data)
            ThD.check_stop()
            
        if file_name != None:
            self._SaveData(file_name)

    def Stop(self, TurnOff = True):
        print('Stoping...')
        self.Measure.stop()
        if self.Measure.thread is not None:
            self.Measure.thread.join()
        print('DONE')

    @property
    def wave_length(self):
        '''
        Sets or return the working wave length (in nm)
        '''
        return self.MC.wave_length

    @wave_length.setter
    def wave_length(self, wave_length_value):
        self.MC.setRefPosition(wave_length_value)
