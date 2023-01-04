from PyQt5 import QtCore, QtGui, QtWidgets

import icons_rc

class Ui_aboutDialog():
    def setupUi(self, aboutDialog):

        icon = QtGui.QIcon()
        iconpath = ":/icons/T4G.png"
        text = '<h1>General information </h1>            <p align="justify">This appliication was created in the context of the mobilizing project TOOLING4G - Advanced tools for smart manufacturing. It is a low-cost software alternative to commercially available bespoke mould monitoring systems, intended for research and development purposes. </p>      <h1>System description</h1> <h2>Hardware</h2>   <p align="justify">There are two sensor modules which can be used with the current version of the software:</p> <ul><li>Module 1 - Dedicated to the acquisition of data from two temperature sensors, one mould cavity pressure sensor and a force sensor.</li> <li>Module 2 - Dedicated to the acquisition of vibration data through an inertial module with a 3D accelerometer and a 3D gyroscope.</li></ul> <p align="justify">In each module, a microcontroller receives sensor readings and sends the data via USB to the computer.</p> <p align="justify">The modules can be monitored individually or simultaneously. The program is not guaranteed to work correctly with modules different from the listed above.</p>    <h2>User interface</h2>  <p align="justify">The various windows, dialogs and button functionalities are listed below:</p> <ul><p align="justify"><li>Main window:</p> <p align="justify">The main window is divided into three areas. On the top section are the buttons for program control. The central area is reserved for display of the plots with data from sensors. On the bottom of the window, status and event messages are conveyed to the user.</p> <p align="justify">Buttons:</p> <p align="justify"><ul><li>Configuration - When clicked, shows the "Select Devices" window. </li><li>Find device - Shows the "Serial Port Communication Settings" window.</li> <li>Start - Starts the monitoring session.</li> <li>Next - Is used to start a new monitoring session using the already connected devices with the same configuration of the previous session.</li> <li>Stop - Allows the user to stop the session before the maximum monitoring time is reached. Data received until this button is clicked can still be saved.</li> <li>Remove Devices - Disconnects all the connected devices, allowing the user to change the configuration for further sessions.</li> <li>Save session - Shows the "Save Settings as:" dialog.</li> <li>Exit - This button can be clicked to leave and close the program. When clicked, a confirmation message is shown, giving an opportunity for the user to go back and save any unsaved data.</li></ul></p><p align="justify"><li>Select Devices window:</p><p align="justify">In this window, the user has to choose either one of the hardware modules or both, as well as setting the maximum monitoring time for the session in seconds. The value for monitoring time should be an integer. If a valid decimal number is inserted, the value will be rounded down. After configuring these settings, the done button can be clicked. If no device is selected, monitoring time has not been defined or is not a valid integer or decimal number, an error message is shown upon clicking the done button.</p><p align="justify">Buttons:</p><p align="justify"><ul><li>Done - Sets the devices configurations and monitoring time.</li></ul></li></p><p align="justify"><li>Serial Port Communication Settings window:</p><p align="justify">In this window it is possible to select the port and baud rate for the connection(s) to the device(s), as well as initiating those connection(s). Make sure to connect module 1 with the settings to the left of the user and module 2 with the ones to the right. Otherwise, either an error message is shown when the start button is clicked or monitoring starts, but data is not displayed and saved correctly.</p><p align="justify">Buttons:</p><p align="justify"><ul><li>Connect - The connect button to the left of the user starts the serial communication with module 1 (device 1). The connect button to the right of the user starts the serial communication with module 2 (device 2). Both the connections are started according to the settings specified in this window.</li></ul></p></li><p align="justify"><li>Save Settings dialog:</p><p align="justify">To save the session data, the user must first select a folder path and file name in this dialog.</p><p align="justify">Buttons:</p><p align="justify"><ul><li>Save - Save data as a .csv file in the specified folder.</li><li>Cancel - Cancel the saving operation. Closes the dialog without saving.</li></ul></li></ul></p>   <h2>Operating system requirements</h2>    <p align="justify">The application was originally developed and tested in Windows 10 only. Compatibility with different versions or alternative operating systems is not guaranteed for this version of the software.</p>'
        

        aboutDialog.setObjectName("aboutDialog")
        aboutDialog.resize(700,500)
        icon.addPixmap(QtGui.QPixmap(iconpath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        aboutDialog.setWindowIcon(icon)

        self.verticalLayout = QtWidgets.QVBoxLayout(aboutDialog)
        self.verticalLayout.setContentsMargins(10,10,10,10)

        self.aboutText = QtWidgets.QTextEdit(aboutDialog)
        self.aboutText.setObjectName("aboutText")
        self.aboutText.setReadOnly(True)
        self.aboutText.setStyleSheet("border: 1px solid white;")
        self.aboutText.insertHtml(text)

        self.verticalLayout.addWidget(self.aboutText)    

        self.retranslateUi(aboutDialog)

        QtCore.QMetaObject.connectSlotsByName(aboutDialog)
    
    def retranslateUi(self, aboutDialog):
        wintitle = "About..."
        _translate = QtCore.QCoreApplication.translate
        aboutDialog.setWindowTitle(_translate("aboutDialog", wintitle))
        

if __name__=="__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    aboutDialog = QtWidgets.QDialog()
    ui = Ui_aboutDialog()
    ui.setupUi(aboutDialog)
    aboutDialog.show()
    sys.exit(app.exec_())