#!/usr/bin/env python3

# -*- coding: utf-8 -*-
#
# Copyright 2019 by Heiko Schäfer <heiko@rangun.de>
#
# This file is part of DiskFit.
#
# DiskFit is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# DiskFit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with DiskFit.  If not, see <http://www.gnu.org/licenses/>.
#

from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QProcess
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMainWindow
from .models.outputmodel import OutputModel
from .models.inputmodel import InputModel
from .mainwindow import mainwindow
from shlex import quote
import sys
import re


class MainWindow(QMainWindow):

    gui_restored = False

    __ui = None
    __proc1 = QProcess()
    __proc2 = QProcess()
    __proc3 = QProcess()
    __inputModel = None
    __outputModel = None
    __diskfit = "/usr/bin/diskfit"
    __diskfitProgress = None
    __lastResult = list()
    __resultBuf = ""
    __statusBar = None

    def __init__(self):

        super(MainWindow, self).__init__()

        self.__ui = mainwindow.Ui_MainWindow()
        self.__ui.setupUi(self)

        self.__diskfitProgress = QProgressBar()
        self.__diskfitProgress.setMinimum(0)
        self.__diskfitProgress.setMaximum(100)
        self.__diskfitProgress.setValue(0)

        self.__statusBar = self.statusBar()
        self.__statusBar.addPermanentWidget(self.__diskfitProgress)

        self.__inputModel = InputModel(self.__ui.table_input,
                                       self.__ui.label_inputSummary,
                                       self.__ui.action_Start,
                                       self.__ui.action_SelectAll,
                                       self.__ui.action_inputRemoveAll,
                                       self.__ui.button_clearInput)

        self.__ui.table_input.setModel(self.__inputModel)
        self.__ui.table_input.header(). \
            setSectionResizeMode(0, QHeaderView.Stretch)
        self.__ui.table_input.header(). \
            setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.__outputModel = OutputModel(self.__ui.table_output,
                                         self.__ui.label_runSummary,
                                         self.__inputModel)

        self.__ui.table_output.setModel(self.__outputModel)
        self.__ui.table_output.header(). \
            setSectionResizeMode(0, QHeaderView.Stretch)
        self.__ui.table_output.header(). \
            setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.__ui.table_output.header(). \
            setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.__ui.table_output.header(). \
            setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.__ui.button_InputAdd.clicked.connect(self.__inputModel.addFiles)
        self.__ui.button_clearInput.clicked. \
            connect(self.__inputModel.removeAll)
        self.__ui.button_ListRemove.clicked. \
            connect(self.__inputModel.removeFiles)
        self.__ui.table_input.header().sectionClicked.connect(self.sortInput)
        self.__ui.table_input.selectionModel().selectionChanged. \
            connect(self.inputSelectionChanged)
        self.__ui.combo_target.currentIndexChanged.connect(self.targetChanged)
        self.__ui.action_Start.triggered.connect(self.start)
        self.__ui.actionAbout.triggered.connect(self.about)

        self.readSettings()
        self.getTargets()

    def getTargets(self):
        self.__proc1.errorOccurred.connect(self.error)
        self.__proc1.readyReadStandardOutput.connect(self.targetsAvailable)
        self.__proc1.start(self.__diskfit, list(), QProcess.ReadOnly)
        self.__proc1.waitForStarted(-1)

    def closeEvent(self, evt):
        settings = QSettings()
        settings.setValue("bytes", self.__ui.spin_bytes.value())
        settings.setValue("target", self.__ui.combo_target.currentIndex())
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        super().closeEvent(evt)

    def readSettings(self):
        settings = QSettings()
        g_ = settings.value("geometry")
        if g_ is not None:
            self.restoreGeometry(g_)
            self.gui_restored |= True
        s_ = settings.value("windowState")
        if s_ is not None:
            self.restoreState(s_)
            self.gui_restored |= True

    @pyqtSlot()
    def about(self):
        QMessageBox.about(self, self.tr("About"),
                          QApplication.applicationName() + " " +
                          QApplication.applicationVersion() + "\n" +
                          self.tr("A simple disk fit calculator (GUI)") +
                          "\n\n(c) 2019 by Heiko Schäfer <heiko@rangun.de>")

    @pyqtSlot()
    def start(self):
        self.__ui.action_Start.setEnabled(False)
        self.__ui.actionStop.setEnabled(True)
        self.__ui.group_InputFiles.setEnabled(False)
        self.__ui.group_profile.setEnabled(False)

        args_ = list()

        args_.append(self.__ui.combo_target.currentText())

        for file_ in self.__inputModel.files():
            args_.append(quote(file_.text()))

        self.__proc3.errorOccurred.connect(self.error)
        self.__proc3.readyReadStandardError.connect(self.progressAvailable)
        self.__proc3.readyReadStandardOutput.connect(self.resultAvailable)
        self.__proc3.finished.connect(self.finished)

        self.__statusBar.showMessage(self.tr("Calculating for ") +
                                     str(self.__inputModel.rowCount()) +
                                     self.tr(" files …"))

        self.__proc3.start(self.__diskfit, args_, QProcess.ReadOnly)
        self.__proc3.waitForStarted()

        self.__lastResult.clear()

        self.__ui.actionStop.triggered.connect(self.__proc3.terminate)

    @pyqtSlot(QProcess.ProcessError)
    def error(self, err):
        if err == QProcess.FailedToStart:
            QMessageBox.critical(None, self.tr("Error"),
                                 self.tr("Failed to launch " + self.__diskfit))
        self.finished(0, QProcess.NormalExit)

    @pyqtSlot(int, QProcess.ExitStatus)
    def finished(self, ec, es):

        if not QProcess.CrashExit or ec == 0:
            for r_ in self.__resultBuf.splitlines(False):
                r_match_ = r_rex.search(r_)
                if r_match_:
                    self.__lastResult.append((r_match_.group(1),
                                              r_match_.group(2),
                                              r_match_.group(3),
                                              r_match_.group(4)))

            self.__statusBar.showMessage(self.tr("Processing result …"))
            self.__outputModel.setLastResult(self.__lastResult)
            self.__statusBar.clearMessage()
        else:
            self.__statusBar.showMessage(self.tr("Calculation interrupted"),
                                         5000)

        self.__resultBuf = ""

        self.__ui.action_Start.setEnabled(True)
        self.__ui.actionStop.setEnabled(False)
        self.__ui.group_InputFiles.setEnabled(True)
        self.__ui.group_profile.setEnabled(True)
        self.__diskfitProgress.setValue(0)

    @pyqtSlot()
    def progressAvailable(self):
        for p_ in str(self.__proc3.readAllStandardError().data().
                      decode("utf-8")).splitlines(False):
            p_match_ = p_rex.search(p_)
            if p_match_:
                self.__diskfitProgress.setValue(int(p_match_.group(2)))

    @pyqtSlot()
    def resultAvailable(self):
        self.__resultBuf += self.__proc3.readAllStandardOutput().data(). \
            decode("utf-8")

    @pyqtSlot()
    def targetsAvailable(self):

        for t_ in reversed(str(self.__proc1.readAllStandardOutput().data().
                               decode("utf-8")).splitlines(False)):

            t_match_ = t_rex.match(t_)

            if t_match_ is not None:

                l_ = list()
                m_ = t_match_.group(1)
                l_.append(m_)

                self.__ui.combo_target.insertItem(-1, m_)
                self.__ui.combo_target.setCurrentIndex(0)

                self.__proc2.readyReadStandardOutput. \
                    connect(self.targetSizeAvailable)

                self.__proc2.start(self.__diskfit, l_, QProcess.ReadOnly)
                self.__proc2.waitForFinished(-1)

        settings = QSettings()
        t_ = settings.value("target")
        if t_ is not None:
            self.__ui.combo_target.setCurrentIndex(int(t_))
            if self.__ui.combo_target.itemData(int(t_)) is None:
                self.__ui.spin_bytes.setValue(float(settings.value("bytes")))

    @pyqtSlot()
    def targetSizeAvailable(self):
        s_ = str(self.__proc2.readAllStandardOutput().data().
                 decode("utf-8")).splitlines(False)
        if len(s_):
            self.__ui.combo_target.setItemData(0, float(s_[0]))
        self.targetChanged(0)

    @pyqtSlot(int)
    def targetChanged(self, idx):
        d_ = self.__ui.combo_target.itemData(idx)
        if d_ is not None:
            self.__ui.spin_bytes.setValue(d_)
            self.__ui.spin_bytes.setEnabled(False)
        else:
            self.__ui.spin_bytes.setEnabled(True)

    @pyqtSlot()
    def inputSelectionChanged(self):
        en_ = self.__ui.table_input.selectionModel().hasSelection()
        self.__ui.button_ListRemove.setEnabled(en_)
        self.__ui.action_InputRemove.setEnabled(en_)

    @pyqtSlot(int)
    def sortInput(self, idx):
        self.__ui.table_input.header().setSortIndicatorShown(True)


def main(args=None):
    app = QApplication(sys.argv)

    app.setApplicationName("QDiskFit")
    app.setApplicationVersion("2.0.2.6")
    app.setApplicationDisplayName(app.applicationName() + " " +
                                  app.applicationVersion())
    app.setOrganizationDomain("rangun.de")
    app.setOrganizationName("diskfit")

    dw = QDesktopWidget()

    my_mainWindow = MainWindow()
    if not my_mainWindow.gui_restored:
        my_mainWindow.resize(dw.width() * 0.7, dw.height() * 0.7)
    my_mainWindow.show()

    sys.exit(app.exec_())


t_rex = re.compile('\s+([^\s]+).*')
p_rex = re.compile('(Computing for \d+ files: (\d+)% \.\.\.)+.*')
r_rex = re.compile('\[([^\]]*)\]:([^ ]+) = ([^\(]+) \(([0-9\.%]*)\)')

if __name__ == "__main__":
    main()
