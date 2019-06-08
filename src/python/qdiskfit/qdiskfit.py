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

from PyQt5.QtCore import QT_TR_NOOP
from PyQt5.QtCore import QTranslator
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QProcess
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import qDebug
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QTime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QActionGroup
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QMenu
from .util.langcenv import LangCProcessEnvironment
from .models.outputmodel import OutputModel
from .models.inputmodel import InputModel
from .profileedit import ProfileEdit
from .mainwindow import mainwindow
from .util.keyfile import Keyfile
from shlex import quote
from .site import Site
import time
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
    __diskfit = Site().get("diskfitPath", "/usr/bin/diskfit")
    __diskfitProgress = None
    __lastResult = list()
    __resultBuf = ""
    __statusBar = None
    __runningTime = None
    __keyfile = None
    __saveTarget = True

    def __init__(self):

        super(MainWindow, self).__init__()

        df_env_ = LangCProcessEnvironment().env()
        df_env_.remove("DISKFIT_STRIPDIR")

        self.__proc1.setProcessEnvironment(df_env_)
        self.__proc2.setProcessEnvironment(df_env_)
        self.__proc3.setProcessEnvironment(df_env_)

        self.__ui = mainwindow.Ui_MainWindow()
        self.__ui.setupUi(self)

        self.__diskfitProgress = QProgressBar()
        self.__diskfitProgress.setMinimum(0)
        self.__diskfitProgress.setMaximum(100)
        self.__diskfitProgress.setValue(0)

        self.__statusBar = self.statusBar()
        self.__statusBar.addPermanentWidget(self.__diskfitProgress)

        self.__keyfile = Keyfile()

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

        self.__ui.table_input. \
            customContextMenuRequested.connect(self.inputContextRequested)

        self.__outputModel = OutputModel(self.__ui.table_output,
                                         self.__ui.label_runSummary,
                                         self.__inputModel)

        self.__ui.table_output.setModel(self.__outputModel)

        self.__ui.table_output.header(). \
            setContextMenuPolicy(Qt.CustomContextMenu)
        self.__ui.table_output.header(). \
            customContextMenuRequested.connect(self.outputOrder)

        self.__ui.table_output.header(). \
            setSectionResizeMode(0, QHeaderView.Stretch)
        self.__ui.table_output.header(). \
            setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.__ui.table_output.header(). \
            setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.__ui.table_output.header(). \
            setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.__outputModel.modelSaveable. \
            connect(self.__ui.action_Save.setEnabled)
        self.__ui.action_Save.triggered.connect(self.__outputModel.saveModel)

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
        self.__ui.action_diffTarget.triggered.connect(self.diffTarget)

        self.__outputModel.resultReady.connect(self.resultReady)

        self.__ui.actionProfileeditor.triggered.connect(self.editProfile)

        self.readSettings()
        self.getTargets()

    def getTargets(self):
        self.__proc1.errorOccurred.connect(self.error)
        self.__proc1.readyReadStandardOutput.connect(self.targetsAvailable)
        self.__proc1.start(self.__diskfit, list(), QProcess.ReadOnly)

        while self.__ui.combo_target.count() > 1:
            self.__ui.combo_target.removeItem(0)

        self.__proc1.waitForStarted(-1)

    def closeEvent(self, evt):

        settings = QSettings()

        if self.__saveTarget:
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

    @pyqtSlot(QPoint)
    def inputContextRequested(self, pos):

        globalPos = self.__ui.table_input.mapToGlobal(pos)

        menu_ = QMenu()

        menu_.addAction(self.__ui.action_InputAdd)
        menu_.addAction(self.__ui.action_InputRemove)
        menu_.addAction(self.__ui.action_inputRemoveAll)
        menu_.addSeparator()
        menu_.addAction(self.__ui.action_SelectAll)
        menu_.addSeparator()
        menu_.addAction(self.__ui.action_diffTarget)

        menu_.exec_(globalPos)

    @pyqtSlot(QPoint)
    def outputOrder(self, pos):

        settings_ = QSettings()

        globalPos = self.__ui.table_output.header().mapToGlobal(pos)

        menu = QMenu()

        atit_ = QAction(self.tr("Sort by title"))
        atit_.setSeparator(True)
        asiz_ = QAction(self.tr("Sort by size"))
        asiz_.setSeparator(True)

        atas_ = QAction(self.tr("ascending"))
        atas_.setCheckable(True)
        atas_.setChecked(int(settings_.value("resultSort", 0)) == 0)
        atds_ = QAction(self.tr("descending"))
        atds_.setCheckable(True)
        atds_.setChecked(int(settings_.value("resultSort", 0)) == 1)
        asas_ = QAction(self.tr("ascending"))
        asas_.setCheckable(True)
        asas_.setChecked(int(settings_.value("resultSort", 0)) == 2)
        asds_ = QAction(self.tr("descending"))
        asds_.setCheckable(True)
        asds_.setChecked(int(settings_.value("resultSort", 0)) == 3)

        agrp_ = QActionGroup(menu)
        agrp_.addAction(atit_)
        agrp_.addAction(atas_)
        agrp_.addAction(atds_)
        agrp_.addAction(asiz_)
        agrp_.addAction(asas_)
        agrp_.addAction(asds_)

        menu.addActions(agrp_.actions())

        selectedItem = menu.exec_(globalPos)

        if selectedItem:
            if selectedItem is atas_:
                settings_.setValue("resultSort", 0)
            elif selectedItem is atds_:
                settings_.setValue("resultSort", 1)
            elif selectedItem is asas_:
                settings_.setValue("resultSort", 2)
            else:
                settings_.setValue("resultSort", 3)
            self.__outputModel.applyResult()

    @pyqtSlot()
    def about(self):
        QMessageBox.about(self, self.tr("About"),
                          QApplication.applicationName() + " " +
                          QApplication.applicationVersion() + "\n" +
                          self.tr("A simple disk fit calculator (GUI)") +
                          "\n\n(c) 2019 by Heiko Schäfer <heiko@rangun.de>")

    @pyqtSlot()
    def start(self):
        self.__ui.actionProfileeditor.setEnabled(False)
        self.__ui.action_SelectAll.setEnabled(False)
        self.__ui.action_inputRemoveAll.setEnabled(False)
        self.__ui.action_InputRemove.setEnabled(False)
        self.__ui.action_InputAdd.setEnabled(False)
        self.__ui.action_Start.setEnabled(False)
        self.__ui.actionStop.setEnabled(True)
        self.__ui.action_diffTarget.setEnabled(False)
        self.__ui.group_InputFiles.setEnabled(False)
        self.__ui.group_profile.setEnabled(False)

        args_ = list()

        if self.__ui.combo_target.currentIndex() is \
           not self.__ui.combo_target.model().rowCount() - 1:
            args_.append(self.__ui.combo_target.currentText())
        else:
            args_.append(str(int(self.__ui.spin_bytes.value())))

        for file_ in self.__inputModel.files():
            args_.append(quote(file_.text()))

        self.__proc3.errorOccurred.connect(self.error)
        self.__proc3.readyReadStandardError.connect(self.progressAvailable)
        self.__proc3.readyReadStandardOutput.connect(self.resultAvailable)
        self.__proc3.finished.connect(self.finished)

        self.__statusBar.showMessage(self.tr("Calculating for {} files ...").
                                     format(str(self.__inputModel.rowCount())))

        self.__proc3.start(self.__diskfit, args_, QProcess.ReadOnly)
        self.__proc3.waitForStarted()
        self.__runningTime = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)

        self.__lastResult.clear()

        self.__ui.actionStop.triggered.connect(self.__proc3.terminate)

    @pyqtSlot(QProcess.ProcessError)
    def error(self, err):
        if err == QProcess.FailedToStart:
            QMessageBox.critical(None, self.tr("Error"),
                                 self.tr("Failed to launch {}.".
                                         format(self.__diskfit)))
        self.finished(0, QProcess.NormalExit)

    @pyqtSlot(int, QProcess.ExitStatus)
    def finished(self, ec, es):

        if not QProcess.CrashExit or ec == 0:

            if self.__proc3.receivers(self.__proc3.finished):
                self.__proc3.finished.disconnect(self.finished)

            elapsedTime_ = time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - \
                self.__runningTime

            rbs_ = self.__resultBuf.splitlines(False)
            prm_ = QT_TR_NOOP("Processing result ...")

            progress_ = QProgressDialog(QApplication.
                                        translate("@default", prm_), None, 0,
                                        len(rbs_) * 2)
            progress_.setWindowModality(Qt.WindowModal)
            progress_.setMinimumDuration(750)
            progress_.setAutoReset(True)
            progress_.setAutoClose(True)

            self.__statusBar.showMessage(QApplication.translate("@default",
                                                                prm_))
            for pv_, r_ in enumerate(rbs_):
                r_match_ = r_rex.search(r_)
                if r_match_:
                    self.__lastResult.append((r_match_.group(1),
                                              r_match_.group(2),
                                              r_match_.group(3),
                                              r_match_.group(4)))

            progress_.setMaximum(len(self.__lastResult))

            self.__ui.table_output.setEnabled(False)
            self.__outputModel.setLastResult(self.__lastResult, progress_)
            self.__statusBar. \
                showMessage(self.tr("Calculation took {}").
                            format(time.strftime("%H:%M:%S", time.
                                                 gmtime(int(elapsedTime_)))),
                            0)

            progress_.reset()
            self.__ui.table_output.setEnabled(True)

        else:
            self.__statusBar.showMessage(self.tr("Calculation interrupted"),
                                         5000)

        self.__resultBuf = ""

    @pyqtSlot()
    def resultReady(self):
        self.__ui.actionProfileeditor.setEnabled(True)
        self.__ui.action_SelectAll. \
            setEnabled(self.__inputModel.rowCount() > 0)
        self.__ui.action_inputRemoveAll. \
            setEnabled(self.__inputModel.rowCount() > 0)
        self.__ui.action_InputRemove. \
            setEnabled(len(self.__ui.table_input.selectedIndexes()) > 0)
        self.__ui.action_diffTarget.setEnabled(self.enableExclusive())
        self.__ui.action_InputAdd.setEnabled(True)
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
        self.__saveTarget = True

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
        self.__ui.action_diffTarget.setEnabled(self.enableExclusive())

    @pyqtSlot(int)
    def sortInput(self, idx):
        self.__ui.table_input.header().setSortIndicatorShown(True)

    @pyqtSlot()
    def editProfile(self):
        dlg_ = ProfileEdit(self.__keyfile)
        if dlg_.exec() == ProfileEdit.Accepted:
            self.getTargets()

    @pyqtSlot()
    def diffTarget(self):
        size_ = self.exclusiveSize()

        self.__inputModel.removeFiles()
        self.__ui.combo_target.setCurrentIndex(self.__ui.combo_target.
                                               model().rowCount()-1)
        self.__ui.spin_bytes.setValue(size_)
        self.__saveTarget = False

    def enableExclusive(self):
        return self.__ui.table_input.selectionModel().hasSelection() and \
            self.exclusiveSize() >= 0

    def exclusiveSize(self):
        return int(self.__ui.spin_bytes.value()) - \
            self.__inputModel.getAccuSize(self.__ui.
                                          table_input.selectedIndexes(),
                                          self.__keyfile.
                                          getBlocksize(self.__ui.
                                                       combo_target.
                                                       currentText()))


def main(args=None):

    app = QApplication(sys.argv)

    translator = QTranslator()

    app.setApplicationName("QDiskFit")
    app.setApplicationVersion("2.0.2.11")
    app.setApplicationDisplayName(app.applicationName() + " " +
                                  app.applicationVersion())
    app.setOrganizationDomain("rangun.de")
    app.setOrganizationName("diskfit")

    if translator.load(QLocale(), "qdiskfit", "_",
                       Site().get("transPath", "/usr/share/qdiskfit")):
        app.installTranslator(translator)
    else:
        qDebug("Translations not found!")

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

# kate: indent-mode: python