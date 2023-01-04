"""
Loow cost monitoring system.
Prepared to dysplay and store values from an accelerometer and gyroscope module and an Arduino module receiving data from a force sensor, a cavity pressure and up to two temperature sensors. 
Developed for the project TOOLING4G.

User interface based on PyQt5.
"""
from PyQt5 import QtWidgets, QtCore, QtGui, uic, Qt
import pyqtgraph as pg
import numpy as np
import sys
import random
import os
import csv
import serial
from serial.tools import list_ports
from time import sleep
from time import perf_counter
import queue
from functools import partial

import MainWindow
import ComSettings
import ModuleSelect
import help_dialog
from graphswidget import GraphsWidget

##########################################################################################
################################## Program ###############################################
##########################################################################################

# User Interface threads: ################################################################
##########################################################################################
# The main GUI window class:
class MainWindow(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
    """Main window of the GUI:

    Shows buttons for configuration, to connect or disconnect serial communication, start/stop reading, save session data and exit app;
    Shows the "real-time" plots of the sensors;
    Shows messages in a message box.
    """
    #Define signals:
    startSig = QtCore.pyqtSignal() #Start monitoring signal
    stopSig = QtCore.pyqtSignal() #Stop monitoring signal
    disconnectSig = QtCore.pyqtSignal() #Disconnect devices signal
    disconnectSig2 = QtCore.pyqtSignal() #Disconnect device 2 signal
    stopThreadSig = QtCore.pyqtSignal() #Stop serial threads signal
    saveSig =QtCore.pyqtSignal() #Save session signal

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.modules = 0 # Variable to store device choice: 0 - no device selected; 1 - module 1 selected; 2 - module 2 selected; 3 - both modules selected.
        self.sensors = [] #List: Letters for sensors expected to be 
        #                                     connected to system. T - Temperature sensor; 
        #                                     P - Pressure sensor; F - Force sensor; 
        #                                     A - Accelerometer; G - Gyroscope.
        self.nsensors_m1 = 4 #Number of sensors in module 1
        self.nsensors_m2 = 2 #number of sensors in module 2
        self.time_lim = 30 #Monitoring max time
        self.br1 = '' #Baud rate dev 1
        self.port1 = '' #Port dev 1
        self.br2 = '' #Baud rate dev 2
        self.port2 = '' #Port dev 2
        self.dev1_connected = False #State of device 1 (connected/disconnecte => True/False)
        self.dev2_connected = False #State of device 2 (connected/disconnecte => True/False)
        self.nplots = 0 #number of subplots to create = number of sensors. (default -> module 1)
        self.xdata = [] #x data list for all x data from a session
        self.ydata = [] #y data list for all y data from a session
        self.xdata_m2 = [] #x data list for module 2 (vibration - A/G)
        self.ydata_m2 = [] #y data list for module 2 (vibration - A/G)
        self.xdata_plts = [] #x data list for plots
        self.ydata_plts = [] #y data list for plots
        self.xdata_plts_m2 = [] #x data list for module 2 plots
        self.ydata_plts_m2 = [] #y data list for module 2 plots
        self.plotDataItem_lst = [] #List for plot data items identifiers
        self.splotlist = [] #List of subplots (initialized)
        self.colors_xyz = ['b','r','g'] #Colors for module 2 graphs
        #LABELS:
        self.x_Label = 'Time [s]'
        self.y_labels = ['Temperature 1 [°C]','Temperature 2 [°C]','Pressure [bar]','Force [N]','Acceleration [g]','Angular velocity [dps/1000]']
        self.gyro_labels = ['Gx','Gy','Gz']
        self.accel_labels = ['Ax','Ay','Az']

        # Run configure function when configurationButton is clicked:
        self.configurationButton.clicked.connect(self.configure)
        # Run exit_app_event function when exitButton is clicked:
        self.exitButton.clicked.connect(self.closeEvent)
        # Run start_monitoring function when startButton is clicked
        self.startButton.clicked.connect(self.start_monitoring)
        # Run find_device function when findDeviceButton is clicked:
        self.findDeviceButton.clicked.connect(self.find_device)
        # Run stopReading and stop_message functions when stopButton is clicked:
        self.stopButton.clicked.connect(self.stopReading)
        self.stopButton.clicked.connect(self.stop_message)
        # Run rem_devs function when removeDeviceButton is clicked:
        self.removeDeviceButton.clicked.connect(self.rem_devs)
        # Run next_Session function when nextButton is clicked:
        self.nextButton.clicked.connect(self.next_Session)
        # Run save_Session function when saveSessionButton is clicked:
        self.saveSessionButton.clicked.connect(self.save_Session)

        self.aboutAction = QtWidgets.QAction("&About...", self)
        self.menuHelp.addAction(self.aboutAction)
        self.aboutAction.triggered.connect(self.onAboutTriggered)

        #Initial message:
        self.messagesBox.appendHtml('<p style="color:blue;">TOOLING4G Mould Monitoring System v1.0.</p><p></p>')

    def onAboutTriggered(self):
        '''
        Executed when About button is clicked:

        Show help dialog.
        '''
        self.About = help_dialog()
        self.About.show()



    def closeEvent(self, event):
        '''
        Action for when exitButton is clicked.

        1 - emit signal to stop serial thread loop.
        2 - A message appears asking if user really wishes to leave.
        3 - Message has 2 buttons: Return and Leave.
            3.1 - Leave - Exit app
            3.2 - Return - Close message
        '''
        self.stopThreadSig.emit()

        reply = QtWidgets.QMessageBox.question(self, "Message", 'Are you sure you want to leave? Any unsaved work will be lost.', 
        QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Close)

        if reply == QtWidgets.QMessageBox.Close:
            app.quit()
        else:
            try:
                event.ignore()
            except:
                pass


    def save_Session(self):
        '''
        Save session dialog:

        Save a csv file with session data.
        '''
        sensor_list = self.sensors
        fname = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Settings as:', os.getenv('HOME'), 'CSV(*.csv)')

        if fname[0] != '':
            with open(fname[0], 'w', newline='') as csv_file:
                writer = csv.writer(csv_file, dialect='excel')

                header = ["t"]
                for sensor in self.sensors:
                    if sensor == "A":
                        header.append('Ax')
                        header.append('Ay')
                        header.append('Az')
                    elif sensor == "G":
                        header.append('Gx')
                        header.append('Gy')
                        header.append('Gz')
                    else:
                        header.append(sensor)

                if self.modules == 1:
                    self.module1_Data_Write(header, writer)
                elif self.modules == 2:
                    self.module2_Data_Write(header, writer)
                elif self.modules == 3:
                    self.all_Modules_Data_Write(header, writer)
                
                #Saved session message:
                self.messagesBox.appendHtml('<p>Session data was saved.</p>')

    def module1_Data_Write(self,header,writer): # only module 1
        '''
        Write data colected by module 1 (temperature, pressure or force)
        '''
        for row in range(len(self.xdata) + 1):
            row_data = []
            if row == 0:
                row_data = header
            else:
                for col in range(len(self.sensors) + 1):
                    if col == 0:
                        row_data.append(self.xdata[row-1])
                    else:
                        row_data.append(self.ydata[row-1][col-1])
            writer.writerow(row_data)

    def module2_Data_Write(self,header,writer): # only module 2 (has 'A' and 'G' sensors)
        '''
        Write data colected by module 2 (3D accelerometer and 3D gyroscope)
        '''
        for row in range(len(self.xdata_m2) + 1):
            row_data = []
            if row == 0:
                row_data = header
            else:
                for col in range(len(self.ydata_m2[row-1])+1):
                    if col == 0:
                        row_data.append(self.xdata_m2[row-1])
                    else:
                        row_data.append(self.ydata_m2[row-1][col-1])
            writer.writerow(row_data)

    def all_Modules_Data_Write(self,header,writer): # both module 1 and 2
        '''
        Write data colected by both modules.

        For when both modules operate simultaneously.
        '''
        header.append("t2")
        x = 0
        if len(self.xdata) > len(self.xdata_m2):
            x = len(self.xdata)
            while len(self.xdata) > len(self.xdata_m2):
                self.xdata_m2.append(' ')
                self.ydata_m2.append('[ , , , , , ]')
        else: 
            x = len(self.xdata_m2)
            while len(self.xdata) < len(self.xdata_m2):
                self.xdata.append(' ')
                self.ydata.append(' ')

        for row in range(x + 1):
            row_data = []
            if row == 0:
                row_data = header
            else:
                for col in range(len(self.sensors) + 1):
                    if col == 0:
                        row_data.append(self.xdata[row-1])
                    else:
                        if col <= self.nsensors_m1:
                            row_data.append(self.ydata[row-1][col-1])
                        else:
                            if self.sensors[col-1] == 'A':
                                for i in range(3):
                                    row_data.append(self.ydata_m2[row-1][i])
                            elif self.sensors[col-1] == 'G':
                                for i in range(3, 6):    
                                    row_data.append(self.ydata_m2[row-1][i])
                row_data.append(self.xdata_m2[row - 1])
            writer.writerow(row_data)

       
    def stopReading(self):
        '''
        To emit the signal to stop reading and enable/disable the buttons acordingly.
        '''
        self.stopSig.emit()
        sleep(0.2)

        #Enable/Disable buttons:
        self.stopButton.setEnabled(False)
        self.removeDeviceButton.setEnabled(True)
        self.nextButton.setEnabled(True)
        self.saveSessionButton.setEnabled(True)

    def stop_message(self):
        '''
        Write the stop message in the message box.
        '''
        self.messagesBox.appendHtml('<p>The session was stopped.</p>')

    def end_message(self):
        '''
        Write the end message in the message box.
        '''
        self.messagesBox.appendHtml('<p>Finished session.</p>')


    def rem_devs(self):
        '''
        Remove/disconnect the module 1 and/or module 2 devices.

        Enable/disable the buttons acordingly.
        '''
        if self.modules == 1:
            self.disconnectSig.emit()
            self.stopThreadSig.emit()
            sleep(0.2)
            #Disconnect signals:
            self.SerialThread.ConnectSig.disconnect(self.HandleThConnectSig)
            self.startSig.disconnect(self.SerialThread.startSignalRec)
            self.disconnectSig.disconnect(self.SerialThread.disconnectSerial)
            self.stopThreadSig.disconnect(self.SerialThread.stop_Thread)

        elif self.modules == 2:
            self.disconnectSig2.emit()
            self.stopThreadSig.emit()
            sleep(0.2)
            #Disconnect signals:
            self.SerialThread2.ConnectSig2.disconnect(self.HandleThConnectSig2)
            self.startSig.disconnect(self.SerialThread2.startSignalRec)
            self.disconnectSig2.disconnect(self.SerialThread2.disconnectSerial)        
            self.stopThreadSig.disconnect(self.SerialThread2.stop_Thread)

        elif self.modules == 3:
            self.disconnectSig.emit()
            self.disconnectSig2.emit()
            self.stopThreadSig.emit()
            sleep(0.2)
            #Disconnect signals:
            #Ser. Thread 1:
            self.SerialThread.ConnectSig.disconnect(self.HandleThConnectSig)
            self.startSig.disconnect(self.SerialThread.startSignalRec)
            self.disconnectSig.disconnect(self.SerialThread.disconnectSerial)
            self.stopThreadSig.disconnect(self.SerialThread.stop_Thread)
            #Ser. Thread 2:
            self.SerialThread2.ConnectSig2.disconnect(self.HandleThConnectSig2)
            self.startSig.disconnect(self.SerialThread2.startSignalRec)
            self.disconnectSig2.disconnect(self.SerialThread2.disconnectSerial)
            self.stopThreadSig.disconnect(self.SerialThread2.stop_Thread)
        
        #Enable/Disable buttons:
        self.configurationButton.setEnabled(True)
        self.removeDeviceButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        self.startButton.setEnabled(False)

        #Disconnected devs message:
        self.messagesBox.appendHtml('<p>All devices are disconnected.</p>')


    def next_Session(self):
        '''
        Reset variables for data storage and plots.
        Setup the plots.
        Initially defined configuration is assumed.
        Emit start signal.
        '''
        if self.modules == 3:
            self.reset_Data_n_Plot_Vars()
    
            self.SubplotSetup()
            self.graphThread_m1 = GraphThread(self.dataQueue, self.sensors[0:self.nsensors_m1], self.time_lim)
            self.graphThread_m1.monitTimeEndSig.connect(self.stopReading)
            self.graphThread_m1.monitTimeEndSig.connect(self.end_message)
            self.graphThread_m1.graphUpdateSig.connect(partial(self.ploter, 31))
            self.graphThread_m1.graphEndSig.connect(self.receiveXYData)
            self.SerialThread.readQueueSig.connect(self.graphThread_m1.readQueue)
            self.stopSig.connect(self.graphThread_m1.stop_Thread)

            self.graphThread_m2 = GraphThread(self.dataQueue2, self.sensors[self.nsensors_m1:(self.nsensors_m1 + self.nsensors_m2)], self.time_lim)
            self.graphThread_m2.monitTimeEndSig.connect(self.stopReading)
            self.graphThread_m2.monitTimeEndSig.connect(self.end_message)
            self.graphThread_m2.graphUpdateSig.connect(partial(self.ploter, 32))
            self.graphThread_m2.graphEndSig.connect(self.receiveXYData_m2)
            self.SerialThread2.readQueue2Sig.connect(self.graphThread_m2.readQueue)
            self.stopSig.connect(self.graphThread_m2.stop_Thread)

            self.stopButton.setEnabled(True)
            #Monitoring message:
            self.messagesBox.appendHtml('<p>Monitoring...</p>')
            self.graphThread_m1.start()
            self.graphThread_m2.start()
            self.startSig.emit()
        else:
            self.reset_Data_n_Plot_Vars()

            self.startButton.setEnabled(False)
            self.findDeviceButton.setEnabled(False)
    
            self.SubplotSetup()

            if self.modules == 1:
                self.graphThread = GraphThread(self.dataQueue, self.sensors, self.time_lim)
                self.graphThread.graphUpdateSig.connect(partial(self.ploter, 1))
                self.graphThread.monitTimeEndSig.connect(self.stopReading)
                self.graphThread.monitTimeEndSig.connect(self.end_message)
                self.graphThread.graphEndSig.connect(self.receiveXYData)
                self.SerialThread.readQueueSig.connect(self.graphThread.readQueue)
            elif self.modules == 2:
                self.graphThread = GraphThread(self.dataQueue2, self.sensors, self.time_lim)
                self.graphThread.graphUpdateSig.connect(partial(self.ploter, 2)) 
                self.graphThread.monitTimeEndSig.connect(self.stopReading)
                self.graphThread.monitTimeEndSig.connect(self.end_message)
                self.graphThread.graphEndSig.connect(self.receiveXYData_m2)
                self.SerialThread2.readQueue2Sig.connect(self.graphThread.readQueue)
            self.stopSig.connect(self.graphThread.stop_Thread)

            self.stopButton.setEnabled(True)
            #Monitoring message:
            self.messagesBox.appendHtml('<p>Monitoring...</p>')
            self.graphThread.start()
            self.startSig.emit()

        self.nextButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.removeDeviceButton.setEnabled(False)
        self.saveSessionButton.setEnabled(False)

  
    def start_monitoring(self):
        '''
        Start monitoring:
        - Setup subplots;
        - Emit start signal.
        '''
        if self.modules == 3:
            if self.dev1_connected == True and self.dev2_connected == True:
                self.reset_Data_n_Plot_Vars()

                self.startButton.setEnabled(False)
                self.findDeviceButton.setEnabled(False)
                self.removeDeviceButton.setEnabled(False)
        
                self.SubplotSetup()
                self.graphThread_m1 = GraphThread(self.dataQueue, self.sensors[0:self.nsensors_m1], self.time_lim)
                self.graphThread_m1.monitTimeEndSig.connect(self.stopReading)
                self.graphThread_m1.monitTimeEndSig.connect(self.end_message)
                self.graphThread_m1.graphUpdateSig.connect(partial(self.ploter, 31))
                self.graphThread_m1.graphEndSig.connect(self.receiveXYData)
                self.SerialThread.readQueueSig.connect(self.graphThread_m1.readQueue)
                self.stopSig.connect(self.graphThread_m1.stop_Thread)

                self.graphThread_m2 = GraphThread(self.dataQueue2, self.sensors[self.nsensors_m1:(self.nsensors_m1 + self.nsensors_m2)], self.time_lim)
                self.graphThread_m2.monitTimeEndSig.connect(self.stopReading)
                self.graphThread_m2.monitTimeEndSig.connect(self.end_message)
                self.graphThread_m2.graphUpdateSig.connect(partial(self.ploter, 32))
                self.graphThread_m2.graphEndSig.connect(self.receiveXYData_m2)
                self.SerialThread2.readQueue2Sig.connect(self.graphThread_m2.readQueue)
                self.stopSig.connect(self.graphThread_m2.stop_Thread)

                self.stopButton.setEnabled(True)
                self.graphThread_m1.start()
                self.graphThread_m2.start()
                self.startSig.emit()
            else:
                self.startButton.setEnabled(False)
                self.configurationButton.setEnabled(True)
                if self.dev1_connected == False:
                    self.disconnectSig.emit()
                elif self.dev2_connected == False:
                    self.disconnectSig2.emit()
        else:
            self.reset_Data_n_Plot_Vars()

            self.startButton.setEnabled(False)
            self.findDeviceButton.setEnabled(False)
            self.removeDeviceButton.setEnabled(False)
    
            self.SubplotSetup()

            if self.modules == 1:
                self.graphThread = GraphThread(self.dataQueue, self.sensors, self.time_lim)
                self.graphThread.graphUpdateSig.connect(partial(self.ploter, 1))
                self.graphThread.monitTimeEndSig.connect(self.stopReading)
                self.graphThread.monitTimeEndSig.connect(self.end_message)
                self.graphThread.graphEndSig.connect(self.receiveXYData)
                self.SerialThread.readQueueSig.connect(self.graphThread.readQueue)
            elif self.modules == 2:
                self.graphThread = GraphThread(self.dataQueue2, self.sensors, self.time_lim)
                self.graphThread.graphUpdateSig.connect(partial(self.ploter, 2))               
                self.graphThread.monitTimeEndSig.connect(self.stopReading)
                self.graphThread.monitTimeEndSig.connect(self.end_message)
                self.graphThread.graphEndSig.connect(self.receiveXYData_m2)
                self.SerialThread2.readQueue2Sig.connect(self.graphThread.readQueue)
            self.stopSig.connect(self.graphThread.stop_Thread)

            self.stopButton.setEnabled(True)
            self.graphThread.start()
            self.startSig.emit()

        #Monitoring message:
        self.messagesBox.appendHtml('<p>Monitoring...</p>')
    
    
    def ploter(self, module, xpoints, ypoints):
        '''
        Plot data points in the correct plots, depending on the operation mode (module 1, module 2 or both).

         -module=1 -> only module 1 is in operation
         -module=2 -> only module 2 is in operation
         -module=31 -> Both modules operate. Plot data in the graphs corresponding to module 1
         -module=32 -> Both modules operate. Plot data in the graphs corresponding to module 2
        '''
        if module == 1:
            for i in range(len(self.ydata_plts)):
                self.plotDataItem_lst[i][0].setData(xpoints, ypoints[i], pen=pg.mkPen(self.colors_xyz[0]))
        elif module == 2:
            for i in range(len(self.ydata_plts)):
                self.plotDataItem_lst[i][0][0].setData(xpoints, ypoints[i][0], pen=pg.mkPen(self.colors_xyz[0]))
                self.plotDataItem_lst[i][1][0].setData(xpoints, ypoints[i][1], pen=pg.mkPen(self.colors_xyz[1]))
                self.plotDataItem_lst[i][2][0].setData(xpoints, ypoints[i][2], pen=pg.mkPen(self.colors_xyz[2]))
        elif module == 31:
            for i in range(4):
                self.plotDataItem_lst[i][0].setData(xpoints, ypoints[i], pen=pg.mkPen(self.colors_xyz[0]))
        elif module == 32:
            for i in range(2):
                self.plotDataItem_lst[i + 4][0][0].setData(xpoints, ypoints[i][0], pen=pg.mkPen(self.colors_xyz[0]))
                self.plotDataItem_lst[i + 4][1][0].setData(xpoints, ypoints[i][1], pen=pg.mkPen(self.colors_xyz[1]))
                self.plotDataItem_lst[i + 4][2][0].setData(xpoints, ypoints[i][2], pen=pg.mkPen(self.colors_xyz[2]))


    def receiveXYData(self, xvals, yvals):
        '''
        Receive module 1 colected data after monitoring stops.
        '''
        self.xdata = xvals
        self.ydata = yvals

    def receiveXYData_m2(self, xvals, yvals):
        '''
        Receive module 2 colected data after monitoring stops.
        '''
        self.xdata_m2 = xvals
        self.ydata_m2 = yvals


    def reset_Data_n_Plot_Vars(self):
        '''
        Reset data storage variables and plot/subplot related lists.
        '''
        self.GraphArea.canvas.clear()

        self.xdata = []
        self.xdata_m2 = []
        self.ydata = []
        self.ydata_m2 = []
        self.splotlist = []
        self.plotDataItem_lst = []
        self.xdata_plts = []
        self.ydata_plts = []

        for n in range(self.nplots):
            if self.sensors[n] == 'A' or self.sensors[n] == 'G':
                self.ydata_plts.append([[],[],[]])
                self.plotDataItem_lst.append([[],[],[]])
            else:
                self.ydata_plts.append([])
                self.plotDataItem_lst.append([])

    def SubplotSetup(self):
        '''
        Initialize and setup subplots.
        '''
        rows_cols = [[1,1],[1,2],[2,2],[2,2],[2,3],[2,3],[3,3],[3,3]]
        n_rows = rows_cols[self.nplots - 1][0]
        n_cols = rows_cols[self.nplots - 1][1]
        sens_count = 0

        for i in range(n_rows):
            for j in range(n_cols):
                sens_count += 1
                if sens_count <= self.nplots:
                    self.splotlist.append(self.GraphArea.canvas.addPlot(i, j))
                else:
                    pass

        for it in range(len(self.splotlist)):
            if self.sensors[it] == 'A':
                for i in range(3):
                    self.plot_w_legend(self.splotlist[it], self.plotDataItem_lst[it][i], self.accel_labels[i])
                self.splotlist[it].setLabel('left', self.y_labels[-2])
            elif self.sensors[it] =='G':
                for i in range(3):
                    self.plot_w_legend(self.splotlist[it], self.plotDataItem_lst[it][i], self.gyro_labels[i])
                self.splotlist[it].setLabel('left', self.y_labels[-1])
            else:
                self.plotDataItem_lst[it].append(self.splotlist[it].plot(Brush=(255,255,255)))
                self.splotlist[it].getAxis("bottom").setStyle(tickTextOffset = 5, tickTextHeight = 9)
                self.splotlist[it].setLabel('left', self.y_labels[it])
            self.splotlist[it].setLabel('bottom', 'Time [s]')

        self.show()

    def plot_w_legend(self, subplot, plot_data_item, legend):
        """Function to create the plot data items for accelerometer and gyroscope data:
        It adds legends to the multiple overlaped lines, from the variables: self.gyro_labels and self.accel_labels"""              
        subplot.addLegend(brush='w', labelTextColor='k')
        plot_data_item.append(subplot.plot(Brush=(255,255,255), name=legend))
        subplot.getAxis("bottom").setStyle(tickTextOffset = 5, tickTextHeight = 9)


    def find_device(self):
        '''
        What to do when findDeviceButton is clickked:
        - Open FindDevDlg Dialog (Dialog for serial comunication configuration)
        '''
        self.startButton.setEnabled(False)
        try:
            self.rem_devs()
        except:
            pass

        self.FindDevDlg = FindDeviceWindow()
        self.FindDevDlg.connectSig.connect(self.serThStart)
        self.FindDevDlg.connectSig2.connect(self.serTh2Start)

        # Configure find device window according to the chosen modules
        cnfg_by_module_opt = [[True,False], [False,True], [True,True]]
        for i in range(3):
            if self.modules == i + 1:
                self.FindDevDlg.brCbBox.setEnabled(cnfg_by_module_opt[i][0])
                self.FindDevDlg.portCbBox.setEnabled(cnfg_by_module_opt[i][0])
                self.FindDevDlg.connectButton.setEnabled(cnfg_by_module_opt[i][0])  

                self.FindDevDlg.brCbBox2.setEnabled(cnfg_by_module_opt[i][1])
                self.FindDevDlg.portCbBox2.setEnabled(cnfg_by_module_opt[i][1])
                self.FindDevDlg.connectButton2.setEnabled(cnfg_by_module_opt[i][1])

        self.FindDevDlg.show()

    def serThStart(self, Port, Br):
        '''
        Start a parallel thread to handle serial communication.
        '''
        self.br1 = Br
        self.port1 = Port

        self.dataQueue = queue.Queue()

        self.SerialThread = SerThread(Port,Br,self.dataQueue, self.sensors)
        self.SerialThread.ConnectSig.connect(self.HandleThConnectSig)
        self.SerialThread.readErrorSigTh1.connect(self.HandleReadErrorSigTh1)

        self.startSig.connect(self.SerialThread.startSignalRec)
        self.stopSig.connect(self.SerialThread.stopSignalRec)
        self.disconnectSig.connect(self.SerialThread.disconnectSerial)
        self.stopThreadSig.connect(self.SerialThread.stop_Thread)

        self.SerialThread.start()

    def serTh2Start(self, Port, Br):
        '''
        Start parallel thread 2 to handle serial communication from accelerometer module.
        '''
        self.br2 = Br
        self.port2 = Port

        self.dataQueue2 = queue.Queue()

        self.SerialThread2 = SerThread2(Port,Br,self.dataQueue2, self.sensors)
        self.SerialThread2.ConnectSig2.connect(self.HandleThConnectSig2)
        self.SerialThread2.readErrorSigTh2.connect(self.HandleReadErrorSigTh2)
        
        self.startSig.connect(self.SerialThread2.startSignalRec)
        self.stopSig.connect(self.SerialThread2.stopSignalRec)
        self.disconnectSig2.connect(self.SerialThread2.disconnectSerial)
        self.stopThreadSig.connect(self.SerialThread2.stop_Thread)

        self.SerialThread2.start()

    def HandleReadErrorSigTh2(self):
        '''
        '''
        self.stopReading()
        self.stopButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        self.saveSessionButton.setEnabled(False)
        self.removeDeviceButton.setEnabled(False)
        self.stop_message()
        try:
            self.rem_devs()
        except:
            pass
        self.findDeviceButton.setEnabled(True)

        QtWidgets.QMessageBox.information(self,"Message", 'Error! Something went wrong while trying to receive and read data from the vibration module. Please make sure the correct device is connected to the chosen communication port and make sure to choose baud rate matching the device.', 
        QtWidgets.QMessageBox.Ok)


    def HandleReadErrorSigTh1(self):
        '''
        '''
        self.stopReading()
        self.stopButton.setEnabled(False)
        self.nextButton.setEnabled(False)
        self.saveSessionButton.setEnabled(False)
        self.removeDeviceButton.setEnabled(False)
        self.stop_message()
        try:
            self.rem_devs()
        except:
            pass
        self.findDeviceButton.setEnabled(True)

        QtWidgets.QMessageBox.information(self,"Message", 'Error! Something went wrong while trying to receive and read data from the TPF module. Please make sure the correct device is connected to the chosen communication port and make sure to choose baud rate matching the device.', 
        QtWidgets.QMessageBox.Ok)
        
    
    def HandleThConnectSig(self, ConnectedT_F):
        '''
        '''
        if ConnectedT_F == True:
            self.messagesBox.appendHtml('<p style="color:green;">Device 1: connected.</p><p>Port: %s</p><p>Baud rate: %s</p>' %(self.port1, self.br1))
            self.startButton.setEnabled(True)
            self.removeDeviceButton.setEnabled(True)
            self.configurationButton.setEnabled(False)
            self.FindDevDlg.connectButton.setEnabled(False)
        else:
            self.messagesBox.appendHtml('<p style="color:red;">Device 1: connection failed!.</p>')
        self.dev1_connected = ConnectedT_F

    def HandleThConnectSig2(self, ConnectedT_F):
        '''
        '''
        if ConnectedT_F == True:
            self.messagesBox.appendHtml('<p style="color:green;">Device 2: connected.</p><p>Port: %s</p><p>Baud rate: %s</p>' %(self.port2, self.br2))
            self.startButton.setEnabled(True)
            self.removeDeviceButton.setEnabled(True)
            self.configurationButton.setEnabled(False)
            self.FindDevDlg.connectButton2.setEnabled(False)
        else:
            self.messagesBox.appendHtml('<p style="color:red;">Device 2: connection failed!.</p>')   
        self.dev2_connected = ConnectedT_F


    def configure(self):
        '''
        Configure:
        Selection of the modules to be connected later;
        Definition of the time interval for data recording.
        '''
        self.ModuleSelectWin = ModuleSelect()
        self.ModuleSelectWin.configSignal.connect(self.cnfg_Sig_Received)
        self.ModuleSelectWin.show()

    def cnfg_Sig_Received(self, modules, timeint):
        '''
        Store values for the modules to be connected and monitoring time interval in variables from the active main window.
        modules: int 1, 2 or 3;
        timeint: int time in seconds;
        '''
        self.config_message(modules, timeint)
        self.modules = modules
        self.time_lim = timeint
        self.findDeviceButton.setEnabled(True)
        self.sensors = [['T1','T2','P','F'],['A','G']]   

        sens_indexes_by_module_cfg = [[0],[1],[0,1]]
        for m in range(3):
            if self.modules == m + 1:
                s = 0
                sensors = []
                for i in sens_indexes_by_module_cfg[m]:
                    s += len(self.sensors[i])
                    sensors += self.sensors[i]

        self.nplots = s
        self.sensors = sensors

        for n in range(self.nplots):
            if self.sensors[n] == 'A' or self.sensors[n] == 'G':
                self.plotDataItem_lst.append([[],[],[]])
            else:
                self.plotDataItem_lst.append([]) 

    def config_message(self, modules, timeint):
        '''
        '''
        #Config message:
        self.messagesBox.appendHtml('<p>Configuration:</p>')
        if modules == 1:
            self.messagesBox.appendHtml('<p>Operation mode: TPF module (device 1)</p>')
        elif modules == 2:
            self.messagesBox.appendHtml('<p>Operation mode: Vibration module (device 2)</p>')
        elif modules == 3:
            self.messagesBox.appendHtml('<p>Operation mode: TPF (device 1) and vibration (device 2) modules</p>')
        self.messagesBox.appendHtml('<p>Monitoring time: %ds</p>' %timeint)


# The dialogue to show help about/help info:
class help_dialog(QtWidgets.QDialog, help_dialog.Ui_aboutDialog):
    '''
    '''
    def __init__(self, parent = None):
        super(help_dialog, self).__init__(parent)
        self.setupUi(self)


# The dialogue to select devices for the session:
class ModuleSelect(QtWidgets.QDialog, ModuleSelect.Ui_DeviceSelWin):
    '''
    '''
    configSignal = QtCore.pyqtSignal(int, float)
    def __init__(self, parent = None):
        super(ModuleSelect, self).__init__(parent)
        self.setupUi(self)

        self.devs = 0 # Variable to store device choice: 0 - no device selected; 1 - module 1 selected; 2 - module 2 selected; 3 - both modules selected.
        self.doneButton.clicked.connect(self.doneBtnClicked)

    def doneBtnClicked(self):
        try:
            if self.m1CBox.isChecked() == True and self.m2CBox.isChecked() == False:
                self.devs = 1
            elif self.m1CBox.isChecked() == False and self.m2CBox.isChecked() == True:
                self.devs = 2
            elif self.m1CBox.isChecked() == True and self.m2CBox.isChecked() == True:
                self.devs = 3

            self.timeint = float(self.timeIntEdit.text()) # Variable for monitoring time interval definition

            if self.devs == 0:
                QtWidgets.QMessageBox.information(self, "Message", 'At least one of the modules above must be selected to proceed.')
            elif self.timeint == 0:
                QtWidgets.QMessageBox.information(self, "Message", 'The monitoring time interval value must be greater than 0.')
            else:
                self.configSignal.emit(self.devs, self.timeint)
                self.close()

        except:
            QtWidgets.QMessageBox.information(self, "Message", 'The value for monitoring time interval must be written as either an integer or a float.')
            self.devs = 0


# Window for serial comunication setting and connection:
class FindDeviceWindow(QtWidgets.QDialog, ComSettings.Ui_comSettingsDialog):
    '''
    '''
    connectSig = QtCore.pyqtSignal(str, str)
    connectSig2 = QtCore.pyqtSignal(str, str)
    def __init__(self, parent = None):
        super(FindDeviceWindow, self).__init__(parent)
        self.setupUi(self)

        self.connectButton.clicked.connect(partial(self.connect_event, 1))
        self.connectButton2.clicked.connect(partial(self.connect_event, 2))
        self.closeButton.clicked.connect(self.close)


    def connect_event(self, dev_num):
        '''Try connecting to serial device.
        If the connection fails, the message "Connection to device dev_num failed." appears in red in the message box of the main window.
        '''
        if dev_num == 1:
            self.connect_to_Device()
        elif dev_num == 2:
            self.connect_to_Device2()

    def connect_to_Device(self):
        '''Emit a signal for connection to device 1.
        The signal also carries information regarding the port and baudrate selected by the user for the connection.
        '''
        fullportname = self.portCbBox.currentText()
        port = fullportname.split(' ')[0]
        br = self.brCbBox.currentText()
        self.connectSig.emit(port, br)

    def connect_to_Device2(self):
        '''
        Emit a signal for connection to device 2.
        The signal also carries information regarding the port and baudrate selected by the user for the connection.
        '''
        fullportname = self.portCbBox2.currentText()
        port = fullportname.split(' ')[0]
        br = self.brCbBox2.currentText()
        self.connectSig2.emit(port, br)



# Serial thread: #########################################################################
##########################################################################################
# A separate class is created for managing the serial thread, in parallel with the GUI operation:
class SerThread(QtCore.QThread):
    ConnectSig = QtCore.pyqtSignal(bool)
    readQueueSig = QtCore.pyqtSignal()
    readErrorSigTh1 = QtCore.pyqtSignal()

    def __init__(self, port, br, dataQueue, sensors, parent = None):
        super(QtCore.QThread, self).__init__()

        self.dataQueue = dataQueue
        self.port = port
        self.br = br
        self.IsConnected = False
        self.startsigrec = False
        self.stopsigrec = False
        self.stopThread = False
        self.data = ''
        self.n_sensors = len(sensors)
        self.sensors = sensors

    @QtCore.pyqtSlot()
    def stop_Thread(self):
        '''
        '''
        self.stopThread = True
        
    @QtCore.pyqtSlot()
    def disconnectSerial(self):
        '''
        '''
        if self.IsConnected == True:
            self.ser.close()
            self.IsConnected = False
        else:
            pass

    @QtCore.pyqtSlot()
    def stopSignalRec(self):
        '''
        '''
        self.stopsigrec = True

    @QtCore.pyqtSlot()
    def startSignalRec(self):
        '''
        '''
        self.start = perf_counter()
        self.startsigrec = True
        self.stopsigrec = False

    def ConnectSerial(self):
        '''
        '''
        try:
            self.ser = serial.Serial(self.port, self.br, timeout=0.1)
            self.ConnectSig.emit(True)
            self.IsConnected = True
            return True
        except:
            self.ConnectSig.emit(False)
            self.IsConnected = False
            return False

    def Timer(self, start):
        '''
        Counts time since start.

        start: float
        returns end: float
        '''
        current = perf_counter()
        return current - start

    def Read_amd_Process_serData(self, sensors=[], ydata_lst=[]):
        '''
        '''
        serData = self.ser.readline()
        msg = serData.decode('utf-8')
        msg = msg.replace('\r\n','')
        msg_lst = msg.split(',')

        for i in range(len(sensors)):
            ydata_lst.append(float(msg_lst[i]))
        return ydata_lst

    def run(self):
        while self.stopThread == False:
            if self.IsConnected == False:
                self.IsConnected = self.ConnectSerial()
            else:
                pass
            
            if self.IsConnected == False:
                self.stopThread = True
            else:
                while self.startsigrec == False:
                    sleep(0.01)
                if self.startsigrec:
                    self.ser.write("s".encode('utf-8'))

                try:
                    while not self.stopsigrec:
                        y_lst = []
                        y_lst = self.Read_amd_Process_serData(['T1','T2','P','F'], y_lst)

                        msgLst = []
                        for el in y_lst:
                            msgLst.append(el)
                        
                        x = self.Timer(self.start)
                        msgLst.append(x)
                        if self.stopsigrec == False:
                            self.dataQueue.put(msgLst, timeout=0.01)
                            self.readQueueSig.emit()

                        while not (self.ser.in_waiting > 0):
                            sleep(0.001)
                            if self.stopsigrec == True:
                                break
                except:
                    self.readErrorSigTh1.emit()
                    break
                
                self.ser.write("p".encode('utf-8'))
                self.startsigrec = False
                self.stopsigrec = False


# A separate class is created for managing the second serial thread, in parallel with the main GUI and first thread operation:
class SerThread2(QtCore.QThread):
    ConnectSig2 = QtCore.pyqtSignal(bool)
    readQueue2Sig = QtCore.pyqtSignal()
    readErrorSigTh2 = QtCore.pyqtSignal()

    def __init__(self, port, br, dataQueue, sensors, parent = None):
        super(QtCore.QThread, self).__init__()

        self.dataQueue = dataQueue
        self.port = port
        self.br = br
        self.IsConnected = False
        self.startsigrec = False
        self.stopsigrec = False
        self.stopThread = False
        self.data = ''
        self.n_sensors = len(sensors)
        self.sensors = sensors

    @QtCore.pyqtSlot()
    def stop_Thread(self):
        '''
        '''
        self.stopThread = True

    @QtCore.pyqtSlot()
    def disconnectSerial(self):
        '''
        '''
        if self.IsConnected == True:
            self.ser.close()
            self.IsConnected = False
        else:
            pass

    @QtCore.pyqtSlot()
    def stopSignalRec(self):
        '''
        '''
        self.stopsigrec = True

    @QtCore.pyqtSlot()
    def startSignalRec(self):
        '''
        '''
        self.start = perf_counter()
        self.startsigrec = True
        self.stopsigrec = False

    def ConnectSerial(self):
        '''
        '''
        try:
            self.ser = serial.Serial(self.port, self.br, timeout=0.1)
            self.ConnectSig2.emit(True)
            self.IsConnected = True
            return True
        except:
            self.ConnectSig2.emit(False)
            self.IsConnected = False
            return False

    def Timer(self, start):
        '''
        Counts time since start.

        start time: float
        returns the time in seconds (s) elapsed since start: float
        '''
        current = perf_counter()
        return current - start

    def Read_amd_Process_serData(self, sensors=[], ydata_lst=[]):
        '''
        '''
        serData = self.ser.readline()
        msg = serData.decode('utf-8')
        msg = msg.replace('\n','')
        msg_lst = msg.split(',')

        for i in range(len(sensors)):
            ydata_lst.append(float(msg_lst[i]))
        return ydata_lst

    def run(self):
        while self.stopThread == False:
            if self.IsConnected == False:
                self.IsConnected = self.ConnectSerial()
            else:
                pass
            
            if self.IsConnected == False:
                self.stopThread = True
            else:
                while self.startsigrec == False:
                    sleep(0.01)
                if self.startsigrec:
                    self.ser.write("s".encode('utf-8'))

                try:
                    while not self.stopsigrec:
                        y_lst = []
                        y_lst = self.Read_amd_Process_serData(['Ax', 'Ay', 'Az', 'Gx','Gy', 'Gz'], y_lst)

                        msgLst = []
                        for el in y_lst:
                            msgLst.append(el)
                        
                        x = self.Timer(self.start)
                        msgLst.append(x)
                        if self.stopsigrec == False:
                            self.dataQueue.put(msgLst, timeout=0.01)
                            self.readQueue2Sig.emit()

                        while not (self.ser.in_waiting > 0):
                            sleep(0.001)
                            if self.stopsigrec == True:
                                break
                except:
                    self.readErrorSigTh2.emit()
                    break

                self.ser.write("p".encode('utf-8'))
                self.startsigrec = False
                self.stopsigrec = False



# Graph thread(s): #######################################################################
##########################################################################################
# Threads to handle graph updates:
class GraphThread(QtCore.QThread):
    graphEndSig = QtCore.pyqtSignal(list, list) #Signal to be sent to Main Window when this thread ends. It will carry xdata and ydata lists.
    monitTimeEndSig = QtCore.pyqtSignal() #When the monitoring time limit is reached, this signal is emited to trigger stop reading procedure in main GUI.
    graphUpdateSig = QtCore.pyqtSignal(list, list) #Signal to send to the main GUI thread to update graph. carries lists with x and y values for the graph.

    def __init__(self, dataQueue, sensors, read_period, parent = None):
        super(QtCore.QThread, self).__init__()

        self.readQSigRec = False
        self.stopThread = False
        self.dataQueue = dataQueue
        self.read_period = read_period
        self.xdata = []
        self.ydata = []
        self.xdata_plts = []
        self.ydata_plts = []
        self.n_disp_data_pts = 20 #Maximum number of data points to be plotted simutaneously in each plot.
        self.n_sensors = len(sensors)
        self.sensors = sensors
        self.GraphTime0 = 0
        self.update_interval = 0.15 #seconds

        try:
            val_to_dump = 0
            if self.dataQueue.unfinished_tasks > 0:
                for task in range(self.dataQueue.unfinished_tasks):
                    val_to_dump=self.dataQueue.get(timeout=0.01)
        except:
            pass

        for n in range(self.n_sensors):
            if self.sensors[n] == 'A' or self.sensors[n] == 'G':
                self.ydata_plts.append([[],[],[]])
            else:
                self.ydata_plts.append([])

    @QtCore.pyqtSlot()
    def readQueue(self):
        '''
        '''
        self.readQSigRec = True

    @QtCore.pyqtSlot()
    def stop_Thread(self):
        '''
        '''
        self.stopThread = True

    def update_graph(self, new_x, new_y, plot_T_F):
        '''
        Update subplots with new y and x values.
        '''
        #UPDATE XY LISTS:
        if len(self.xdata_plts) <= self.n_disp_data_pts:
            #just append new x element
            self.xdata_plts.append(new_x)
        else:
            #drop off first x element, append a new one
            self.xdata_plts = self.xdata_plts[1:] + [new_x]
    
        for i in range(len(self.ydata_plts)):
            if self.sensors[i] == 'A':
                for j in range(3):
                    if len(self.ydata_plts[i][j]) <= self.n_disp_data_pts:
                        #just append new y element
                        self.ydata_plts[i][j].append(new_y[j])
                    else:
                        #drop off first y element, append a new one
                        self.ydata_plts[i][j] = self.ydata_plts[i][j][1:] + [new_y[j]]
            elif self.sensors[i] == 'G':
                j=0
                for j in range(3):
                    if len(self.ydata_plts[i][j]) <= self.n_disp_data_pts:
                        #just append new y element
                        self.ydata_plts[i][j].append(new_y[j + 3]/1000)
                    else:
                        #drop off first y element, append a new one
                        self.ydata_plts[i][j] = self.ydata_plts[i][j][1:] + [new_y[j + 3]/1000]
            else:
                if len(self.ydata_plts[i]) <= self.n_disp_data_pts:
                    #just append new y element
                    self.ydata_plts[i].append(new_y[i])
                else:
                    #drop off first y element, append a new one
                    self.ydata_plts[i] = self.ydata_plts[i][1:] + [new_y[i]]
    
        #UPDATE GRAPH:
        if plot_T_F == True:
            self.graphUpdateSig.emit(self.xdata_plts, self.ydata_plts)

    def run(self):
        t0 = perf_counter()
        while self.stopThread == False:
            if self.readQSigRec == True:

                plot_T_F = False
                t1 = perf_counter()
                timer= t1 - t0

                self.serData = self.dataQueue.get(timeout=0.01)
                self.xdata.append(self.serData[-1])

                ypoints = []
                for i in range(len(self.serData) - 1):
                    ypoints.append(self.serData[i])
                self.ydata.append(ypoints)
                
                if timer >= self.update_interval:
                    t0 = perf_counter()
                    plot_T_F = True

                self.update_graph(self.serData[-1], ypoints, plot_T_F)
                self.readQSigRec = False

            sleep(0.001)

            if len(self.xdata) > 0 and self.xdata[-1] > self.read_period:
                self.monitTimeEndSig.emit()
                self.stopThread = True
        
        self.graphEndSig.emit(self.xdata, self.ydata)



pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

app = QtWidgets.QApplication(sys.argv)
form = MainWindow()
form.showMaximized()
app.exec_()

##########################################################################################
################################## The End ###############################################
##########################################################################################