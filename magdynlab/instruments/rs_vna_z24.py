# -*- coding: utf-8 -*-

import visa
import numpy
import time


#Author: Diego González Chávez
#email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com

#This classes controls the: 
#Vector Network Analyzer
#Rohde & Schwarz : VNA Z24

#Make documentation
#TODO:


class Channel(object):
    def __init__(self, parent, ChanNum = 1, ID = 'Auto'):
        self.parent = parent
        self.write = parent.write
        self.ask = parent.ask
        self.askValues = parent.askValues

        self._Number = ChanNum
        if ID == 'Auto':
            self.ID = 'Ch%d' % self.Number
        else:
            self.ID = ID
        self.write('CONF:CHAN%d:STAT ON' % self.Number)

    def __getNumber(self):
        return self._Number
    Number = property(__getNumber, None, None, )
        
    def __getTraces(self):
        TrcNames = (self.ask('CONF:TRAC:CAT?').strip('\'')).split(',')[1::2]
        vTraces = []
        for trN in TrcNames:
            tr = Trace(self, trN)
            if tr.ChannelNumber == self.Number:
                vTraces.append(tr)
        return vTraces
    Traces = property(__getTraces, None, None, )
    
    def __getBandwidth(self):
        BW = self.ask('SENS%(Ch)d:BWID?' %{'Ch':self.Number})
        return numpy.float(BW)
    def __setBandwidth(self, newBW):
        self.write('SENS%(Ch)d:BWID %{BW}0.9E' %{'Ch':self.Number, 'BW':newBW})
    Bandwidth = property(__getBandwidth, __setBandwidth, None, )
    
    def SetSweep(self, start, stop, np, na = 50):
        self.write('SENS%(Ch)d:FREQ:STAR %(f)0.9E' %{'Ch':self.Number, 'f':start})
        self.write('SENS%(Ch)d:FREQ:STOP %(f)0.9E' %{'Ch':self.Number, 'f':stop})
        self.write('SENS%(Ch)d:SWE:POIN %(n)d' %{'Ch':self.Number, 'n':np})

        self.write('SENS%(Ch)d:AVER:COUN %(n)d' %{'Ch' : self.Number, 'n' : na})
        if na > 1:
            self.write('SENS%(Ch)d:AVER:STAT ON' %{'Ch' : self.Number})
        else:
            self.write('SENS%(Ch)d:AVER:STAT OFF' %{'Ch' : self.Number})
    def getSTIM(self):
        return self.askValues('CALC%(Ch)d:DATA:STIM?' %{'Ch' : self.Number})
    def INIT(self):
        while True:
            self.write('INIT%(Ch)d:IMM' %{'Ch' : self.Number})
            if self.ask('SYST:ERR:ALL?') == '0,"No error"':
                break

class Trace(object):
    def __init__(self, parent, Name = 'Auto'):
        self.parent = parent
        self.write = parent.write
        self.ask = parent.ask
        self.askValues = parent.askValues
        self.Name = Name
        self.__ChanNumber = int(self.ask('CONF:TRAC:CHAN:NAME:ID? \'' + self.Name + '\''))
        
    @property
    def ChannelNumber(self):
        #Channel Number
        return self.__ChanNumber
        
    def getNewData(self, timeout = 0):
        ChN = self.ChannelNumber
        self.write('INIT:CONT OFF')
        averStat = self.ask('SENS%(Ch)d:AVER:STAT?' %{'Ch':ChN})
        if averStat == '1':
            averCount = int(self.ask('SENS%(Ch)d:AVER:COUN?' %{'Ch':ChN}))
            self.write('SENS%(Ch)d:AVER:CLE' %{'Ch':ChN})
        else:
            averCount = 1
        
        for i in range(averCount):
            self.parent.INIT()
            while self.ask('CALC%(Ch)d:DATA:NSW:COUN?' %{'Ch':ChN}) == '0':
                time.sleep(0.01)
    def getFDAT(self, New = False):
        
        #Return formatted trace data, according to the selected trace format
        
        ChN = self.ChannelNumber
        self.write('CALC%(Ch)d:PAR:SEL \'' %{'Ch':ChN} + self.Name + '\'')
        if New:
            self.getNewData()
        return self.askValues('CALC%(Ch)d:DATA? FDAT' %{'Ch':ChN})
    def getSDAT(self, New = False):
        
        #Returns unformatted trace data: Real and imaginary part of each measurement point
        #For wave quantities the unit is Volts
        
        ChN = self.ChannelNumber
        self.write('CALC%(Ch)d:PAR:SEL \'' %{'Ch':ChN} + self.Name + '\'')
        if New:
            self.getNewData()
        SDAT = self.askValues('CALC%(Ch)d:DATA? SDAT' %{'Ch':ChN})
        return SDAT[::2] + 1.0j*SDAT[1::2]
    def SaveSData(self, fileName, New = False):
        f = self.parent.getSTIM()
        S = self.getSDAT(New)
        numpy.savetxt(fileName, numpy.array([f, S.real, S.imag]).transpose(), fmt = '%.16E')

class Diagram(object):
    def __init__(self, parent, Name = 'Auto'):
        self.parent = parent
        self.VI = parent.VI
        self.Traces = []

class VectorNetworkAnalyser(object):
    def __init__(self, GPIB_Address = 20, GPIB_Device = 0, ResourceName = None):
        if ResourceName is None:
            ResourceName = 'GPIB%d::%d::INSTR' %(GPIB_Device, GPIB_Address)
        self.VI = visa.ResourceManager().open_resource(ResourceName)
        self.VI.write('*CLS')
        self.VI.write('SYST:COMM:GPIB:RTER EOI')
        self.VI.write_termination = None
        self.VI.read_termination = self.VI.LF
        #self.VI.write('*RST')
        self.write('FORM:DATA REAL, 64')
        self.Ch1 = Channel(self, 1)
        #self.Ch2 = Channel(self, 2)
    def __del__(self):
        self.VI.close()
    def checkSTB(self):
        c0 = time.clock()
        while numpy.binary_repr(self.VI.stb)[-1] == 0:
            if time.clock() - c0 >= 1:
                print("Device not ready")
                raise
    def write(self, command):
        self.checkSTB()
        self.VI.write(command)
    def ask(self, command):
        self.checkSTB()
        #return self.VI.ask(command)
        return self.VI.query(command)
    def askValues(self, command):
        self.checkSTB()
        #return numpy.array(self.VI.ask_for_values(command, visa.double))
        self.VI.read_termination = None
        data =  numpy.array(self.VI.query_binary_values(command, datatype='d'))
        self.VI.read_termination = self.VI.LF
        return data