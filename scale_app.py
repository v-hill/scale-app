
import csv
import json
import sys
from datetime import datetime

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QDoubleValidator, QIcon, QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QGroupBox, QHeaderView, QLabel, QLineEdit,
                             QMessageBox, QPushButton, QTableWidget,
                             QTableWidgetItem, QTabWidget, QVBoxLayout,
                             QWidget)


def dark_mode(app):
    """
    Set the colour palette of an app to a custom dark mode theme.

    Parameters
    ----------
    app : PyQt5.QtWidgets.QApplication
        The Qt App object

    Returns
    -------
    PyQt5.QtWidgets.QApplication
        The Qt app with the dark mode theme applied.
    """
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(30, 30, 30))
    palette.setColor(QPalette.WindowText, QColor(225, 225, 225))
    palette.setColor(QPalette.Light, Qt.white)
    palette.setColor(QPalette.Midlight, QColor(225, 225, 225))
    palette.setColor(QPalette.Dark, QColor(65, 65, 65))
    palette.setColor(QPalette.Mid, QColor(160, 160, 160))
    palette.setColor(QPalette.BrightText, QColor(255, 51, 51))
    palette.setColor(QPalette.Button, QColor(40, 40, 40))
    palette.setColor(QPalette.Base, QColor(65, 65, 65))
    palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, QColor(225, 225, 225))
    palette.setColor(QPalette.ButtonText, QColor(225, 225, 225))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    return app


class WeightLog():
    """
    Main class for storing both the Qt app and database, with functions
    that act on both objects.
    """

    def __init__(self, settings):
        self.settings = settings
        # self.df = pd.read_csv(self.settings['db_path'], encoding='utf-8')
        self.tabdialog = Tab(settings)
        self.tabdialog.show()


class Tab(QDialog):
    """
    Child class of a Qt dialog window. Where a dialog window is a top-level
    window mostly used for short-term tasks and brief communications with
    the user.

    Parameters
    ----------
    QDialog : PyQt5.QtWidgets.QDialog
        The main Qt dialog window which stores the individual tabs of the
        programme.
    """

    def __init__(self, settings):
        super().__init__()
        self.setWindowTitle("Body Weight Log")
        self.setWindowIcon(QIcon("icon.png"))
        vbox = QVBoxLayout()
        tabWidget = QTabWidget()

        font = tabWidget.font()
        font.setPointSize(settings['font_point_size'])
        tabWidget.setFont(font)
        self.setMinimumSize(
            QSize(
                settings['WindowWidth'],
                settings['WindowHeight']))

        tabWidget.addTab(TabAdd(settings), "Add data")
        tabWidget.addTab(TabCSV(settings), "View table")
        tabWidget.addTab(TabPlotting(settings), "Plot data")
        vbox.addWidget(tabWidget)
        self.setLayout(vbox)


