# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Vector Network Analizer controller
#
# TODO:
# Make documentation

__all__ = ['VNA_Controller']


class VNA_Controller(object):
    '''
    Vector Network Analizer controller
    '''

    def __init__(self, VNA_instrument):
        self.VNA = VNA_instrument

    def getSData(self, TrN, new=True):
        '''
        Get unformatted trace data:
        Real and imaginary part of each measurement point.
        2 values per trace point irrespective of the selected trace format
        '''
        X = self.VNA.Ch1.traces[TrN].getSDAT(new)
        return X.copy()

    def getFData(self, TrN, new=True):
        '''
        Get formatted trace data:
        1 values per trace point as the selected trace format
        '''
        X = self.VNA.Ch1.traces[TrN].getFDAT(new)
        return X.copy()

    @property
    def frequencies(self):
        return self.VNA.Ch1.getSTIM()

    def cleanDisplayArea(self):
        self.VNA.write('SYST:DISP:UPDATE ON')
        areas = self.VNA.query('DISP:CAT?').strip('\'').split(',')[::2]
        if not '1' in areas:
            self.VNA.write('DISP:WIND1:STAT ON')
        for area in areas:
            if area is not '1':
                self.VNA.write('DISP:WIND%s:STAT OFF' % area)
        self.VNA.write('CALC1:PAR:DEL:ALL')

    def set_traces_SParameters_1P(self):
        self.cleanDisplayArea()

        self.VNA.write('CALC1:PAR:DEF \'Trc1\', S11')
        self.VNA.write('CALC1:PAR:SEL \'Trc1\'')
        self.VNA.write('CALC1:FORM MLIN')
        self.VNA.write('DISP:WIND1:TRAC1:FEED \'Trc1\'')
        self.VNA.write('DISP:WIND1:TRAC1:Y:PDIV 0.11')
        self.VNA.write('DISP:WIND1:TRAC1:Y:RPOS 50')
        self.VNA.write('DISP:WIND1:TRAC1:Y:RLEV 0.5')

    def set_traces_SParameters_2P(self):
        self.cleanDisplayArea()

        self.VNA.write('CALC1:PAR:DEF \'Trc1\', S11')
        self.VNA.write('CALC1:PAR:SEL \'Trc1\'')
        self.VNA.write('CALC1:FORM MLIN')
        self.VNA.write('CALC1:PAR:DEF \'Trc2\', S21')
        self.VNA.write('CALC1:PAR:SEL \'Trc2\'')
        self.VNA.write('CALC1:FORM MLIN')
        self.VNA.write('CALC1:PAR:DEF \'Trc3\', S22')
        self.VNA.write('CALC1:PAR:SEL \'Trc3\'')
        self.VNA.write('CALC1:FORM MLIN')
        self.VNA.write('CALC1:PAR:DEF \'Trc4\', S12')
        self.VNA.write('CALC1:PAR:SEL \'Trc4\'')
        self.VNA.write('CALC1:FORM MLIN')

        self.VNA.write('DISP:WIND1:TRAC1:FEED \'Trc1\'')
        self.VNA.write('DISP:WIND1:TRAC2:FEED \'Trc2\'')
        self.VNA.write('DISP:WIND1:TRAC3:FEED \'Trc3\'')
        self.VNA.write('DISP:WIND1:TRAC4:FEED \'Trc4\'')

        self.VNA.write('DISP:WIND1:TRAC1:Y:PDIV 0.11')
        self.VNA.write('DISP:WIND1:TRAC2:Y:PDIV 0.11')
        self.VNA.write('DISP:WIND1:TRAC3:Y:PDIV 0.11')
        self.VNA.write('DISP:WIND1:TRAC4:Y:PDIV 0.11')

        self.VNA.write('DISP:WIND1:TRAC1:Y:RPOS 50')
        self.VNA.write('DISP:WIND1:TRAC2:Y:RPOS 50')
        self.VNA.write('DISP:WIND1:TRAC3:Y:RPOS 50')
        self.VNA.write('DISP:WIND1:TRAC4:Y:RPOS 50')
        
        if self.VNA.query_float('DISP:WIND1:TRAC1:Y:RPOS?') != 50:
            self.VNA.write('DISP:WIND1:TRAC1:Y:RPOS 5')
            self.VNA.write('DISP:WIND1:TRAC2:Y:RPOS 5')
            self.VNA.write('DISP:WIND1:TRAC3:Y:RPOS 5')
            self.VNA.write('DISP:WIND1:TRAC4:Y:RPOS 5')

        self.VNA.write('DISP:WIND1:TRAC1:Y:RLEV 0.5')
        self.VNA.write('DISP:WIND1:TRAC2:Y:RLEV 0.5')
        self.VNA.write('DISP:WIND1:TRAC3:Y:RLEV 0.5')
        self.VNA.write('DISP:WIND1:TRAC4:Y:RLEV 0.5')

    def set_traces_WaveQuantities(self):
        self.cleanDisplayArea()

        self.VNA.write('CALC1:PAR:DEF \'Trc5\', R1')
        self.VNA.write('CALC1:FORM MLIN')
        self.VNA.write('CALC1:PAR:DEF \'Trc6\', R2')
        self.VNA.write('CALC1:FORM MLIN')
        self.VNA.write('CALC1:PAR:DEF \'Trc7\', A')
        self.VNA.write('CALC1:FORM MLIN')
        self.VNA.write('CALC1:PAR:DEF \'Trc8\', B')
        self.VNA.write('CALC1:FORM MLIN')

        self.VNA.write('DISP:WIND1:TRAC5:FEED \'Trc5\'')
        self.VNA.write('DISP:WIND1:TRAC6:FEED \'Trc6\'')
        self.VNA.write('DISP:WIND1:TRAC7:FEED \'Trc7\'')
        self.VNA.write('DISP:WIND1:TRAC9:FEED \'Trc8\'')

    def backup_sweep(self):
        freqStart = self.VNA.query('SENS1:FREQ:STAR?')
        freqStop = self.VNA.query('SENS1:FREQ:STOP?')
        sweepPoints = self.VNA.query('SENS1:SWE:POIN?')
        self._sweep_data = [freqStart, freqStop, sweepPoints]

    def restore_sweep(self):
        freqStart, freqStop, sweepPoints = self._sweep_data
        self.VNA.write('SENS1:SWE:POIN %s' %sweepPoints)
        self.VNA.write('SENS1:FREQ:STAR %s' %freqStart)
        self.VNA.write('SENS1:FREQ:STOP %s' %freqStop)


