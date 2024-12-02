import time
import board
import digitalio
import rtc
import ds1302

# Define the clock, data and enable pins
clkpin = digitalio.DigitalInOut(board.GP7)
datapin = digitalio.DigitalInOut(board.GP8)
cepin = digitalio.DigitalInOut(board.GP6)

# Instantiate the ds1302 class
ds1302 = ds1302.DS1302(clkpin,datapin,cepin)

# Now, let us set the time
the_time = time.struct_time((2018,10,22,10,34,30,1,-1,-1))
ds1302.write_datetime(the_time)

print(the_time)

# Redefine the RTC class to link with the ds1302
class RTC(object):
    @property
    def datetime(self):
        return ds1302.read_datetime()

# Instantiate the rtc class and set the time source
r = RTC()
rtc.set_time_source(r)

# With this in place, you can now call the following to get the time!
time.localtime()
print(time.localtime())