# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qdiskfit/mainwindow/progress.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_progressWidget(object):
    def setupUi(self, progressWidget):
        progressWidget.setObjectName("progressWidget")
        progressWidget.resize(131, 32)
        self.hboxlayout = QtWidgets.QHBoxLayout(progressWidget)
        self.hboxlayout.setContentsMargins(0, 0, 0, 0)
        self.hboxlayout.setSpacing(0)
        self.hboxlayout.setObjectName("hboxlayout")
        self.stopButton = QtWidgets.QPushButton(progressWidget)
        self.stopButton.setFlat(True)
        self.stopButton.setObjectName("stopButton")
        self.hboxlayout.addWidget(self.stopButton)
        self.progressBar = QtWidgets.QProgressBar(progressWidget)
        self.progressBar.setObjectName("progressBar")
        self.hboxlayout.addWidget(self.progressBar)
        self.hboxlayout.setStretch(1, 1)

        self.retranslateUi(progressWidget)
        QtCore.QMetaObject.connectSlotsByName(progressWidget)

    def retranslateUi(self, progressWidget):
        pass


