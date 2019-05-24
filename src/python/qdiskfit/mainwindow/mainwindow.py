# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qdiskfit/mainwindow/mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(539, 695)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.group_profile = QtWidgets.QGroupBox(self.centralwidget)
        self.group_profile.setObjectName("group_profile")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.group_profile)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label_target = QtWidgets.QLabel(self.group_profile)
        self.label_target.setObjectName("label_target")
        self.horizontalLayout_3.addWidget(self.label_target)
        self.combo_target = QtWidgets.QComboBox(self.group_profile)
        self.combo_target.setObjectName("combo_target")
        self.combo_target.addItem("")
        self.horizontalLayout_3.addWidget(self.combo_target)
        self.spin_bytes = QtWidgets.QDoubleSpinBox(self.group_profile)
        self.spin_bytes.setEnabled(False)
        self.spin_bytes.setDecimals(0)
        self.spin_bytes.setMinimum(1.0)
        self.spin_bytes.setMaximum(1.8446744073709552e+19)
        self.spin_bytes.setObjectName("spin_bytes")
        self.horizontalLayout_3.addWidget(self.spin_bytes)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.horizontalLayout_3.setStretch(0, 3)
        self.horizontalLayout_3.setStretch(2, 1)
        self.horizontalLayout_3.setStretch(4, 3)
        self.verticalLayout.addWidget(self.group_profile)
        self.splitter_inout = QtWidgets.QSplitter(self.centralwidget)
        self.splitter_inout.setOrientation(QtCore.Qt.Vertical)
        self.splitter_inout.setChildrenCollapsible(False)
        self.splitter_inout.setObjectName("splitter_inout")
        self.group_InputFiles = QtWidgets.QGroupBox(self.splitter_inout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.group_InputFiles.sizePolicy().hasHeightForWidth())
        self.group_InputFiles.setSizePolicy(sizePolicy)
        self.group_InputFiles.setObjectName("group_InputFiles")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.group_InputFiles)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget_2 = QtWidgets.QWidget(self.group_InputFiles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.widget_2)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.table_input = QtWidgets.QTreeView(self.widget_2)
        self.table_input.setAcceptDrops(True)
        self.table_input.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_input.setProperty("showDropIndicator", True)
        self.table_input.setDragEnabled(False)
        self.table_input.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.table_input.setAlternatingRowColors(True)
        self.table_input.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.table_input.setRootIsDecorated(False)
        self.table_input.setItemsExpandable(False)
        self.table_input.setSortingEnabled(True)
        self.table_input.setObjectName("table_input")
        self.table_input.header().setSortIndicatorShown(False)
        self.table_input.header().setStretchLastSection(False)
        self.verticalLayout_7.addWidget(self.table_input)
        self.label_inputSummary = QtWidgets.QLabel(self.widget_2)
        self.label_inputSummary.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_inputSummary.setObjectName("label_inputSummary")
        self.verticalLayout_7.addWidget(self.label_inputSummary)
        self.label_inputSummary.raise_()
        self.table_input.raise_()
        self.horizontalLayout.addWidget(self.widget_2)
        self.widget = QtWidgets.QWidget(self.group_InputFiles)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setObjectName("widget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.button_InputAdd = QtWidgets.QPushButton(self.widget)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.button_InputAdd.setIcon(icon)
        self.button_InputAdd.setObjectName("button_InputAdd")
        self.verticalLayout_5.addWidget(self.button_InputAdd)
        self.button_ListRemove = QtWidgets.QPushButton(self.widget)
        self.button_ListRemove.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.button_ListRemove.setIcon(icon)
        self.button_ListRemove.setObjectName("button_ListRemove")
        self.verticalLayout_5.addWidget(self.button_ListRemove)
        spacerItem2 = QtWidgets.QSpacerItem(0, 16, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem2)
        self.button_clearInput = QtWidgets.QPushButton(self.widget)
        self.button_clearInput.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("user-trash")
        self.button_clearInput.setIcon(icon)
        self.button_clearInput.setObjectName("button_clearInput")
        self.verticalLayout_5.addWidget(self.button_clearInput)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.horizontalLayout.addWidget(self.widget)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.group_outputFiles = QtWidgets.QGroupBox(self.splitter_inout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.group_outputFiles.sizePolicy().hasHeightForWidth())
        self.group_outputFiles.setSizePolicy(sizePolicy)
        self.group_outputFiles.setObjectName("group_outputFiles")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.group_outputFiles)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.table_output = QtWidgets.QTreeView(self.group_outputFiles)
        self.table_output.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_output.setDragEnabled(True)
        self.table_output.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.table_output.setAlternatingRowColors(True)
        self.table_output.setRootIsDecorated(True)
        self.table_output.setItemsExpandable(True)
        self.table_output.setObjectName("table_output")
        self.table_output.header().setStretchLastSection(False)
        self.verticalLayout_3.addWidget(self.table_output)
        self.label_runSummary = QtWidgets.QLabel(self.group_outputFiles)
        self.label_runSummary.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_runSummary.setObjectName("label_runSummary")
        self.verticalLayout_3.addWidget(self.label_runSummary)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout.addWidget(self.splitter_inout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 539, 32))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menu_Help = QtWidgets.QMenu(self.menubar)
        self.menu_Help.setObjectName("menu_Help")
        self.menu_Edit = QtWidgets.QMenu(self.menubar)
        self.menu_Edit.setObjectName("menu_Edit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonFollowStyle)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.RightToolBarArea, self.toolBar)
        self.actionQuit = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("application-exit")
        self.actionQuit.setIcon(icon)
        self.actionQuit.setMenuRole(QtWidgets.QAction.QuitRole)
        self.actionQuit.setObjectName("actionQuit")
        self.actionStop = QtWidgets.QAction(MainWindow)
        self.actionStop.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("process-stop")
        self.actionStop.setIcon(icon)
        self.actionStop.setObjectName("actionStop")
        self.action_Start = QtWidgets.QAction(MainWindow)
        self.action_Start.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("system-run")
        self.action_Start.setIcon(icon)
        self.action_Start.setObjectName("action_Start")
        self.action_InputAdd = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.action_InputAdd.setIcon(icon)
        self.action_InputAdd.setObjectName("action_InputAdd")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme("help-about")
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName("actionAbout")
        self.action_InputRemove = QtWidgets.QAction(MainWindow)
        self.action_InputRemove.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.action_InputRemove.setIcon(icon)
        self.action_InputRemove.setObjectName("action_InputRemove")
        self.action_SelectAll = QtWidgets.QAction(MainWindow)
        self.action_SelectAll.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("edit-select-all")
        self.action_SelectAll.setIcon(icon)
        self.action_SelectAll.setObjectName("action_SelectAll")
        self.action_inputRemoveAll = QtWidgets.QAction(MainWindow)
        self.action_inputRemoveAll.setEnabled(False)
        icon = QtGui.QIcon.fromTheme("user-trash")
        self.action_inputRemoveAll.setIcon(icon)
        self.action_inputRemoveAll.setObjectName("action_inputRemoveAll")
        self.menuFile.addAction(self.action_Start)
        self.menuFile.addAction(self.actionStop)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menu_Help.addAction(self.actionAbout)
        self.menu_Edit.addAction(self.action_InputAdd)
        self.menu_Edit.addAction(self.action_InputRemove)
        self.menu_Edit.addAction(self.action_inputRemoveAll)
        self.menu_Edit.addSeparator()
        self.menu_Edit.addAction(self.action_SelectAll)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menu_Edit.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.toolBar.addAction(self.action_Start)
        self.toolBar.addAction(self.actionStop)
        self.toolBar.addAction(self.actionAbout)
        self.label_target.setBuddy(self.combo_target)

        self.retranslateUi(MainWindow)
        self.actionQuit.triggered.connect(MainWindow.close)
        self.action_InputAdd.triggered.connect(self.button_InputAdd.click)
        self.action_InputRemove.triggered.connect(self.button_ListRemove.click)
        self.action_SelectAll.triggered.connect(self.table_input.selectAll)
        self.action_inputRemoveAll.triggered.connect(self.button_clearInput.click)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.combo_target, self.spin_bytes)
        MainWindow.setTabOrder(self.spin_bytes, self.table_input)
        MainWindow.setTabOrder(self.table_input, self.button_InputAdd)
        MainWindow.setTabOrder(self.button_InputAdd, self.button_ListRemove)
        MainWindow.setTabOrder(self.button_ListRemove, self.button_clearInput)
        MainWindow.setTabOrder(self.button_clearInput, self.table_output)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.group_profile.setTitle(_translate("MainWindow", "Profile"))
        self.label_target.setText(_translate("MainWindow", "&Target:"))
        self.combo_target.setToolTip(_translate("MainWindow", "Predefined or custom target"))
        self.combo_target.setItemText(0, _translate("MainWindow", "Custom"))
        self.spin_bytes.setToolTip(_translate("MainWindow", "Size of the target in bytes"))
        self.spin_bytes.setSuffix(_translate("MainWindow", " Bytes"))
        self.group_InputFiles.setTitle(_translate("MainWindow", "Input files"))
        self.table_input.setToolTip(_translate("MainWindow", "Files used for calculation"))
        self.label_inputSummary.setText(_translate("MainWindow", "No files"))
        self.button_InputAdd.setToolTip(_translate("MainWindow", "Add file(s) for calculation"))
        self.button_InputAdd.setText(_translate("MainWindow", "&Add"))
        self.button_ListRemove.setToolTip(_translate("MainWindow", "Remove file(s)"))
        self.button_ListRemove.setText(_translate("MainWindow", "&Remove"))
        self.button_clearInput.setToolTip(_translate("MainWindow", "Clear all input files"))
        self.button_clearInput.setText(_translate("MainWindow", "&Clear"))
        self.group_outputFiles.setTitle(_translate("MainWindow", "Output"))
        self.table_output.setToolTip(_translate("MainWindow", "Result of the calculation"))
        self.label_runSummary.setText(_translate("MainWindow", "No result"))
        self.menuFile.setTitle(_translate("MainWindow", "Fi&le"))
        self.menu_Help.setTitle(_translate("MainWindow", "Hel&p"))
        self.menu_Edit.setTitle(_translate("MainWindow", "&Edit"))
        self.toolBar.setWindowTitle(_translate("MainWindow", "Toolbar"))
        self.actionQuit.setText(_translate("MainWindow", "&Quit"))
        self.actionQuit.setShortcut(_translate("MainWindow", "Ctrl+Q"))
        self.actionStop.setText(_translate("MainWindow", "St&op"))
        self.actionStop.setToolTip(_translate("MainWindow", "Interrupt calculation"))
        self.actionStop.setShortcut(_translate("MainWindow", "Esc"))
        self.action_Start.setText(_translate("MainWindow", "&Start"))
        self.action_Start.setToolTip(_translate("MainWindow", "Start calculation"))
        self.action_Start.setShortcut(_translate("MainWindow", "Ctrl+R"))
        self.action_InputAdd.setText(_translate("MainWindow", "&Add input files..."))
        self.action_InputAdd.setShortcut(_translate("MainWindow", "Ctrl++"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.action_InputRemove.setText(_translate("MainWindow", "&Remove input files"))
        self.action_InputRemove.setShortcut(_translate("MainWindow", "Del"))
        self.action_SelectAll.setText(_translate("MainWindow", "&Select all input files"))
        self.action_SelectAll.setShortcut(_translate("MainWindow", "Ctrl+A"))
        self.action_inputRemoveAll.setText(_translate("MainWindow", "&Remove all input files"))
        self.action_inputRemoveAll.setShortcut(_translate("MainWindow", "Shift+Del"))

