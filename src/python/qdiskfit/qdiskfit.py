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
from PyQt5.QtCore import QXmlStreamReader
from PyQt5.QtCore import QTemporaryFile
from PyQt5.QtCore import QTranslator
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import qDebug
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QActionGroup
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMenu
from .models.outputmodel import OutputModel
from .models.inputmodel import InputModel
from .profileedit import ProfileEdit
from .mainwindow import mainwindow
from .exclusivedlg import ExclusiveDlg
from .util.diskfitprocess import DiskFitProcess
from .progresswidget import ProgressWidget
from .util.keyfile import Keyfile
from .util.hrsize import HRSize
from datetime import timedelta
from datetime import datetime
from datetime import date
from .site import Site
import signal
import time
import sys
import os
import re


class MainWindow(QMainWindow):

    gui_restored = False

    __ui = None
    __tmp = None
    __proc1 = DiskFitProcess()
    __proc2 = DiskFitProcess()
    __proc3 = DiskFitProcess()
    __inputModel = None
    __outputModel = None
    __diskfitProgress = None
    __lastResult = []
    __resultXml = None
    __statusBar = None
    __unselInputSum = None
    __runningTime = 0.0
    __etaProgress = 0.0
    __etaProgressLabel = None
    __initialEta = 0.0
    __keyfile = None
    __saveTarget = True
    __exclusiveDlg = None

    def __init__(self):

        super(MainWindow, self).__init__()

        self.__ui = mainwindow.Ui_MainWindow()
        self.__ui.setupUi(self)

        self.__etaProgressLabel = QLabel()

        self.__diskfitProgress = ProgressWidget(self.__ui.actionStop)
        self.__diskfitProgress.setMinimum(0)
        self.__diskfitProgress.setMaximum(100)
        self.__diskfitProgress.setValue(0)

        self.__statusBar = self.statusBar()
        self.__statusBar.insertPermanentWidget(0, self.__etaProgressLabel, 2)
        self.__statusBar.insertPermanentWidget(1, self.__diskfitProgress, 1)
        self.__diskfitProgress.setHidden(True)
        self.__etaProgressLabel.setHidden(True)

        self.__keyfile = Keyfile()

        self.__inputModel = InputModel(self.__ui.table_input,
                                       self.__ui.action_Start,
                                       self.__ui.action_SelectAll,
                                       self.__ui.action_inputRemoveAll,
                                       self.__ui.button_clearInput)

        self.__ui.table_input.setModel(self.__inputModel)

        self.__ui.table_input.\
            setContextMenuActions((self.__ui.action_InputAdd,
                                   self.__ui.action_InputRemove,
                                   self.__ui.action_inputRemoveAll,
                                   None,
                                   self.__ui.action_SelectAll,
                                   None,
                                   self.__ui.action_diffTarget))

        self.__outputModel = OutputModel(self.__ui.table_output,
                                         self.__ui.label_runSummary,
                                         self.__inputModel)

        self.__ui.table_output.setModel(self.__outputModel)

        self.__ui.table_output.header(). \
            setContextMenuPolicy(Qt.CustomContextMenu)
        self.__ui.table_output.header(). \
            customContextMenuRequested.connect(self.outputOrder)

        self.__ui.table_output.setContextMenuPolicy(Qt.CustomContextMenu)
        self.__ui.table_output. \
            customContextMenuRequested.connect(self.outputContextRequested)

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
        self.__ui.spin_bytes.valueChanged.connect(self.__inputModel.
                                                  setTargetSize)
        self.__ui.spin_bytes.valueChanged.connect(self.__outputModel.
                                                  setTargetSize)

        self.__outputModel.resultReady.connect(self.resultReady)

        self.__ui.actionProfileeditor.triggered.connect(self.editProfile)

        self.__exclusiveDlg = ExclusiveDlg()

        self.__ui.actionShow_exclusive_files.triggered. \
            connect(self.showExclusiveFiles)

        self.readSettings()
        self.getTargets()

    def getTargets(self):
        self.__proc1.errorOccurred.connect(self.error)
        self.__proc1.readyReadStandardOutput.connect(self.targetsAvailable)
        self.__proc1.runDiskFit()

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
    def outputContextRequested(self, pos):

        globalPos = self.__ui.table_output.mapToGlobal(pos)
        currentIndex = self.__ui.table_output.currentIndex()

        if currentIndex.isValid():

            atar_ = QAction(self.tr("Add as new target..."))

            menu_ = QMenu()
            menu_.addAction(atar_)

            selectedItem = menu_.exec_(globalPos)

            if selectedItem and selectedItem is atar_:
                self.__keyfile.addTarget(self.tr("my_target_{}").
                                         format(date.today().isoformat()),
                                         self.__ui.table_output.model().
                                         item(currentIndex.row(), 2).num(),
                                         self.__keyfile.
                                         getBlocksize(self.__ui.
                                                      combo_target.
                                                      currentText()))
                self.__ui.actionProfileeditor.trigger()

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
    def showExclusiveFiles(self):
        self.__exclusiveDlg.exec()

    def updateETA(self, eta_, p_=0):
        str_ = self.tr("Calculating for {} files ..."). \
            format(str(self.__inputModel.enabledItems()))

        if self.__initialEta >= 30.0 and p_ > 0 and p_ <= 90:

            if p_ == 1:
                eta_ *= 2.0

            left_ = timedelta(milliseconds=(eta_ * 1000.0))
            leta_ = datetime.now() + left_

            millis_ = int(eta_ * 1000.0)
            seconds_ = (millis_ / 1000) % 60
            seconds_ = int(seconds_)
            minutes_ = (millis_ / (1000 * 60)) % 60
            minutes_ = int(minutes_)
            hours_ = (millis_ / (1000 * 60 * 60)) % 24
            hours_ = int(hours_)

            str_ += " — ETA: " + format(leta_.time().strftime("%H:%M:%S") +
                                        " [~" + "{0}:{1}:{2}".
                                        format(("00" + str(hours_))[-2:]
                                               if hours_ < 10 else str(hours_),
                                               ("00" + str(minutes_))[-2:],
                                               ("00" + str(seconds_))[-2:] +
                                               "]"))

        self.__etaProgressLabel.setText(str_)

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

        self.__diskfitProgress.setHidden(False)

        args_ = []

        if self.__ui.combo_target.currentIndex() is \
           not self.__ui.combo_target.model().rowCount() - 1:
            args_.append(self.__ui.combo_target.currentText())
        else:
            args_.append(str(int(self.__ui.spin_bytes.value())))

        self.__tmp = QTemporaryFile()

        if self.__tmp.open():
            for file_ in self.__inputModel.files():
                self.__tmp.write(bytearray(file_.text(), "utf-8"))
                self.__tmp.putChar('\n')
            self.__tmp.close()
            args_.append("@" + self.__tmp.fileName())

            self.__proc3.errorOccurred.connect(self.error)
            self.__proc3.readyReadStandardError.connect(self.progressAvailable)
            self.__proc3.readyReadStandardOutput.connect(self.resultAvailable)
            self.__proc3.finished.connect(self.finished)

            self.__etaProgressLabel.setHidden(False)
            self.updateETA(0.0)

            self.__resultXml = QXmlStreamReader()

            self.__proc3.runDiskFit(args_)
            self.__proc3.waitForStarted()
            self.__runningTime = time.clock_gettime(time.CLOCK_MONOTONIC_RAW)
            self.__etaProgress = self.__runningTime

            self.__lastResult *= 0

            self.__ui.actionStop.triggered.connect(self.stop)
        else:
            QMessageBox.critical(None, self.tr("Error"),
                                 self.__tmp.errorString())
            self.finished(0, DiskFitProcess.NormalExit)

    @pyqtSlot()
    def stop(self):
        if self.__initialEta > 150.0:
            self.__ui.actionStop.triggered.disconnect(self.stop)
            os.kill(self.__proc3.pid(), signal.SIGSTOP)
            if ((QMessageBox.question(None,
                                      self.tr("Paused"),
                                      self.tr("Really cancel calculation?")) ==
                 QMessageBox.Yes)):
                os.kill(self.__proc3.pid(), signal.SIGCONT)
                self.__proc3.terminate()

            os.kill(self.__proc3.pid(), signal.SIGCONT)
            self.__ui.actionStop.triggered.connect(self.stop)
        else:
            self.__proc3.terminate()

    @pyqtSlot(DiskFitProcess.ProcessError)
    def error(self, err):
        if err == DiskFitProcess.FailedToStart:
            QMessageBox.critical(None, self.tr("Error"),
                                 self.tr("Failed to launch {}.".
                                         format(DiskFitProcess.diskfitPath())))
        self.finished(0, DiskFitProcess.NormalExit)

    def appendResultFiles(self, files_, bs_):

        ts_ = 0

        for f_ in files_:

            ps_ = self.__outputModel.fileSize(f_)
            if bs_ > 0:
                ps_ += bs_ - (ts_ & (bs_ - 1))
            ts_ += ps_

        self.__lastResult.append((files_, str(len(files_)),
                                  HRSize.sizeString(ts_)))

    @pyqtSlot(int, DiskFitProcess.ExitStatus)
    def finished(self, ec, es):

        if not DiskFitProcess.CrashExit or ec == 0:

            if self.__proc3.receivers(self.__proc3.finished):
                self.__proc3.finished.disconnect(self.finished)

            elapsedTime_ = time.clock_gettime(time.CLOCK_MONOTONIC_RAW) - \
                self.__runningTime

            prm_ = QT_TR_NOOP("Processing result ...")
            bs_ = self.__keyfile.getBlocksize(self.__ui.
                                              combo_target.currentText())

            files_ = None
            while (self.__resultXml is not None and
                   not self.__resultXml.atEnd()):
                if self.__resultXml.readNextStartElement():
                    if self.__resultXml.name() == "files":
                        if files_ is not None:
                            self.appendResultFiles(files_, bs_)
                        files_ = []
                    elif self.__resultXml.name() == "filename":
                        files_.append((self.__resultXml.readElementText()))

            if files_ is not None and len(files_):
                self.appendResultFiles(files_, bs_)

            progress_ = QProgressDialog(QApplication.
                                        translate("@default", prm_), None, 0,
                                        len(self.__lastResult) * 2)
            progress_.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
            progress_.setWindowModality(Qt.WindowModal)
            progress_.setMinimumDuration(750)
            progress_.setAutoReset(True)
            progress_.setAutoClose(True)

            self.__statusBar.showMessage(QApplication.translate("@default",
                                                                prm_))

            progress_.setMaximum(len(self.__lastResult))

            self.__ui.table_output.setEnabled(False)
            self.__outputModel.setLastResult(self.__lastResult, progress_)

            if elapsedTime_ > 1.0:
                self.__statusBar. \
                    showMessage(self.tr("Calculation took {}").
                                format(time.
                                       strftime("%H:%M:%S", time.
                                                gmtime(int(elapsedTime_)))), 0)
            else:
                self.__statusBar.clearMessage()

            progress_.reset()
            self.__ui.table_output.setEnabled(True)

        else:
            self.__statusBar.showMessage(self.tr("Calculation interrupted"),
                                         5000)

        self.__tmp = None
        self.__resultXml = None
        self.__etaProgressLabel.setHidden(True)
        self.__diskfitProgress.setHidden(True)

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
        self.__diskfitProgress.setHidden(False)
        self.__diskfitProgress.setValue(0)
        self.__diskfitProgress.setMaximum(100)

    @pyqtSlot()
    def progressAvailable(self):

        try:
            for p_ in str(self.__proc3.readAllStandardError().data().
                          decode("utf-8")).splitlines(False):
                p_match_ = p_rex.search(p_)
                if p_match_:
                    p_ = int(p_match_.group(2))
                    eta_ = (time.clock_gettime(time.CLOCK_MONOTONIC_RAW) -
                            self.__etaProgress) * (90 - p_)
                    self.__etaProgress = time. \
                        clock_gettime(time.CLOCK_MONOTONIC_RAW)
                    if p_ == 0:
                        self.__diskfitProgress.setMaximum(0)
                    else:
                        self.__diskfitProgress.setMaximum(100)
                        if p_ == 1:
                            self.__initialEta = eta_
                        self.updateETA(eta_, p_)

                    self.__diskfitProgress.setValue(p_)
        except UnicodeDecodeError as e:
            qDebug("".join(("UnicodeDecodeError in parsing progress. "
                            "Ignored. - ", str(e))))

    @pyqtSlot()
    def resultAvailable(self):
        self.__resultXml.addData(self.__proc3.readAllStandardOutput().data())

    @pyqtSlot()
    def targetsAvailable(self):

        for t_ in reversed(str(self.__proc1.readAllStandardOutput().data().
                               decode("utf-8")).splitlines(False)):

            t_match_ = t_rex.match(t_)

            if t_match_ is not None:

                l_ = []
                m_ = t_match_.group(1)
                l_.append(m_)

                self.__ui.combo_target.insertItem(-1, m_)
                self.__ui.combo_target.setCurrentIndex(0)

                self.__proc2.readyReadStandardOutput. \
                    connect(self.targetSizeAvailable)

                self.__proc2.runDiskFit(l_)
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
            self.__inputModel.setTargetSize(d_)
            self.__ui.spin_bytes.setValue(d_)
            self.__ui.spin_bytes.setEnabled(False)
        else:
            tsc_ = self.__keyfile.getTargetsize(self.__ui.combo_target.
                                                currentText())
            self.__inputModel.setTargetSize(float(tsc_ if tsc_ is not None
                                                  else self.__ui.spin_bytes.
                                                  value()))
            self.__ui.spin_bytes.setEnabled(True)

        self.__inputModel.modelChanged()

    @pyqtSlot()
    def inputSelectionChanged(self):

        en_ = self.__ui.table_input.selectionModel().hasSelection()
        self.__ui.button_ListRemove.setEnabled(en_)
        self.__ui.action_InputRemove.setEnabled(en_)
        self.__ui.action_diffTarget.setEnabled(self.enableExclusive())

        if en_:
            if self.__unselInputSum is None:
                self.__unselInputSum = self.__ui.table_input.summary()
            self.__ui. \
                table_input. \
                setSummary(self.tr("<i>{0} in {1} files</i> of {2}").
                           format(HRSize.
                                  sizeString(self.
                                             __inputModel.
                                             getAccuSize(self.__ui.
                                                         table_input.
                                                         selectedIndexes(),
                                                         0)),
                                  len(self.__ui.table_input.
                                      selectionModel().selectedRows()),
                                  self.__unselInputSum))
        else:
            self.__ui.table_input.setSummary(self.__unselInputSum)
            self.__unselInputSum = None

    @pyqtSlot(int)
    def sortInput(self, idx):
        self.__ui.table_input.header().setSortIndicatorShown(True)

    @pyqtSlot()
    def editProfile(self):
        dlg_ = ProfileEdit(self.__keyfile, self.__ui.combo_target.
                           currentText())
        if dlg_.exec() == ProfileEdit.Accepted:
            self.getTargets()

    @pyqtSlot()
    def diffTarget(self):

        size_ = self.exclusiveSize()

        self.__exclusiveDlg.diffFiles(self.__ui.table_input)

        self.__inputModel.removeFiles()
        self.__ui.combo_target.setCurrentIndex(self.__ui.combo_target.
                                               model().rowCount() - 1)
        self.__ui.spin_bytes.setValue(size_)
        self.__saveTarget = False
        self.__inputModel.setTargetSize(size_)

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
    app.setApplicationVersion("2.0.4.4")
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

if __name__ == "__main__":
    main()

# kate: indent-mode: python
