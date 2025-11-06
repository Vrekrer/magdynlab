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
        if 'Fixed frequency' in Data['Mode']:
            ax.set_xlim([Data['h'].min(), Data['h'].max()])
        else:
            ax.set_xlim([Data['f'].min()/1E9, Data['f'].max()/1E9])
        ax.set_ylim([-1E-10, 1E-10])
        
    line = ax.lines[-1]
    if 'Fixed frequency' in Data['Mode']:
        line.set_data(Data['h'], Data['dP/dH']*1000)
        ax.set_xlabel('Field (Oe)')
    else:
        line.set_data(Data['f']/1E9, Data['dP/dH']*1000)
        ax.set_xlabel('Freq (GHz)')
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

class PNA_FMR_1P(object):
    def __init__(self, ResouceNames={}):
        logFile = os.path.expanduser('~/MagDynLab.log')
        
        defaultRN = dict(RN_Fonte = None,
                         RN_Voltmeter = 'GPIB0::17::INSTR',
                         RN_PNA = 'TCPIP::192.168.13.10::INSTR')
        defaultRN.update(ResouceNames)
        RN_Fonte = defaultRN['RN_Fonte']
        RN_PNA = defaultRN['RN_PNA']
        RN_Voltmeter = defaultRN['RN_Voltmeter']
        
        PowerSource = instrs.LakeShore_643(ResourceName=RN_Fonte,
                                           logFile=logFile)
        Voltmeter = instrs.KEITHLEY_195(ResourceName=RN_Voltmeter,
                                        logFile=logFile)
        VNA = instrs.KEYSIGHT_PNA(ResourceName=RN_PNA,
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

    @ThD.as_thread
    def Measure_dPdH(self, fields, freq, file_name, 
                     dH=5,  average_factor=10, hold_time=0.05):

        Data = self.Data_dPdH
        Data['Mode'] = 'Fixed frequency'

        self.VNAC.backup_sweep()
        self.VNAC.VNA.Ch1.SetSweep(start=freq, stop=freq, np=1)

        Data['h'] = fields
        Data['f'] = freq
        Data['dH'] = numpy.zeros_like(fields) + numpy.nan
        data_shape = (len(Data['h']), 2, average_factor)
        Data['S11'] = numpy.zeros(data_shape, dtype=complex) + numpy.nan
        Data['dP/dH'] = numpy.zeros_like(fields) + numpy.nan
        extra_info = ['',
                      'Mode : Fixed frequency',
                      'Frequency : %(f)0.6f GHz' % {'f':freq/1E9},
                      'Average factor : %(av)d' % {'av':average_factor}, 
                      '']
        Data.info = self.Info + '\n'.join(extra_info)
        print('*** Measuring dP/dH fixed frequency***')
        print('\n'.join(extra_info))
        
        #make smoot field transitions
        self.FC.setField(fields[-1])
        self.FC.setField(fields[-1])
        I_end = self.FC.PowerSource.measured_current
        self.FC.setField(fields[0])
        self.FC.setField(fields[0])
        I_start = self.FC.PowerSource.measured_current

        Is_H_dc = numpy.linspace(I_start, I_end, len(fields))

        # Loop for each DC field
        for hi, I_H_dc in enumerate(Is_H_dc):
            self.FC.PowerSource.setpoint = I_H_dc - dH*1E-3
            self.FC.PowerSource.WaitRamp()
            time.sleep(hold_time)
            Hn = self.FC.getField()

            for av_i in range(average_factor):
                Data['S11'][hi,1,av_i] = self.VNAC.getSData(0, True)

            self.FC.PowerSource.setpoint = I_H_dc + dH*1E-3
            self.FC.PowerSource.WaitRamp()
            time.sleep(hold_time)
            Hp = self.FC.getField()            
            
            for av_i in range(average_factor):
                Data['S11'][hi,0,av_i] = self.VNAC.getSData(0, True)
            ThD.check_stop()
            
            PAbs_hi = 1 - numpy.abs(Data['S11'][hi])**2
            P_pos = numpy.nanmean(PAbs_hi[0,:])
            P_neg = numpy.nanmean(PAbs_hi[1,:])
            Data['dP/dH'][hi] = (P_pos - P_neg)/(Hp-Hn)
            Data['dH'][hi] = Hp-Hn
            Data['h'][hi] = (Hp+Hn)/2
            Plot_dPdH(Data)
                
            ThD.check_stop()
        self.VNAC.restore_sweep()
        print('Done!')
        
        if file_name is not None:
            Data.save(file_name)
            Data.savetxt(file_name + '.dPxH', keys=['h', 'dP/dH'])



    @ThD.as_thread
    def Measure_dPdH_freq(self, field, file_name, 
                          dH=2, average_factor=20,
                          hold_time = 0.2):

        Data = self.Data_dPdH
        Data['Mode'] = 'Fixed field '
        Data['f'] = self.VNAC.frequencies
        data_shape = (len(Data['f']), 2, average_factor)
        Data['S11'] = numpy.zeros(data_shape, dtype=complex) + numpy.nan
        Data['dP/dH'] = numpy.zeros_like(Data['f']) + numpy.nan

        extra_info = ['',
                      'Mode : Fixed field',
                      'Field : ~ %0.2f Oe' % field,
                      'Freq : %0.2f - %0.2f GHz'  % (Data['f'].min()/1E9, Data['f'].max()/1E9),
                      'dH : %s' % dH,
                      'Average factor : %d' % average_factor,
                      '']

        print('*** Measuring dP/dH fixed field***')
        print('\n'.join(extra_info))

        self.FC.setField(field)
        self.FC.setField(field)
        I_H_dc = self.FC.PowerSource.measured_current

        self.FC.PowerSource.setpoint = I_H_dc + dH*1E-3
        self.FC.PowerSource.WaitRamp()
        time.sleep(hold_time)
        Hp = self.FC.getField()
        
        for av_i in range(average_factor):
            Data['S11'][:,0,av_i] = self.VNAC.getSData(0, True)

        self.FC.PowerSource.setpoint = I_H_dc - dH*1E-3
        self.FC.PowerSource.WaitRamp()
        time.sleep(hold_time)
        Hn = self.FC.getField()
        
        Data['dH'] = (Hp-Hn)
        Data['h'] = (Hp+Hn)/2
        print('Field : %0.2f Oe \n' % Data['h'])
        print('dH : %0.2f Oe \n' % Data['dH'],)

        for av_i in range(average_factor):
            Data['S11'][:,1,av_i] = self.VNAC.getSData(0, True)

        PAbs = 1 - numpy.abs(Data['S11'])**2
        P_pos = numpy.nanmean(PAbs[:,0,:], axis=-1)
        P_neg = numpy.nanmean(PAbs[:,1,:], axis=-1)
        Data['dP/dH'] = (P_pos - P_neg)/(Hp-Hn)
        
        Plot_dPdH(Data)
        
        ThD.check_stop()
        print('Done!')
        

        extra_info = ['',
                      'Mode : Fixed field',
                      'Field : %0.2f Oe' % Data['h'],
                      'Freq : %0.2f - %0.2f GHz'  % (Data['f'].min()/1E9, Data['f'].max()/1E9),
                      'dH : %s' % Data['dH'],
                      'Average factor : %d' % average_factor,
                      '']
        Data.info = self.Info + '\n'.join(extra_info)

        if file_name is not None:
            Data.save(file_name)
            Data.savetxt(file_name + '.dPxf', keys=['f', 'dP/dH'])



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
