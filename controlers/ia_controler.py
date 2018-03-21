# coding=utf-8

# Author: Diego González Chávez
# email : diegogch@cbpf.br / diego.gonzalez.chavez@gmail.com
#
# Impedance Analizer controler
#
# TODO:
# Make documentation

__all__ = ['IA_Controler']


class IA_Controler(object):
    '''
    Impedance Analizer controler
    '''

    def __init__(self, IA_instrument):
        self.IA = IA_instrument
        self._Tr = self.IA.Ch1.traces[0]

    def getRData(self, new=True):
        X = self._Tr.getRDAT(new)
        return X.copy()

    @property
    def frequencies(self):
        return self.IA.Ch1.fs
