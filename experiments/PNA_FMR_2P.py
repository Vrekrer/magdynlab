# -*- coding: utf-8 -*-

import numpy
import time
import os
import magdynlab.instruments
import magdynlab.controllers
import magdynlab.data_types
import threading_decorators as ThD
import matplotlib.pyplot as plt


@ThD.gui_safe
def Plot_dPdH(Data):
    f = plt.figure('VNA-FMR dP/dH', (5, 4))

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]

    if not(ax.lines):
        ax.plot([],[],'b.-')
        ax.set_xlim([Data['h'].min(), Data['h'].max()])
        ax.set_ylim([-1E-10, 1E-10])
        
    line = ax.lines[-1]
    line.set_data(Data['h'], Data['dP/dH']*1000)
    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('dP/dH')
    ax.grid(True)

    #check Y scale
    ymax = numpy.nan_to_num(Data['dP/dH']).max()*1000
    ymin = numpy.nan_to_num(Data['dP/dH']).min()*1000
    dy  = ymax - ymin
    yc = (ymax + ymin)/2
    ymin, ymax = ax.get_ylim()
    ymax = numpy.max([yc + dy*1.1/2, ymax])
    ymin = numpy.min([yc - dy*1.1/2, ymin])
    ax.set_ylim([ymin, ymax])

    f.tight_layout()
    f.canvas.draw()

@ThD.gui_safe
def Plot_ColorMap(Data):
    f = plt.figure('PNA-FMR', (5, 4))

    extent = numpy.array([Data['h'].min(),
                          Data['h'].max(),
                          Data['f'].min()/1E9,
                          Data['f'].max()/1E9])

    if not(f.axes):
        plt.subplot()
    ax = f.axes[0]
    ax.clear()
    ax.imshow(Data['ColorMap'].T,
              aspect='auto',
              origin='lower',
              extent=extent)

    ax.set_xlabel('Field (Oe)')
    ax.set_ylabel('Freq (GHz)')
    f.tight_layout()
    f.canvas.draw()

