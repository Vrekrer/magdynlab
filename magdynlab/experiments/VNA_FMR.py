# -*- coding: utf-8 -*-

import numpy
import time
import magdynlab.instruments
import magdynlab.controlers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt

@ThD.gui_safe
def MyPlot(Data):
    f = plt.figure('VNA-FMR', (5,4))

    extent = numpy.array([Data.x.min(),
                          Data.x.max(),
                          Data.y.min()/1E9,
                          Data.y.max()/1E9])

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    ax.clear()
    ax.imshow(Data.dataArray,
               aspect = 'auto',
               origin = 'lower',
               extent = extent)
               
    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('Freq (GHz)')
    f.tight_layout()
    f.canvas.draw()


class VNA_FMR(object):
    def __init__(self, GPIB_Device = 0):
        PowerSource = magdynlab.instruments.KEPCO_BOP(GPIB_Device=0,
                                                      GPIB_Address=6)
        VNA = magdynlab.instruments.RS_VNA_Z(ResourceName='TCPIP::192.168.0.2::INSTR')

        self.FC = MagDynLab.Controlers.FieldControler_Driven(GPIB_Device = GPIB_Device)
        self.FC.Kepco.Voltage = 15

        # We store the raw S parameters in this Collection
        self.DataCollection = []
        for i in range(4):
            D = magdynlab.data_types.Data3D()
            self.DataCollection.append(D)

        # This is used to plot
        self.DataPlot = magdynlab.data_types.Data3D()
        
        self.traceNumbers = [0,1,2,3]

        self.SaveFormat = 'txt'
        self.Info = ''

    def _MeasureSpectra(self):
        Ss = []
        S = self.VNAC.getSData(self.traceNumbers[0], True)
        Ss.append(S)
        for tr in self.traceNumbers[1:]:
            S = self.VNAC.getSData(tr, False)
            Ss.append(S)
        return Ss
        
    def _SaveData(self, file_name):
        if self.SaveFormat == 'txt':
            self.keys = ['.11', '.22','.12','.21']
            for i, D in enumerate(self.DataCollection):
                D.saveZ(file_name, extR = self.keys[i] + '.Sr', 
                                   extI = self.keys[i] + '.Si')
            D = self.DataCollection[0]
            D.savex(file_name, ext = '.h')
            D.savey(file_name, ext = '.f')
        else:
            numpy.savez_compressed(file_name + '.VNA_Raw', 
                                   S11 = numpy.nan_to_num(self.DataCollection[0].dataArray),
                                   S22 = numpy.nan_to_num(self.DataCollection[1].dataArray),
                                   S12 = numpy.nan_to_num(self.DataCollection[2].dataArray),
                                   S21 = numpy.nan_to_num(self.DataCollection[3].dataArray),
                                   Ref = self.Refs,
                                   h = self.DataCollection[0].x, 
                                   f = self.DataCollection[0].y,
                                   Info = self.Info)

    def SaveRef(self, file_name):
        self.Refs = numpy.array( self._MeasureSpectra() )
        if self.SaveFormat == 'txt':
            numpy.savetxt(file_name + '.RefR', self.Refs.real)
            numpy.savetxt(file_name + '.RefI', self.Refs.imag)
            numpy.savetxt(file_name + '.f', self.VNAC.Frequencies)
        else:
            numpy.savez_compressed(file_name + '.VNA_Ref', 
                                   Ref = self.Refs,
                                   f = self.VNAC.Frequencies,
                                   Info = self.Info)

    def PlotData(self, i = None):
        RefS11 = self.Refs[0]
        if not self.onePort:
            RefS12 = self.Refs[2]
        else:
            RefS12 = 0

        Pr = 1 - numpy.abs(RefS11)**2 - numpy.abs(RefS12)**2
        
        #Update only last column
        if i != None:
            LastS11 = self.DataCollection[0].dataArray[:,i]
            LastS12 = self.DataCollection[2].dataArray[:,i]
            
            Pm = 1 - numpy.abs(LastS11)**2 - numpy.abs(LastS12)**2
            self.DataPlot.addColumn(Pm-Pr)
        else:
            S11 = self.DataCollection[0].dataArray
            S12 = self.DataCollection[2].dataArray
            
            Pm = 1 - numpy.abs(S11)**2 - numpy.abs(S12)**2
            self.DataPlot.dataArray = Pm-Pr[:,None]
        MyPlot(self.DataPlot)
        
    @ThD.as_thread
    def Measure(self, crv, file_name):      
        fields = crv
        freqs = self.VNAC.Frequencies
        
        #Initialize data objects
        for D in self.DataCollection:
            D.initialize(fields, freqs)
        self.DataPlot.initialize(fields, freqs)
        
        #Loop for each field
        for i, h in enumerate(fields):
            
            self.FC.setField(h, Tol = 0.25, FldStep = 0.5)
            #time.sleep(0.5)
            Ss = self._MeasureSpectra()
            for j, S in enumerate(Ss):
                self.DataCollection[j].addColumn(S)
            self.PlotData(i)
            ThD.check_stop()
            
        if file_name != None:
            self._SaveData(file_name)
        self.FC.TurnOff()
        self.FC.Kepco.BEEP()

    def Stop(self, TurnOff = True):
        self.FC.BEEP()
        self.Measure.stop()
        if self.Measure.thread is not None:
            self.Measure.thread.join()
        time.sleep(1)
        self.FC.BEEP()
        time.sleep(0.1)
        self.FC.BEEP()
        if TurnOff:
            self.FC.setField(0)

        


        
        
        
        
