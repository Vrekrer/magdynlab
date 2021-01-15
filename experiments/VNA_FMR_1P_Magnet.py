# -*- coding: utf-8 -*-

import numpy
import time
import os
import magdynlab.instruments as  instrs
import magdynlab.controllers as ctrls
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
    f = plt.figure('VNA-FMR', (5, 4))

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

class VNA_FMR_1P(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')
        
        defaultRN = dict(RN_Fonte = None,
                         RN_Voltmeter = 'GPIB0::17::INSTR',
                         RN_VNA = 'TCPIP::192.168.13.2::INSTR')
        defaultRN.update(ResouceNames)
        RN_Fonte = defaultRN['RN_Fonte']
        RN_VNA = defaultRN['RN_VNA']
        RN_Voltmeter = defaultRN['RN_Voltmeter']
        
        PowerSource = instrs.LakeShore_643(ResourceName=RN_Fonte,
                                           logFile=logFile)
        VNA = instrs.RS_VNA_Z(ResourceName=RN_VNA,
                              logFile=logFile)
#        Voltmeter = instrs.VrekrerVoltMeter(ResourceName=RN_Voltmeter,
#                                            logFile=logFile)
        Voltmeter = instrs.KEITHLEY_195(ResourceName=RN_Voltmeter,
                                        logFile=logFile)

        self.VNAC = ctrls.VNA_Controller(VNA)
        self.FC = ctrls.FieldController_LS643(PowerSource, Voltmeter)

        #Experimental/plot data
        self.Data = magdynlab.data_types.DataContainer()
        self.Data.file_id = '.VNA_1P_Raw' #S11 vs hs vs fs

        self.ColorMapData = magdynlab.data_types.DataContainer()
        self.ColorMapData.file_id = '.VNA_ColorMap' #PAbs vs hs vs fs

        self.Data_Osc = magdynlab.data_types.DataContainer()
        self.Data_Osc.file_id = '.VNA_Osc_1P_Raw'  #S11 vs h  vs hosc

        self.Data_dPdH = magdynlab.data_types.DataContainer()
        self.Data_dPdH.file_id = '.VNA_dPdH'  #dP/dH vs h (fixed freq)
        self.Info = ''

    def SetTraces(self):
        self.VNAC.set_traces_SParameters_1P()

    def PlotColorMap(self, i=None):
        Pabs_ref = 1 - numpy.abs(self.Data['S11_Ref'])**2

        if i is not None:
            # Update only i column
            Pabs = 1 - numpy.abs(self.Data['S11'][i])**2
            if self.Data['h'][0] > self.Data['h'][-1]:
                i = -1 - i
            self.ColorMapData['ColorMap'][i] = Pabs - Pabs_ref
        else:
            Pabs = 1 - numpy.abs(self.Data['S11'])**2
            self.ColorMapData['ColorMap'] = Pabs - Pabs_ref[None,:]
            if self.Data['h'][0] > self.Data['h'][-1]:
                self.ColorMapData['ColorMap'] = Pabs[::-1] - Pabs_ref[None,:]
        Plot_ColorMap(self.ColorMapData)

    def MeasureRef(self):
        self.Data['S11_Ref'] = self.VNAC.getSData(0, True)

    @ThD.as_thread
    def Measure(self, fields, file_name, hold_time=0.0):

        self.Data['h'] = fields
        self.Data['f'] = self.VNAC.frequencies
        data_shape = (len(self.Data['h']), len(self.Data['f']))
        self.Data['S11'] = numpy.zeros(data_shape, dtype=complex)
        self.Data.info = self.Info
        
        self.ColorMapData['h'] = self.Data['h'].copy()
        self.ColorMapData['f'] = self.Data['f']
        self.ColorMapData['ColorMap'] = numpy.zeros(data_shape, dtype=float)
        self.ColorMapData['ColorMap'] += numpy.nan
        self.ColorMapData.info = self.Info
        
        # Loop for each field
        for i, h in enumerate(fields):
            self.FC.setField(h)
            self.Data['h'][i] = self.FC.getField()
            time.sleep(hold_time)
            self.Data['S11'][i] = self.VNAC.getSData(0, True)
            self.PlotColorMap(i)
            ThD.check_stop()

        if file_name is not None:
            self.Data.save(file_name)
        self.FC.TurnOff()

    def PlotdPdH(self, i=None):
        ss = self.Data_Osc['AC Field'] / self.Data_Osc['oscH']**2
        Pabs = 1 - numpy.abs(self.Data_Osc['S11'])**2
        A_Pabs = (Pabs * ss[None,:]).mean(axis=1)
        
        if i is not None:
            self.Data_dPdH['dP/dH'][i] = A_Pabs[i]
        else:
            self.Data_dPdH['dP/dH'] = A_Pabs
        Plot_dPdH(self.Data_dPdH)


    @ThD.as_thread
    def Measure_dPdH(self, H_start, H_stop, H_steps, freq, file_name, 
                     oscH=20, osc_points_per_cicle=4, osc_repetitions=10,
                     hold_time=0.1, osc_hold_time=0.01, turn_off=False):

        self.VNAC.backup_sweep()
        self.VNAC.VNA.Ch1.SetSweep(start=freq, stop=freq, np=1)

        PowerSource2 = magdynlab.instruments.KEPCO_BOP(ResourceName='GPIB0::6::INSTR')
        FC = magdynlab.controllers.FieldController(PowerSource2)
        FC.Kepco.Voltage = 15

        self.FC.setField(H_stop)
        self.FC.setField(H_stop)
        I_end = self.FC.PowerSource.measured_current
        self.FC.setField(H_start)
        self.FC.setField(H_start)
        I_start = self.FC.PowerSource.measured_current

        Is_H_dc = numpy.linspace(I_start, I_end, H_steps)

        self.Data_Osc['h'] = numpy.linspace(H_start, H_stop, H_steps)
        self.Data_Osc['f'] = freq
        self.Data_Osc['osc_points_per_cicle'] = osc_points_per_cicle
        self.Data_Osc['osc_repetitions'] = osc_repetitions
        self.Data_Osc['oscH'] = oscH * 1E-3 #mA
        oscR = osc_repetitions
        oscN = osc_repetitions * osc_points_per_cicle
        ss = numpy.sin(numpy.linspace(0, 2*oscR*numpy.pi, oscN))
        self.Data_Osc['AC Field'] = ss * oscH * 1E-3
        data_shape = (len(self.Data_Osc['h']), oscN)
        self.Data_Osc['S11'] = numpy.zeros(data_shape, dtype=complex)
        self.Data_Osc.info = self.Info

        self.Data_dPdH['h'] = self.Data_Osc['h'].copy()
        self.Data_dPdH['f'] = freq
        self.Data_dPdH['dP/dH'] = numpy.zeros_like(Is_H_dc) + numpy.nan
        extra_info = ['',
                      'Frequency : %(f)0.6f GHz' % {'f':freq/1E9},
                      'Osc Field : %(oscH)0.1f Oe' % {'oscH':oscH}, 
                      'OscPoints : %(oscP)d' % {'oscP':osc_points_per_cicle},
                      'OscReps :%(oscR)d' % {'oscR':osc_repetitions},
                      '']
        self.Data_dPdH.info = self.Info + '\n'.join(extra_info)

        # Loop for each DC field
        for hi, I_H_dc in enumerate(Is_H_dc):
            self.FC.PowerSource.setpoint = I_H_dc
            self.FC.PowerSource.WaitRamp()
            time.sleep(hold_time)
            self.Data_Osc['h'][hi] = self.FC.getField()
            self.Data_dPdH['h'][hi] = self.Data_Osc['h'][hi]

            # Loop for each AC field
            for ci, I_H_ac in enumerate(self.Data_Osc['AC Field']): #currents
                PowerSource2.current = I_H_ac
                time.sleep(osc_hold_time)
                self.Data_Osc['S11'][hi,ci] = self.VNAC.getSData(0, True)
                ThD.check_stop()
            ThD.check_stop()
            self.PlotdPdH(hi)

        if file_name is not None:
            self.Data_Osc.save(file_name)
            self.Data_dPdH.savetxt(file_name + '.dPxH', keys=['h', 'dP/dH'])

        self.VNAC.restore_sweep()
        if turn_off:
            self.FC.TurnOff()
        FC.TurnOff()
        PowerSource2.BEEP()

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