class TabAdd(QWidget):
    """
    Child class of Qt QWidget object. This class represents the first
    tab of the user interface which contains the database additional
    functionalilty.

    Parameters
    ----------
    QWidget : PyQt5.QtWidgets.QWidget
        The widget is the atom of the user interface.
    """

    def __init__(self, settings):
        """
        Setup the "Add data" applicaiton tab.

        Parameters
        ----------
        settings : dict
            Settings dict imported from the app settings.json file.
        """
        super().__init__()
        self.settings = settings
        self.font_size = settings['font_point_size']
        weightlabel = QLabel("Weight (kg):")
        self.weight_edit = QLineEdit()
        self.only_floats = QDoubleValidator()
        self.weight_edit.setValidator(self.only_floats)
        self.weight_edit.setPlaceholderText(self.last_measurement())

        date = QLabel("Date:")
        self.date_edit = QLineEdit()
        self.date_edit.setText(datetime.today().strftime("%Y-%m-%d"))

        addr = QLabel("Comment:")
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("Optional")

        addval = QPushButton("Add value")
        addval.clicked.connect(self.clickMethod)

        vbox = QVBoxLayout()
        vbox.setContentsMargins(30, 30, 30, 30)
        vbox.addWidget(weightlabel)
        vbox.addWidget(self.weight_edit)
        vbox.addWidget(date)
        vbox.addWidget(self.date_edit)
        vbox.addWidget(addr)
        vbox.addWidget(self.comment_edit)
        vbox.addStretch(30)
        vbox.addWidget(addval)
        self.setLayout(vbox)

    def last_measurement(self):
        """
        Get the last weight value entered into the database.

        Returns
        -------
        str
            Last measured weight in kg.
        """
        with open(self.settings['db_path'], newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
        for entry in reversed(data):
            if entry[1] != '':
                return str(entry[1])
        return ''

    def date_format_correct(self):
        """
        Check that date entered conforms to "%Y-%m-%d" format.

        Returns
        -------
        bool
            True if date is of a valid format, else False.
        """
        valid_format = True
        try:
            new_val = self.date_edit.text()
            datetime_object = datetime.strptime(new_val, "%Y-%m-%d")
        except BaseException:
            valid_format = False
        return valid_format

    def date_temporal_paradox_free(self):
        """
        Checks that the date entered is not after todays date. You can't know
        tommorrows weight if you haven't measured it yet.

        Returns
        -------
        bool
            True if date is not a temporal paradox, else False.
        """
        valid_date = True
        new_val = self.date_edit.text()
        datetime_object = datetime.strptime(new_val, "%Y-%m-%d")

        if datetime_object > datetime.now():
            valid_date = False
        return valid_date

    def clickMethod(self):
        """
        Defines the response to the "Add value" button.
        """
        if not self.date_format_correct():
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setWindowIcon(QIcon("icon.png"))
            msg.setIcon(QMessageBox.Warning)

            font = msg.font()
            font.setPointSize(self.font_size)
            msg.setFont(font)

            msg.setText("Date entered in incorrect format.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)

            x = msg.exec_()  # show our messagebox

        elif not self.date_temporal_paradox_free():
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setWindowIcon(QIcon("icon.png"))
            msg.setIcon(QMessageBox.Warning)

            font = msg.font()
            font.setPointSize(self.font_size)
            msg.setFont(font)

            msg.setText(
                "Date entered is invalid since it is after today's date.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setDefaultButton(QMessageBox.Ok)

            x = msg.exec_()  # show our messagebox

        else:
            msg = QMessageBox()
            msg.setWindowTitle("New entry")
            msg.setWindowIcon(QIcon("icon.png"))
            font = msg.font()
            font.setPointSize(self.font_size)
            msg.setFont(font)
            msg.setText("New entry added to weight log")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Ok)
            msg.buttonClicked.connect(self.button_accepted)
            x = msg.exec_()  # show our messagebox

    def button_accepted(self, i):
        """
        Execute if okay button is pressed from AddTab.

        Parameters
        ----------
        i :<PyQt5.QtWidgets.QPushButton
            Button class object
        """
        if i.text() == "OK":
            print("Entry added")


class PandasWidget(QTableWidget):
    """
    Redifinition of the Qt QTableWidget class to implement an editable table
    view of the database.

    Parameters
    ----------
    QTableWidget : PyQt5.QtWidgets.QTableWidget
        Table widgets provide standard table display facilities for
        applications.
    """

    def __init__(self, df):
        super().__init__()
        self.df = df
        self.setStyleSheet('font-size: 28px;')
        self.insert_data(df)

        self.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def insert_data(self, data):
        """
        Populate the table with the data from the weight database.

        Parameters
        ----------
        data : Pandas DataFrame
            The data to be displayed in the table.
        """
        # set table dimension
        self.df = data
        nRows, nColumns = data.shape
        self.setColumnCount(nColumns)
        self.setRowCount(nRows)
        self.setHorizontalHeaderLabels(data.columns)

        # data insertion
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.setItem(i, j, QTableWidgetItem(str(data.iloc[i, j])))

        # Enable cell updates
        self.cellChanged[int, int].connect(self.updateDF)

        self.scrollToBottom()

    def updateDF(self, row, column):
        """
        Updates a specificed cell in the database.

        Parameters
        ----------
        row : int
            The database row index.
        column : int
            The database column index.
        """
        text = self.item(row, column).text()
        self.df.iloc[row, column] = text


class TabCSV(QWidget):
    """
    Child class of Qt QWidget object. This class represents the second tab in
    the application which presents a table of the weight database which can be
    inspected and edited by the user.

    Parameters
    ----------
    QWidget : PyQt5.QtWidgets.QWidget
        The widget is the atom of the user interface.
    """

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.load_csv()

        mainLayout = QVBoxLayout()
        self.tableView = PandasWidget(pd.DataFrame())
        # self.tableView = PandasWidget(self.database)

        self.pushButtonLoad = QPushButton("Load csv")
        self.pushButtonLoad.clicked.connect(self.reload_csv)

        self.pushButtonWrite = QPushButton("Write to csv")
        self.pushButtonWrite.clicked.connect(self.write_csv)

        mainLayout.addWidget(self.tableView)
        mainLayout.addWidget(self.pushButtonLoad)
        mainLayout.addWidget(self.pushButtonWrite)
        self.setLayout(mainLayout)

    def load_csv(self):
        """
        Load in the weight databse from the location specified in the
        settings json file.
        """
        self.database = pd.read_csv(self.settings['db_path'], encoding='utf-8')

    def write_csv(self):
        """
        Write to the weight databse in the location specified in the settings
        json file.
        """
        self.tableView.df.to_csv('Data export.csv', index=False)
        print('CSV file exported')

    @QtCore.pyqtSlot()
    def reload_csv(self):
        """
        Full function to load csv data and populate the table with the new
        data.
        """
        self.load_csv()
        self.tableView.insert_data(self.database)
        self.update()


class TabPlotting(QWidget):
    """
    Child class of Qt QWidget object. This class represents the final tab of
    the application which is used for plotting values in the weight database.

    Parameters
    ----------
    QWidget : PyQt5.QtWidgets.QWidget
        The widget is the atom of the user interface.
    """

    def __init__(self, settings):
        """
        Initialse the layout and user iterface of the plotting tab.

        Parameters
        ----------
        settings : dict
            Settings from the json settings file.
        """
        super().__init__()
        self.settings = settings
        groupBox = QGroupBox("Select data range")
        list = ["1M", "3M", "6M", "YTD", "1Y", "MAX"]
        combo = QComboBox()
        combo.addItems(list)
        vbox = QVBoxLayout()
        vbox.addWidget(combo)
        groupBox.setLayout(vbox)
        groupBox2 = QGroupBox("Plot options")
        av7day = QCheckBox("7 day average")
        av7day.setChecked(1)
        lineplot = QCheckBox("Lineplot")
        plotlbs = QCheckBox("Plot in lbs")

        vboxp = QVBoxLayout()
        vboxp.addWidget(av7day)
        vboxp.addWidget(lineplot)
        vboxp.addWidget(plotlbs)

        plotvals = QPushButton("Plot data")

        groupBox2.setLayout(vboxp)
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(30, 30, 30, 30)
        mainLayout.addWidget(groupBox)
        mainLayout.addWidget(groupBox2)
        mainLayout.addStretch(30)
        mainLayout.addWidget(plotvals)
        self.setLayout(mainLayout)


# The main attraction
if __name__ == "__main__":
    # Import settings
    with open('settings.json', 'r') as f:
        settings = json.load(f)

    # Start the app
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Force the style to be the same on all OSs
    app = dark_mode(app)
    weightlog = WeightLog(settings)
    app.exec()
