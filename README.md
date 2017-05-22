# magdynlab

This software is developed for the automatization and control of the experiments of the Magnetization Dynamics Laboratory at the Brazilian Center for Physics Research (CBPF), Rio de Janeiro, Brazil.

The main purpose of this software is to be easy to use.
Anyone with a minimal python programing skill should be able to easly create new experiment routines.

## How to use:

This software uses three layers of abstraction to simplifiy the creation of experiment routines

## 1.- Instruments
> This layer handles the complexity of comunication with the phisical instruments

> For example, for setting out the output current of a power source KEPCO instrument, instead of doing:

> ```python
> import visa
>  
> ResourceName = 'GPIB0::6::INSTR'
>
> rm  = visa.ResourceManager()
> KepcoVI = open_resource(ResourceName)
> KepcoVI.write_termination = KepcoVI.LF
> KepcoVI.write('*CLS')
> KepcoVI.write('*RST')
> KepcoVI.write('OUTPUT ON')
> KepcoVI.write('FUNC:MODE CURR')
> KepcoVI.write('VOLT 20') #  Protection voltage 20 Volts
> 
> current_value = 10  # 10 Amps
> KepcoVI.write('CURR %0.4f' % current_value)
> ```

> the use of a magdynlab.instrument hides the SCPI codes and make the python code easier to write, read and understand

> ```python
> import magdynlab.instruments
>  
> PowerSource = magdynlab.instruments.KEPCO_BOP(GPIB_Address=6)
> PowerSource.CurrentMode()
> PowerSource.voltage = 20 #  Protection voltage 20 Volts
> 
> PowerSource.current = 10  # 10 Amps
> ```

## 2.- Controlers
> This layer hides complex software routines using the instruments

> For example, to set a magnetic field using a coil connected to a power source, the following code:

> ```python
> import magdynlab.instruments
> import time
>  
> PowerSource = magdynlab.instruments.KEPCO_BOP(GPIB_Address=6)
> PowerSource.CurrentMode()
> PowerSource.voltage = 20  # Protection voltage 20 Volts
> field_per_amp = 15.87  # Coil calibration in Oe/A
> max_rate = 30.0  # Max field rate in Oe/s
>
> field_to_set = 300.0 # 300 Oe
> for i in range(50):  # ramp to the field using 50 steps (simple implementation)
>     time_per_step = (field_to_set / max_rate) / 50
>     time.sleep(time_per_step)
>     PowerSource.current = (i * field_to_set / 50) / field_per_amp
> ```

> is simplified using a magdynlab.controler

> ```python
> import magdynlab.instruments
> import magdynlab.controlers
>  
> PowerSource = magdynlab.instruments.KEPCO_BOP(GPIB_Address=6)
> FieldControler = magdynlab.controlers.FieldControler(PowerSource)
> FieldControler.HperOut = 15.87  # Coil calibration in Oe/A
> FieldControler.MaxHRate = 30.0  # Max field rate in Oe/s
>
> field_to_set = 300.0 # 300 Oe
> FieldControler.setField(field_to_set)
> ```

## 3.- Experiments
> This layer is used to implement experiment routines

> For example, to use measure a magentization curve in a VSM the following code can be used:

> ```python
> import numpy
> import magdynlab.instruments
> import magdynlab.controlers
> import magdynlab.data_types
>  
> PowerSource = magdynlab.instruments.KEPCO_BOP(GPIB_Address=6)
> LockIn = magdynlab.instruments.SRS_SR830()
> 
> FC = magdynlab.controlers.FieldControler(PowerSource)
> VC = magdynlab.controlers.LockIn_Mag_Controler(LockIn)
> Data = magdynlab.data_types.Data2D()
> 
> FC.HperOut = 15.87  # Coil calibration in Oe/A
> FC.MaxHRate = 30.0  # Max field rate in Oe/s
> VC.emu_per_V = 18.7  # Sensing coils sensibility in emu/V
>
> def Measure_MxH(field_pts, file_name):
>     Data.reset()
>     for h in field_pts:
>         # Really easy to read loop! :-)
>         FC.setField(h)
>         m, sm = VC.getMagnetization()
>         Data.addPoint(h, m)
>     SaveData(file_name)
>     FC.TurnOff()
> ```

then, making a real measurement is as simple as:

> ```python
> r1 = numpy.linspace(-300, 300, 101)
> field_pts = numpy.r_[r1, r1[::-1]]  # 101 points from -300 Oe to 300 Oe 
>                                     # and the same in the oposite direction
> Measure_MxH(field_pts, 'my_output_file.txt')
> ```
