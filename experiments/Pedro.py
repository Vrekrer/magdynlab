# -*- coding: utf-8 -*-

import numpy
import time
import os
import magdynlab.instruments
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt


@ThD.gui_safe
def MyPlot(Data):
    f = plt.figure('ZxBias', (5,4))
    
    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    #ax.clear()
    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.plot([],[],'r.-')
        ax.set_xlim(*Data.xlim)
        ax.set_ylim(*Data.ylim)
    line_r = ax.lines[-1]
    line_i = ax.lines[-2]
    line_r.set_data(Data.X, Data.dat[:,1])
    line_i.set_data(Data.X, Data.dat[:,2])
    ax.set_xlabel('Bias (V)')
    ax.set_ylabel('Z (Ohm)')
    ax.grid(True)

    f.tight_layout()
    f.canvas.draw()

class Impedance(object):
    def __init__(self, GPIB_Device=0):
        logFile = os.path.expanduser('~/MagDynLab.log')
        self.IA = magdynlab.instruments.KEYSIGHT_E4990A(ResourceName='TCPIP::192.168.13.3::E4990A::INSTR', logFile=logFile)


        self.Data = magdynlab.data_types.Data2D()
        self.Info = ''


    @ThD.as_thread
    def Measure(self, crv = [], file_name = None):
        bias = numpy.asarray(crv)
        
        # Initialize data objects
        self.Data.reset(n=3)
        self.Data.xlim = [bias.min(), bias.max()]
        self.Data.ylim = [-1E6, 1E6]
        
        # 
        for i, v in enumerate(bias):
            self.IA.Ch1.bias_voltage = v
            z = self.IA.Ch1.traces[0].getRDAT(New=True)
            self.Data.addPoint(v, z.real.mean(), z.imag.mean())
            MyPlot(self.Data)
            ThD.check_stop()
            
        if file_name != None:
            self.Data.save(file_name)
