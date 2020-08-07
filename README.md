# Kurt J. Lesker KJLC 300 Series Vacuum Gauge Network Data Logger & Plotter with Raspberry Pi

This Python code generates a data collection and plotting platform for an RS-485 network of KJLC 300 series vacuum gauges. The network interfaces with a Raspberry Pi (RPi) via the screw terminals on a Seeed Studios RS-485 Shield. Pressure readings are written to individual .csv files and appended to individual plots for each gauge, deleting and rewritting them after a desired time period.

## Some Specific Hardware/Software Used

The specific materials listed below were used in my particular set up, but the code would be applicable to varying equipment (using other KJL gauges with the KJLC ASCII command protocol, using another RPi RS-485 shield, etc.).

* **Vacuum Gauges:** Kurt J. Lesker KJLC 300 series (qty: 4)
  - Model: KJL300803
  - [Gauge Manual](https://www.lesker.com/newweb/gauges/pdf/manuals/kjlc_300_series_manual_v120.pdf)
* **Single Board Computer (SBC):** Raspberry Pi 3
  - Model: B v1.2
  - Operating System: Raspberry Pi OS (32-bit)
    - Version: May 2020
    - Kernel Version: 4.19
* **SBC Shield:** Seeed Studio RS-485 Shield for Raspberry Pi
  - Uses a MAX485 Chip
  - [Shield Wiki](https://wiki.seeedstudio.com/RS-485_Shield_for_Raspberry_Pi/)
  - [MAX485 Chip Data Sheet](https://files.seeedstudio.com/wiki/RS-485_Shield_for_Raspberry_Pi/res/RS-485.pdf)
* **Breakout Board Connectors for Gauges:** Uxcell Item Number A18112900ux0705 with case
  - Female D-Sub connectors with terminal blocks
  - 15 pin configuration
* **Wire:** 24 gauge, stranded


## Python Version & IDE Used
I used the latest stable branch of Python 3 for RPi at the time of assembling the gauge network (branch 3.7). The IDE used was Thonny 3.2.7.


## Wiring

Please refer to the simple diagram below for the wiring of the network. This is a typical RS-485 setup for half-duplex operation. I have omitted some equipment specific details, as they are not pertinent to understanding the overall layout. I have also omitted detailed schematics of the shield, the interplay between the shield and the RPi, etc., as these can be obtained from the manuals listed previously.

![Screen Shot 2020-08-07 at 8 29 27 AM](https://user-images.githubusercontent.com/57844952/89673390-7dcbd280-d8a3-11ea-9c61-b5b3848d6335.png)


## Some (Maybe Useful) Notes

*  #### Quick Reference Sheet

   To eliminate the need to continuously find the shield and gauge pinouts in their respective manuals while constructing the system, I hand drew a simple sheet                      
   for quick reference. Please see the document titled "Quick Pinout Reference." This includes the pinout for the RS-485 shield D-Sub interface and infomration on 
   the screw interface (with the later being used in this project and the former there for anyone who may choose to use the D-Sub). It includes pinout information      
   for both the 15-pin and 9-pin vacuum gauge D-Sub connectors (with the former being used in this case) and a simple diagram of a generic RS-485 network wired    
   for half-duplex operation.

*  #### Communication Pins

   Because this configuration enables only half-duplex operation of the RS-485 system, data transmission and reciept must occur seperately (i.e. a command must be   
   sent to the gauge with the shield in data transmission mode, then the shield must be switched to data receipt mode prior to reading the return data from a  
   gauge). On the RPi, GPIO 14 connects to the 'Data In' (DI) pin on the MAX485 chip, GPIO 15 connects to the 'Recieve Out' (RO) pin, and GPIO 18 connects to the 
   'Driver Enable' and 'Receiver Enable' (DE & RE) pins. The DE & RE pins are of opposite polarity (with DE active-high and RE active-low), thus they can be 
   controlled soley by GPIO 18, pulling DE high when transmitting data and RE low when receiving data (with their respective counterpart maintaining opposite 
   polarity).

   ***NOTE:*** Some RPi models (including the model used) require you to enable the UART pins (GPIO 14 and 15) for such operation. This can be done by making changes to the RPi config file. Instructions detailing this process are easily found online, as are details as to which models require these changes.

*  #### Communication Terminal Labeling

   The communication terminals (listed as terminal '485-A' and '485-B' on the screw terminal interface of the shield used and as 'RS485 DATA B(+)' and 'RS485 DATA  
   A(-)' in the manual for the gauges used) have oppositely labeled polarities [i.e. the shield has the configuration A(+), B(-)]. You will therefore need to make 
   sure that the 'A' data pin of the gauges are in line with the 'B' screw terminal on the shield and vice versa.

*  #### Serial Communication Timing

   Because this configuration enables only half-duplex operation, as described previously, timing is an issue in ensuring that a full command is sent from the RPi 
   and that a return message is not truncated. I found the timing cited in the gauge manual to be largely unhelpful. Moreover, I found that other manuals for KJL 
   gauges employing the same ASCII command protocol were inconsistent with those listed for the KJLC 300 series.

   The manual sates that the protocol should be 100% compatible with that of the Granville-Phillips Mini-Convectron Modules, however, I found the minimum 
   transmission times listed in the affilated Gainville-Phillips guides to be incongruent with those necessary to receive full return messages in many situations 
   (sometimes obtaining succesful readings with transmission times below the listed minima).

   My experience has also been (and I may be overlooking something) that very minor changes to the code usually require changes in transmission and receipt times 
   and that the margin of error is very small (often with only ~.001 second making a difference). When the timing is off, the readings often become littered with 
   null bytes or undesired binary-hex characters. I would appreciate it if anyone who has been more sucessful in efficiently finding the ideal transmission times 
   would please reach out and let me know what has worked for them.

*  #### RS-485 Commands

   For the particular operating system noted above the carriage return necessary to close all commands is '\r', with the entirety of the command given as a byte 
   string (denoted by single quotation marks) with ASCII encoding applied. For example:

  ```
  '#01RD\r'.encode('ascii')
  ```

* #### RS-485 Data Wires

  The data transmission wires were installed as a twisted pair. This (along with the use of differential signal reading) allows a high quality of noise reduction and the ability for long distance transmissions in RS-485 networks. Although the transmission distances and conditions of the laboratory likely did not necessitate the use of twisted data lines, it was a simple task to create them and may be worth the minimal additional effort in other appications, even when the demand is not certain. There are many tutorials on making use of a drill in the twisting process. I used heat shrink to secure either end of a twisted cable run, as well, which I found helpful.

* #### Power Supply

  To supply power to the gauges I spliced one of the KJLC power supplies specific to their model and tied this into the breakout board connected to the first vacuum gauge in the network. Put another way, I connected power to the first secondary RS-485 device (the first vacuum gauge downstream from the RPi) working under the primary device (the RPi). I then ran the power from this gauge to each subsequent secondary device (the remaining vacuum gauges). Following this arrangement allows for easier organization or wires as the power can be run in close proximity to the data wires. Splicing the wires allowed the usage of only the 15-pin D-Sub connections on the gauges. The power supply, prior to splicing is configured to plug directly into the 9-pin D-Sub and I believe one could hook all communication wiring to the 15 pin D-Sub and apply power directly to the 9-pin connection as intended. __It is important to note, however, that power cannot be supplied to both connections as this can damage the gauge.__

  Power to the RPi was delivered with a separate, standard power supply.