class VNA_FMR_2P(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')
        
        defaultRN = dict(RN_Kepco = 'GPIB0::6::INSTR',
                         RN_PNA = 'TCPIP::192.168.13.10::INSTR')
        defaultRN.update(ResouceNames)
        RN_Kepco = defaultRN['RN_Kepco']
        RN_PNA = defaultRN['RN_PNA']

        PowerSource = magdynlab.instruments.KEPCO_BOP(ResourceName=RN_Kepco,
                                                      logFile=logFile)
        VNA = magdynlab.instruments.KEYSIGHT_PNA(ResourceName=RN_PNA,
                                                 logFile=logFile)

        self.VNAC = magdynlab.controllers.VNA_Controller(VNA)
        self.FC = magdynlab.controllers.FieldController(PowerSource)
        self.FC.Kepco.Voltage = 15

        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.VNA_2P_Raw' #S11 vs hs vs fs

        self.ColorMapData = magdynlab.data_types.DataContainer()
        self.ColorMapData.file_id = '.VNA_ColorMap' #PAbs vs hs vs fs

        self.Data_Osc = magdynlab.data_types.DataContainer()
        self.Data_Osc.file_id = '.VNA_Osc_2P_Raw'  #S11 vs h  vs hosc

        self.Data_dPdH = magdynlab.data_types.DataContainer()
        self.Data_dPdH.file_id = '.VNA_dPdH'  #dP/dH vs h (fixed freq)
        self.Info = ''

    def SetTraces(self):
        self.VNAC.set_traces_SParameters_2P()

    def PlotColorMap(self, i=None):
        Pabs_ref = 1 \
                   - numpy.abs(self.Data['S11_Ref'])**2 \
                   - numpy.abs(self.Data['S21_Ref'])**2

        if i is not None:
            # Update only i column
            Pabs = 1 \
                   - numpy.abs(self.Data['S11'][i])**2 \
                   - numpy.abs(self.Data['S21'][i])**2
            if self.Data['h'][0] > self.Data['h'][-1]:
                i = -1 - i
            self.ColorMapData['ColorMap'][i] = Pabs - Pabs_ref
        else:
            Pabs = 1 \
                   - numpy.abs(self.Data['S11'])**2 \
                   - numpy.abs(self.Data['S21'])**2
            self.ColorMapData['ColorMap'] = Pabs - Pabs_ref[None,:]
            if self.Data['h'][0] > self.Data['h'][-1]:
                self.ColorMapData['ColorMap'] = Pabs[::-1] - Pabs_ref[None,:]
        Plot_ColorMap(self.ColorMapData)

    def MeasureRef(self):
        self.Data['S11_Ref'] = self.VNAC.getSData(0, True)
        self.Data['S21_Ref'] = self.VNAC.getSData(1, False)
        self.Data['S22_Ref'] = self.VNAC.getSData(2, False)
        self.Data['S12_Ref'] = self.VNAC.getSData(3, False)

    @ThD.as_thread
    def Measure(self, fields, file_name, hold_time=0.0):

        self.Data['h'] = fields
        self.Data['f'] = self.VNAC.frequencies
        data_shape = (len(self.Data['h']), len(self.Data['f']))
        self.Data['S11'] = numpy.zeros(data_shape, dtype=complex)
        self.Data['S21'] = numpy.zeros(data_shape, dtype=complex)
        self.Data['S22'] = numpy.zeros(data_shape, dtype=complex)
        self.Data['S12'] = numpy.zeros(data_shape, dtype=complex)
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
            self.Data['S11'][i] = self.VNAC.getSData(0, True)
            self.Data['S21'][i] = self.VNAC.getSData(1, False)
            self.Data['S22'][i] = self.VNAC.getSData(2, False)
            self.Data['S12'][i] = self.VNAC.getSData(3, False)
            self.PlotColorMap(i)
            ThD.check_stop()

        if file_name is not None:
            self.Data.save(file_name)
        self.FC.TurnOff()
        self.FC.Kepco.BEEP()

    def PlotdPdH(self, i=None):
        ss = self.Data_Osc['AC Field'] / self.Data_Osc['oscH']**2
        Pabs = 1 \
               - numpy.abs(self.Data_Osc['S11'])**2 \
               - numpy.abs(self.Data_Osc['S21'])**2
        A_Pabs = (Pabs * ss[None,:]).mean(axis=1)
        
        if i is not None:
            self.Data_dPdH['dP/dH'][i] = A_Pabs[i]
        else:
            self.Data_dPdH['dP/dH'] = A_Pabs
        Plot_dPdH(self.Data_dPdH)

    @ThD.as_thread
    def Measure_dPdH(self, fields, freq, file_name, 
                     oscH=5, osc_points_per_cicle=4, osc_repetitions=10,
                     hold_time=0.0, osc_hold_time=0.01, mode='Fast'):

        self.VNAC.backup_sweep()
        self.VNAC.VNA.Ch1.SetSweep(start=freq, stop=freq, np=1)

        self.Data_Osc['h'] = fields
        self.Data_Osc['f'] = freq
        self.Data_Osc['osc_points_per_cicle'] = osc_points_per_cicle
        self.Data_Osc['osc_repetitions'] = osc_repetitions
        self.Data_Osc['oscH'] = oscH
        oscR = osc_repetitions
        oscN = osc_repetitions * osc_points_per_cicle
        ss = numpy.sin(numpy.linspace(0, 2*oscR*numpy.pi, oscN))
        self.Data_Osc['AC Field'] = ss * oscH
        data_shape = (len(self.Data_Osc['h']), oscN)
        self.Data_Osc['S11'] = numpy.zeros(data_shape, dtype=complex)
        self.Data_Osc['S21'] = numpy.zeros(data_shape, dtype=complex)
        if mode == 'Full':
            self.Data_Osc['S22'] = numpy.zeros(data_shape, dtype=complex)
            self.Data_Osc['S12'] = numpy.zeros(data_shape, dtype=complex)
        self.Data_Osc.info = self.Info

        self.Data_dPdH['h'] = fields
        self.Data_dPdH['f'] = freq
        self.Data_dPdH['dP/dH'] = numpy.zeros_like(fields) + numpy.nan
        extra_info = ['',
                      'Frequency : %(f)0.6f GHz' % {'f':freq/1E9},
                      'Osc Field : %(oscH)0.1f Oe' % {'oscH':oscH}, 
                      'OscPoints : %(oscP)d' % {'oscP':osc_points_per_cicle},
                      'OscReps :%(oscR)d' % {'oscR':osc_repetitions},
                      '']
        self.Data_dPdH.info = self.Info + '\n'.join(extra_info)

        # Loop for each DC field
        for hi, h in enumerate(fields):
            self.FC.setField(h)
            time.sleep(hold_time)

            i0 = self.FC.Kepco.current
            cs = i0 + self.Data_Osc['AC Field']/self.FC.HperOut

            # Loop for each AC field
            for ci, c in enumerate(cs):
                self.FC.Kepco.current = c
                time.sleep(osc_hold_time)
                self.Data_Osc['S11'][hi,ci] = self.VNAC.getSData(0, True)
                self.Data_Osc['S21'][hi,ci] = self.VNAC.getSData(1, False)
                if mode == 'Full':
                    self.Data_Osc['S22'][hi,ci] = self.VNAC.getSData(2, False)
                    self.Data_Osc['S12'][hi,ci] = self.VNAC.getSData(3, False)
                ThD.check_stop()
            ThD.check_stop()
            self.PlotdPdH(hi)

        if file_name is not None:
            self.Data_Osc.save(file_name)
            self.Data_dPdH.savetxt(file_name + '.dPxH', keys=['h', 'dP/dH'])

        self.VNAC.restore_sweep()
        self.FC.TurnOff()
        self.FC.Kepco.BEEP()

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


def field_span(center, span, n_pts, hmin=0, hmax=20000):
    crv = numpy.linspace(center-span/2, center+span/2, n_pts)
    mask = (crv >= hmin) * (crv <= hmax)
    return crv[mask]
