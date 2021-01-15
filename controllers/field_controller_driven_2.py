# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Magnetic Field controller
#
# TODO:
# Make documentation

import time
import numpy

__all__ = ['FieldController_LS643']


class FieldController_LS643(object):
    '''
    Magnetic field controller

    to be used with the LakeShore 643 source
    and a voltmeter measuring a hall probe
    '''

    def __init__(self, PowerSource_instrument, Voltmeter_instrument):
        self.PowerSource = PowerSource_instrument
        self.VoltMeter = Voltmeter_instrument

        self.InToH = 10000  #Oe por valor de entrada medidos (Oe/V)
        self.HperOut = 250.0 #Oe por valore de salida (Oe/A) (max)

        self.delay_mult = 1 #field delay multiplyer
        self.field_mult = 1 #field aproach multiplyer

    def __del__(self):
        pass

    def getField(self, delay = 0.5):
        """
        Returns the measured magnetic field
        Usage :
            getField()
            getField(Unit)
        Units:
            'Oe' : Field in Oe
            'A/m' : Field in A/m
        """
        time.sleep(delay * self.delay_mult)
        vIn = self.VoltMeter.voltage
        
        return self.InToH * vIn


    def setField(self, Fld, Tol = 0.5, FldStep = 1.0):
        """
        Set Magnetic Field
        """
        sng = numpy.sign(Fld - self.getField())
      
        while ( sng * (Fld - self.getField(delay = 0)) > 20 * self.field_mult):
            self.PowerSource.setpoint = self.PowerSource.measured_current + sng * 20/self.HperOut
            self.PowerSource.WaitRamp()

        while ( sng * (Fld - self.getField(delay = 0.2)) > Tol ):
            self.PowerSource.setpoint = self.PowerSource.measured_current + sng * FldStep/self.HperOut
            self.PowerSource.WaitRamp()

    def TurnOff(self):
        self.PowerSource.TurnOff(wait = True)

    def BEEP(self):
        pass
 
