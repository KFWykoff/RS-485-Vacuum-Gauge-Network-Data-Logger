import matplotlib.pyplot as plt
import sys
import serial
import time
import RPi.GPIO as GPIO
import csv
import datetime
import os.path
import signal


# create exception class for function timeout
# create signal handler for function timeout
# set signal alarm to manage fucntion call timouts
class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

signal.signal(signal.SIGALRM, timeout_handler)


GPIO.setwarnings(False)


# initialize pin to toggle transmit/receive modes
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT, initial=GPIO.HIGH)



# turn on interactive mode for updating plots
plt.ion()

# create list comprehensions for gauge data
x1 = []
y1 = []

x2 = []
y2 = []

x3 = []
y3 = []

x4 = []
y4 = []

while True:

    # set start time (file_t0) and desired run time (days) for data storage
    ser = serial.Serial('/dev/ttyAMA0', 19200, timeout = 1)
    file_t0 = time.time()
    days = 14
    seconds = (days * 24) * 60 * 60
    #seconds_int = int(seconds)

    # define method for collecting data and writing to csv files
    # string parameter is the gauge address
    def store_pressure(str):

        # create a csv file or write to existing file
        # if file is empty, assign "file_nonexist" condition
        f = open(('Gauge-'+ str +' Pressure Readings.csv'), 'a')
        filename = 'Gauge-'+ str +' Pressure Readings.csv'
        file_nonexist = os.stat(filename).st_size == 0

        # switch to data transmission mode
        GPIO.output(18, 1)
        time.sleep(0.01)

        #read the current time t in data logging process
        #get the date and time
        #find time elapsed (dt) since start of data logging process
        file_t = time.time()
        date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dt = file_t - file_t0

        # create and send 'read pressure' command
        ReadPressure = ('#'+str+'RD\r').encode('ascii')
        ser.write(ReadPressure)
        time.sleep(0.004)

        # switch to data receipt mode
        GPIO.output(18, 0)
        time.sleep(0.01)

        while True:
            # read one byte of byte string return
            output_byte_test = ser.read(1)
            time.sleep(0.1)

            #check that expected linefeed is detected
            if output_byte_test == b'*':
                output_byte = output_byte_test

                # if linefeed is detected append next 12 characters to get full return
                try:
                    output = output_byte + ser.readline(12)
                    time.sleep(0.1)

                # remove linefeed and address from left
                # remove carriage return '\r' from right
                # convert formatted return to a float value
                # if float conversion yields ValueError, begin again from a new single byte reading
                # if output format allows float conversion, break loop
                    pressure_bytes = output[4:-1]
                    time.sleep(1)
                    pressure = float(pressure_bytes)
                    time.sleep(1)
                except ValueError:
                    continue
                else:
                    break

        # optional readout (uncomment for gauge address and pressure):
        print(str)
        #time.sleep(0.1)
        print(pressure)
        #time.sleep(0.1)

        # check string for gauge being read and append appropriate plot data
        if str == '01':
            x1.append(date_time)
            y1.append(pressure)
            g1 = plt.figure('Gauge 1')
            plt.clf()
            plt.scatter(x1,y1)
            plt.ylabel('Pressure (Torr)')
            plt.plot(x1, y1, '-o')
            plt.xticks(rotation=90)
            plt.pause(.05)
            time.sleep(.05)


        elif str == '02':
            x2.append(date_time)
            y2.append(pressure)
            g2=plt.figure('Gauge 2')
            plt.clf()
            plt.scatter(x2,y2)
            plt.ylabel('Pressure (Torr)')
            plt.plot(x2, y2, '-o')
            plt.xticks(rotation=90)
            plt.pause(.05)
            time.sleep(.05)


        elif str == '03':
            x3.append(date_time)
            y3.append(pressure)
            g3=plt.figure('Gauge 3')
            plt.clf()
            plt.scatter(x3,y3)
            plt.ylabel('Pressure (Torr)')
            plt.plot(x3, y3, '-o')
            plt.xticks(rotation=90)
            plt.pause(.05)
            time.sleep(.05)


        else:
            x4.append(date_time)
            y4.append(pressure)
            g4=plt.figure('Gauge 4')
            plt.clf()
            plt.scatter(x4,y4)
            plt.ylabel('Pressure (Torr)')
            plt.plot(x4, y4, '-o')
            plt.xticks(rotation=90)
            plt.pause(.05)
            time.sleep(.05)
            plt.show()


        # write time stamp and pressure to csv
        # if file is new (file_nonexist), re-create headers
        with open(filename, 'a') as f:
            fieldnames = ['Date & Time', 'Pressure(Torr)']
            c = csv.DictWriter(f, fieldnames=fieldnames)
            if file_nonexist:
                c.writeheader()
            c.writerow({'Date & Time': date_time, 'Pressure(Torr)': pressure})

        # return dt for later comparison to desired collection time (i.e. "seconds" value on line )
        return(dt)
        time.sleep(.05)


    # continuously plot and log pressures to csv for each gauge
    # signal alarm trips exception for any function call without a return after 10 seconds
    # in the case of a timeout exception, restart readings from gauge 1
    # for each good reading (< 10 second function call), reset signal alarm.
    # assign 'dt' to function return (total elapsed time) for gauge 4
    while True:
        signal.alarm(10)
        try:
            store_pressure('01')
        except TimeoutException:
            continue
        else:
            signal.alarm(0)

            signal.alarm(10)
            try:
                store_pressure('02')
            except TimeoutException:
                continue
            else:
                signal.alarm(0)

                signal.alarm(10)
                try:
                    store_pressure('03')
                except TimeoutException:
                    continue
                else:
                    signal.alarm(0)

                    signal.alarm(10)
                    try:
                        dt = store_pressure('04')
                    except TimeoutException:
                        continue
                    else:
                        signal.alarm(0)

    # if dt > file_t0, remove csv files and close browser to remove plots
    # break loop to restart data logging process
    if dt >= seconds:
        os.remove('Gauge-01 Pressure Readings.csv')
        os.remove('Gauge-02 Pressure Readings.csv')
        os.remove('Gauge-03 Pressure Readings.csv')
        os.remove('Gauge-04 Pressure Readings.csv')
        os.system("pkill chromium")
        break
