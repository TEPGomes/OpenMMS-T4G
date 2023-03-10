# -*- coding: utf-8 -*-

# Created by: PyQt5 UI code generator 5.9.2

from PyQt5 import QtCore, QtGui, QtWidgets

import icons_rc

class Ui_DeviceSelWin(object):
    def setupUi(self, DeviceSelWin):
        DeviceSelWin.setObjectName("DeviceSelWin")
        DeviceSelWin.setWindowModality(QtCore.Qt.NonModal)
        DeviceSelWin.resize(219, 175)
        DeviceSelWin.setMinimumSize(QtCore.QSize(0, 0))
        DeviceSelWin.setMaximumSize(QtCore.QSize(219, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/T4G.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        DeviceSelWin.setWindowIcon(icon)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(DeviceSelWin)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtWidgets.QLabel(DeviceSelWin)
        self.label.setMinimumSize(QtCore.QSize(0, 0))
        self.label.setMaximumSize(QtCore.QSize(16777215, 25))
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.frame = QtWidgets.QFrame(DeviceSelWin)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.m1CBox = QtWidgets.QCheckBox(self.frame)
        self.m1CBox.setObjectName("m1CBox")
        self.verticalLayout.addWidget(self.m1CBox)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.m2CBox = QtWidgets.QCheckBox(self.frame)
        self.m2CBox.setObjectName("m2CBox")
        self.verticalLayout_3.addWidget(self.m2CBox)
        self.label_3 = QtWidgets.QLabel(self.frame)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_3.addWidget(self.label_3)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addWidget(self.frame)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(DeviceSelWin)
        self.label_4.setTextFormat(QtCore.Qt.AutoText)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.timeIntEdit = QtWidgets.QLineEdit(DeviceSelWin)
        self.timeIntEdit.setMinimumSize(QtCore.QSize(20, 20))
        self.timeIntEdit.setMaximumSize(QtCore.QSize(30, 25))
        self.timeIntEdit.setObjectName("timeIntEdit")
        self.horizontalLayout_2.addWidget(self.timeIntEdit)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.doneButton = QtWidgets.QPushButton(DeviceSelWin)
        self.doneButton.setMinimumSize(QtCore.QSize(0, 25))
        self.doneButton.setMaximumSize(QtCore.QSize(16777215, 25))
        self.doneButton.setObjectName("doneButton")
        self.horizontalLayout_2.addWidget(self.doneButton)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(DeviceSelWin)
        QtCore.QMetaObject.connectSlotsByName(DeviceSelWin)

    def retranslateUi(self, DeviceSelWin):
        _translate = QtCore.QCoreApplication.translate
        DeviceSelWin.setWindowTitle(_translate("DeviceSelWin", "Select devices"))
        self.label.setText(_translate("DeviceSelWin", "Please select the devices to be connected to the system."))
        self.m1CBox.setText(_translate("DeviceSelWin", "T, P, F module"))
        self.label_2.setText(_translate("DeviceSelWin", "Arduino-based acquisition module. It will transmit data from two temperature sensors, a pressure sensor and a force sensor."))
        self.m2CBox.setText(_translate("DeviceSelWin", "A, G module"))
        self.label_3.setText(_translate("DeviceSelWin", "Microchip-based acquisition module. It will transmit data from an accelerometer and gyroscope sensor plate."))
        self.label_4.setText(_translate("DeviceSelWin", "Maximum monitoring time (s):"))
        self.doneButton.setText(_translate("DeviceSelWin", "Done"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DeviceSelWin = QtWidgets.QDialog()
    ui = Ui_DeviceSelWin()
    ui.setupUi(DeviceSelWin)
    DeviceSelWin.show()
    sys.exit(app.exec_())

