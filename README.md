# (Still being written)
# OpenMMS-T4G
![alt text](https://github.com/TEPGomes/OpenMMS-T4G/blob/df8c1e62fc22bc2640ab8e6385d9d2ce8b8dda7e/Images/mini-logo-150px_1.png)
## Project description and background
OpenMMS-T4G is a project developed in the scope of [TOOLING4G - Advanced Tools for Smart Manufacturing](https://tooling4g.toolingportugal.com/), with the following main objectives:
- Creating an open-source-based hardware and software monitoring system to acquire data from various sensors and types of sensor, installed in/on an injection molding tool (the mold);
- Provide a lower cost system, when compared to the conventional ones, that allows the simple collection of data from sensors in the mold;
- Allow visualization of data during the process;

Through this or similar systems, smaller companies and entities from the research and education fields, can be empowered to implement Industry 4.0 concepts in the injection molding process, on lower budgets. This includes development of fault prediction algorithms for planned maintenance, part quality prediction algorithms, process optimization, among other possibilities.

In its current form, OpenMMS-T4G includes a software for connection with one or both of two modules for data acquisition, also developed under the TOOLING4G project. From these modules, currently, only the firmware referring to the Arduino-based one is shared in this repository. With the firmware and adequate hardware, this module can read data from up to two thermocouples, a force sensor, and a cavity pressure sensor. The other module sends data, acquired by a 3D acclerometer and gyroscope, independently from the Arduino.
## Libraries and prerequisites
This section lists what is needed to run the full software and firmware for an Arduino-based data acquisition module:
### Hardware:
- Windows 10 OS - Software has been developed and tested in, and to work in, a Windows 10 operating system;
- Arduino Mega board;
- Custom circuitry to receive sensor data in the Arduino;
### Python libraries:
- [PyQt5](https://pypi.org/project/PyQt5/);
- [pyqtgraph](https://www.pyqtgraph.org/);
- [numpy](https://numpy.org/);
- [sys](https://docs.python.org/3/library/sys.html);
- [random](https://docs.python.org/3/library/random.html);
- [os](https://docs.python.org/3/library/os.html);
- [csv](https://docs.python.org/3/library/csv.html);
- [serial](https://pyserial.readthedocs.io/en/latest/);
- [time](https://docs.python.org/3/library/time.html);
- [queue](https://docs.python.org/3/library/queue.html);
- [functools](https://docs.python.org/3/library/functools.html);
### Arduino libraries:
- 
## How to use
It is our intention to publish a scientific paper detailling the system, how it works, and its current performance. Once we succeed, a link to it will be made available here. Otherwise, further details will be shared here eitherway.
## Current state of development
In its current state of development, there are still known bugs that need to be sorted. Despite this, a monitoring system based on the project's software and firmware has been tested to monitor sensors installed in and on injection molds during processing, and data has been successfully acquired from the sensors.
