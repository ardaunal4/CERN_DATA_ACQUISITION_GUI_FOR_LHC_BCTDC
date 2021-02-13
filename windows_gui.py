from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QDate, pyqtSlot
from PyQt5.QtGui import QIcon
from datetime import datetime
import calendar
import sys
import numpy as np 
import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
#import pytimber
import os
import matplotlib.dates as mdates
from scipy.signal import find_peaks

matplotlib.use('Qt5Agg')
myFmt = mdates.DateFormatter('%d')

#db = pytimber.LoggingDB()

start_date = {"start_day":datetime.now().day, "start_month":datetime.now().month, "start_year":datetime.now().year}
end_date   = {"end_day":datetime.now().day, "end_month":datetime.now().month, "end_year":datetime.now().year}

variable_list = ["LHC.BCTDC.A6R4.B1:BEAM_INTENSITY", "LHC.BCTDC.A6R4.B2:BEAM_INTENSITY", "LHC.BCTDC.B6R4.B1:BEAM_INTENSITY", "LHC.BCTDC.B6R4.B2:BEAM_INTENSITY", 
                 "LHC.BCTDC.A6R4.B1:BEAM_INTENSITY_ADC24BIT", "LHC.BCTDC.A6R4.B2:BEAM_INTENSITY_ADC24BIT", "LHC.BCTDC.B6R4.B1:BEAM_INTENSITY_ADC24BIT", "LHC.BCTDC.B6R4.B2:BEAM_INTENSITY_ADC24BIT"]

data_save_list = ["ADC_16BIT_AB1", "ADC_16BIT_AB2", "ADC_16BIT_BB1", "ADC_16BIT_BB2", "ADC_24BIT_AB1", "ADC_24BIT_AB2", "ADC_24BIT_BB1", "ADC_24BIT_BB2"]

df_16bit_AB1 = pd.DataFrame({"time":[], "intensity":[]}, columns = ["time", "intensity"]); df_16bit_AB2 = pd.DataFrame({"time":[], "intensity":[]}, columns = ["time", "intensity"])
df_16bit_BB1 = pd.DataFrame({"time":[], "intensity":[]}, columns = ["time", "intensity"]); df_16bit_BB2 = pd.DataFrame({"time":[], "intensity":[]}, columns = ["time", "intensity"])
df_24bit_AB1 = pd.DataFrame({"time":[], "intensity":[]}, columns = ["time", "intensity"]); df_24bit_AB2 = pd.DataFrame({"time":[], "intensity":[]}, columns = ["time", "intensity"])
df_24bit_BB1 = pd.DataFrame({"time":[], "intensity":[]}, columns = ["time", "intensity"]); df_24bit_BB2 = pd.DataFrame({"time":[], "intensity":[]}, columns = ["time", "intensity"])
dataFrame_list = [df_16bit_AB1, df_16bit_AB2, df_16bit_BB1, df_16bit_BB2, df_24bit_AB1, df_24bit_AB2, df_24bit_BB1, df_24bit_BB2]

time_dict = {"tstart":"", "tend":""}
error_check = {"error":2}
step_number = {'step_number':80}
second_clicked = {'clicked':0}

class Window(QMainWindow): 
 
    def __init__(self):

        super().__init__()
        self.setGeometry(50, 50, 1500, 900) 
        self.setWindowTitle("Timber Check Data Base")
        self.setWindowIcon(QIcon("CERN_logo.png"))
        self.tabWidget()
        self.Widgets()
        self.layouts()
        self.show()

    def tabWidget(self):

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab1 = QWidget()
        self.tabs.addTab(self.tab1, "Main")

    def Widgets(self):

        self.plt = PlotCanvas(self, width = 10, height = 8)
        self.toolbar = NavigationToolbar(self.plt, self)
        self.result_list = QListWidget(self)
        self.result_list.setMinimumSize(100, 700)
        self.calendar1 = DateEdit1(self)
        self.calendar2 = DateEdit2(self)

        self.cb1 = QCheckBox('16 bit AB1', self)
        self.cb2 = QCheckBox('16 bit AB2', self)
        self.cb3 = QCheckBox('16 bit BB1', self)
        self.cb4 = QCheckBox('16 bit BB2', self)
        self.cb5 = QCheckBox('24 bit AB1', self)
        self.cb6 = QCheckBox('24 bit AB2', self)
        self.cb7 = QCheckBox('24 bit BB1', self)
        self.cb8 = QCheckBox('24 bit BB2', self)

        self.start_time_label = QLabel(" Start time : ")
        self.start_hour = QSpinBox(self)
        self.start_hour.setRange(0, 24)
        self.start_hour.setSingleStep(1)
        self.start_hour.setSuffix("h")

        self.start_minute = QSpinBox(self)
        self.start_minute.setRange(0, 59)
        self.start_minute.setSingleStep(1)
        self.start_minute.setSuffix("m")

        self.start_second = QSpinBox(self)
        self.start_second.setRange(0, 59)
        self.start_second.setSingleStep(1)
        self.start_second.setSuffix("s")

        self.end_time_label = QLabel("                             End time  : ")
        self.end_hour = QSpinBox(self)
        self.end_hour.setRange(0, 24)
        self.end_hour.setSingleStep(1)
        self.end_hour.setSuffix("h")

        self.end_minute = QSpinBox(self)
        self.end_minute.setRange(0, 59)
        self.end_minute.setSingleStep(1)
        self.end_minute.setSuffix("m")

        self.end_second = QSpinBox(self)
        self.end_second.setRange(0, 59)
        self.end_second.setSingleStep(1)
        self.end_second.setSuffix("s")

        self.get_data_button = QPushButton("Get Data", self)
        self.get_data_button.clicked.connect(self.getData)

        self.analysis_qlabel = QLabel("Statistical Analysis", self)
        self.analysis_button = QPushButton("Start Analysis", self)
        self.analysis_button.clicked.connect(self.analysis)

        self.report_qlabel = QLabel("Write Error Report into TXT File")
        self.txt_button = QPushButton("TXT", self)
        self.txt_button.clicked.connect(self.txtFunc)

        self.step_number_qlabel = QLabel("Number of steps for given time range : ")
        self.step_number_txtbox = QLineEdit(self)
        self.step_button = QPushButton("Enter", self)
        self.step_button.clicked.connect(self.step_buttonFunc)

        self.csv_qlabel = QLabel("Write Datas into CSV files")
        self.csv_button = QPushButton("CSV", self)
        self.csv_button.clicked.connect(self.csvFunc)

        self.plot_qlabel = QLabel("Plot and Refresh")
        self.plot_button = QPushButton("Plot Data", self)
        self.plot_button.clicked.connect(self.refresh_plotFunc)
 
        self.pbar = QProgressBar(self)
        self.pbar.setValue(0)

    def refresh_plotFunc(self):

        global dataFrame_list
        self.plt.clear()

        if self.cb1.isChecked():

            plot_data = dataFrame_list[0]
            value_list = plot_data["intensity"]
            times = plot_data["time"]

            if len(value_list) > 0 and len(times) > 0: 
          
                time_list = []
                for time in times:
                    time_list.append(datetime.fromtimestamp(time))

                self.plt.plot(time_list, value_list, color = "blue", variable_name = "16bit_AB1")
            else:
                info_box = QMessageBox.information(self, "WARNING!", "There is no data for 16bit_AB1!")

        if self.cb2.isChecked():

            plot_data = dataFrame_list[1]
            value_list = plot_data["intensity"]
            times = plot_data["time"]
             
            if len(value_list) > 0 and len(times) > 0:  
         
                time_list = []
                for time in times:
                    time_list.append(datetime.fromtimestamp(time))

                self.plt.plot(time_list, value_list, color = "red", variable_name = "16bit_AB2")
            else:
                info_box = QMessageBox.information(self, "WARNING!", "There is no data for 16bit_AB2!")

        if self.cb3.isChecked():

            plot_data = dataFrame_list[2]
            value_list = plot_data["intensity"]
            times = plot_data["time"]

            if len(value_list) > 0 and len(times) > 0:  
         
                time_list = []
                for time in times:
                    time_list.append(datetime.fromtimestamp(time))

                self.plt.plot(time_list, value_list, color = "green", variable_name = "16bit_BB1")
            else:
                info_box = QMessageBox.information(self, "WARNING!", "There is no data for 16bit_BB1!")

        if self.cb4.isChecked():

            plot_data = dataFrame_list[3]
            value_list = plot_data["intensity"]
            times = plot_data["time"]

            if len(value_list) > 0 and len(times) > 0:  
         
                time_list = []
                for time in times:
                    time_list.append(datetime.fromtimestamp(time))

                self.plt.plot(time_list, value_list, color = "orange", variable_name = "16bit_BB2")
            else:
                info_box = QMessageBox.information(self, "WARNING!", "There is no data for 16bit_BB2!")

        if self.cb5.isChecked():

            plot_data = dataFrame_list[4]
            value_list = plot_data["intensity"]
            times = plot_data["time"]

            if len(value_list) > 0 and len(times) > 0:  
         
                time_list = []
                for time in times:
                    time_list.append(datetime.fromtimestamp(time))

                self.plt.plot(time_list, value_list, color = "pink", variable_name = "24bit_AB1")
            else:
                info_box = QMessageBox.information(self, "WARNING!", "There is no data for 24bit_AB1!")

        if self.cb6.isChecked():

            plot_data = dataFrame_list[5]
            value_list = plot_data["intensity"]
            times = plot_data["time"]

            if len(value_list) > 0 and len(times) > 0:  
         
                time_list = []
                for time in times:
                    time_list.append(datetime.fromtimestamp(time))

                self.plt.plot(time_list, value_list, color = "magenta", variable_name = "24bit_AB2")
            else:
                info_box = QMessageBox.information(self, "WARNING!", "There is no data for 24bit_AB2!")

        if self.cb7.isChecked():

            plot_data = dataFrame_list[6]
            value_list = plot_data["intensity"]
            times = plot_data["time"]

            if len(value_list) > 0 and len(times) > 0:  
         
                time_list = []
                for time in times:
                    time_list.append(datetime.fromtimestamp(time))

                self.plt.plot(time_list, value_list, color="aqua", variable_name = "24bit_BB1")
            else:
                info_box = QMessageBox.information(self, "WARNING!", "There is no data for 24bit_BB1!")

        if self.cb8.isChecked():

            plot_data = dataFrame_list[7]
            value_list = plot_data["intensity"]
            times = plot_data["time"]

            if len(value_list) > 0 and len(times) > 0:  
         
                time_list = []
                for time in times:
                    time_list.append(datetime.fromtimestamp(time))

                self.plt.plot(time_list, value_list, color="darkblue", variable_name = "24bit_BB2")
            else:
                info_box = QMessageBox.information(self, "WARNING!", "There is no data for 24bit_BB2!")
            
    def getStartdate(self):

        self.start_date1 =   str(start_date["start_year"]) + "-" + str(start_date["start_month"]) + "-" + str(start_date["start_day"])
        return self.start_date1

    def getEnddate(self):

        self.end_date1 = str(end_date["end_year"]) + "-" + str(end_date["end_month"]) + "-" + str(end_date["end_day"])
        return self.end_date1

    def startTimeFunc(self):

        hour = self.start_hour.value()
        minutes = self.start_minute.value()
        seconds = self.start_second.value()

        if hour <= 9:
            hour = "0" + str(hour)
        if minutes <= 9 :
            minutes = "0" + str(minutes)
        if seconds <= 9 :
            seconds = "0" + str(seconds)

        start_time = str(hour) + ":" + str(minutes) + ":" + str(seconds)
        return start_time

    def endTimeFunc(self):

        hour = self.end_hour.value()
        minutes = self.end_minute.value()
        seconds = self.end_second.value()

        if hour <= 9:
            hour = "0" + str(hour)
        if minutes <= 9 :
            minutes = "0" + str(minutes)
        if seconds <= 9 :
            seconds = "0" + str(seconds)

        end_time = str(hour) + ":" + str(minutes) + ":" + str(seconds)
        return end_time
        
    def getData(self):

        global variable_list
        global dataFrame_list
        self.result_list.clear()
        self.pbar.setValue(0) 
        self.result_list.addItem("Searching has started!")
        self.result_list.addItem("")
        end_date = self.getEnddate()
        start_date = self.getStartdate()
        start_time = self.startTimeFunc()
        end_time = self.endTimeFunc()

        self.tstart = start_date + " " + start_time
        time_dict["tstart"] = self.tstart
        self.tfinal = end_date + " " + end_time
        time_dict["tend"] = self.tfinal 

        t1 = pytimber.parsedate(self.tstart)
        t2 = pytimber.parsedate(self.tfinal)
        second_clicked['clicked'] = second_clicked['clicked'] + 1

        if t1 >= t2:

            info_box = QMessageBox.information(self, "WARNING!", "Start time must be before final time!")
            self.result_list.clear()

        else: 
            for num in range(len(variable_list)):

                time_list = []
                value_list = []
                data = db.get(variable_list[num], t1, t2) 
                timestamps, values = data[variable_list[num]] 
                time_list = list(timestamps) 
                value_list = list(values)
 
                if second_clicked['clicked'] > 1:
                    dataFrame_list[num] = pd.DataFrame({"time":[], "intensity":[]}, columns = ['time', 'intensity'])

                current_var = dataFrame_list[num]
                time_list = [int(i) for i in time_list]
                current_var["time"] = time_list
                current_var["intensity"] = value_list

            self.startSearching(self.tstart, self.tfinal)

    def startSearching(self, tstart, tend):

        global data_save_list
        global dataFrame_list

        ts = pytimber.parsedate(tstart)
        tf = pytimber.parsedate(tend)

        pbar_value = 0

        for count in range(len(dataFrame_list)):

            variable_name = "System Name : " + data_save_list[count]
            self.result_list.addItem(variable_name) 
            error_check["error"] = 2
            t1 = ts
            t2 = tf
            error = 3
            counter = 0
            error_start_list = []
            error_end_list = []
            
            data = dataFrame_list[count]
            time_list = list(data["time"].values)
  
            if len(time_list) != 0 and len(data["intensity"]) != 0:

                while True:
                   
                    if time_list[counter] != t1:
                        error = 1
                    else:
                        error = 0
                        if len(time_list) - 1 > counter:
                            counter += 1

                    if error_check["error"] != error and error == 1 :
                        error_check["error"] = error
                        error_start = datetime.fromtimestamp(t1).strftime('%Y-%m-%d %H:%M:%S')
                        error_start_for_list = "System blocked error started at : " + error_start
                        error_start_list.append(t1)
                        self.result_list.addItem(error_start_for_list)

                    if error_check["error"] != error and error == 0 and len(error_start_list) != 0:
                        error_check["error"] = error
                        error_end_list.append(t1)
                        error_finish = datetime.fromtimestamp(t1).strftime('%Y-%m-%d %H:%M:%S')
                        error_end_for_list = "System blocked error finished at : " + error_finish
                        self.result_list.addItem(error_end_for_list)
                         
                    t1 += 1

                    if t1 >= t2:
                        break
                    
                glitch_num = self.second_derivative(data["intensity"], error_start_list, error_end_list, t2)

                if glitch_num == 0:
                    message = "There are no glitch!"
                elif glitch_num < 0:
                    message = "There are no glitch!"
                else:
                    message = "There are " + str(glitch_num) + " glitches!"

                self.result_list.addItem(message)
                time_list = []
                data = 0

            else:
                self.result_list.addItem("There is no data!")

            if len(error_start_list) == 0:
                warning = "There is no system blocked error!"
                self.result_list.addItem(warning)  

            pbar_value += 12.5
            self.pbar.setValue(pbar_value)

    def std_calc(self, list_of_voltages):

        sum_square = 0
        summ = 0
        counter = 0
    
        for item in list_of_voltages:
        
            counter += 1
            sum_square += item**2
            summ += item
        
        value = abs(sum_square/counter - (summ/counter)**2)
    
        if value != 0:
            std = np.sqrt(value)
        else:
            std = 0
        
        return std 
    
    def analysis(self):

        global dataFrame_list
        path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        counter = 0

        for df in dataFrame_list:

            name = path + '\\' + data_save_list[counter]
            intensities = df['intensity']
            dydy = np.diff(np.diff(intensities))
            peaks, _ = find_peaks(dydy, height = 100000000000) 
            step_list = []
            zero_current = intensities[0:peaks[0]-120]
            step_list.append(zero_current) 
            
            for count in range(len(peaks) - 1):

                index1 = peaks[count]
                index2 = peaks[count + 1]
                step_range = (index1+120, index2-120)
                step = intensities[step_range[0]:step_range[1]]
                step_list.append(step)  

            zero_current2 = intensities[peaks[-1]+120::] 
            step_list.append(zero_current2) 

            mean_list = []
            for step in step_list:
                mean_list.append(np.mean(step))

            std_list = []
            for step in step_list:
                std_list.append(self.std_calc(step))

            max_list = []
            for step in step_list:
                max_list.append(max(step))

            min_list = []
            for step in step_list:
                min_list.append(min(step))

            pp_list = []
            for step in step_list:
                pp_list.append(max(step)-min(step))

            step_num_list = []
            for count in range(len(step_list)):
                step_num_list.append(count)

            features = ['steps', 'mean', 'standard deviation', 'minumum', 'maximum', 'peak-to-peak']
            dictionary = {'steps':step_num_list, "mean":mean_list, 'standard deviation':std_list, "minumum":min_list, 'maximum':max_list, 'peak-to-peak':pp_list}
            df = pd.DataFrame(dictionary, columns = features)
            df.to_csv(name + '_statistical_results.csv', index = False, header = True)
            counter += 1  
        
        success = "Statistical analysis files created succesfully!"
        self.result_list.addItem(success)              

    def second_derivative(self, intensity_list, error_slist, error_elist, tf):

        dydy = np.diff(np.diff(intensity_list))
        peaks, _ = find_peaks(dydy, height = 100000000000)
        step_num = 0
        
        if len(error_slist) != 0 and len(error_elist) != 0:

            if len(error_slist) != len(error_elist):
                error_elist.append(tf)

            for index in range(len(error_slist)):

                time_diff = error_elist[index] - error_slist[index]
                app_step_num = round(time_diff / 3600)
                step_num += app_step_num
                
        glitch_num = len(peaks) - step_number['step_number'] + step_num - 1

        return glitch_num

    def txtFunc(self):

        path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        file1 = open(path + "\\errors.txt","w")  
        file1.write("Errors list between " + str(time_dict["tstart"]) + " and " + str(time_dict["tend"]) + " \n")

        for index in range(self.result_list.count()):
            error = self.result_list.item(index).text()
            file1.write(str(error) + " \n")

        file1.close()
        success = "TXT error file created succesfully!"
        self.result_list.addItem(success)

    def step_buttonFunc(self):
        step_number['step_number'] = int(self.step_number_txtbox.text())
    
    def csvFunc(self):

        path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
        global dataFrame_list
        global variable_list

        for i in range(len(dataFrame_list)):

            name = path + "\\" + str(variable_list[i]) + ".csv"
            data = dataFrame_list[i]
            time_list = data["time"]
            value_list = data["intensity"]

            time_list_for_csv = []
            for time in time_list:
                time_list_for_csv.append(datetime.fromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S'))

            data_dict = {"time":time_list_for_csv, "intensity":value_list}
            data_frame = pd.DataFrame(data_dict)
            data_frame.to_csv(name, index = False, header = True)

        success = "CSV files created succesfully!"
        self.result_list.addItem(success)        

    def layouts(self):

        self.mainlayout = QHBoxLayout()
        self.leftlayout = QFormLayout()
        self.rightlayout = QFormLayout()
        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.left_hbox1 = QHBoxLayout()
        self.left_hbox2 = QHBoxLayout()
        self.left_vbox1 = QVBoxLayout()
        self.left_hbox3 = QHBoxLayout()
        self.left_hbox4 = QHBoxLayout()
        self.left_hbox5 = QHBoxLayout()
        self.right_hbox = QHBoxLayout()
        self.plot_layout = QVBoxLayout()

        self.rightlayoutGroupBox = QGroupBox("Plot")
        self.hbox1.addWidget(self.cb1)
        self.hbox1.addWidget(self.cb2)
        self.hbox1.addWidget(self.cb3)
        self.hbox1.addWidget(self.cb4)
        self.rightlayout.addRow(QLabel("16 Bit Adc Variables:"), self.hbox1)
        
        self.hbox2.addWidget(self.cb5)
        self.hbox2.addWidget(self.cb6)
        self.hbox2.addWidget(self.cb7)
        self.hbox2.addWidget(self.cb8)
        self.rightlayout.addRow(QLabel("24 Bit Adc Variables:"), self.hbox2)
        
        self.right_hbox.addWidget(self.plot_qlabel)
        self.right_hbox.addWidget(self.plot_button)
        self.right_hbox.addStretch()
        self.plot_layout.addWidget(self.toolbar)
        self.plot_layout.addWidget(self.plt)
        self.rightlayout.addRow(self.plot_layout)        
        self.rightlayout.addRow(self.right_hbox)
        self.rightlayoutGroupBox.setLayout(self.rightlayout)

        self.leftlayoutGroupBox = QGroupBox("Error Check")
        self.left_hbox1.addWidget(self.calendar1)
        self.left_hbox1.addStretch()
        self.left_hbox1.addWidget(self.start_time_label)
        self.left_hbox1.addWidget(self.start_hour)
        self.left_hbox1.addWidget(self.start_minute)
        self.left_hbox1.addWidget(self.start_second)
        self.left_hbox1.addStretch()
        self.leftlayout.addRow(QLabel("Start Date:"), self.left_hbox1)
        
        self.left_hbox2.addWidget(self.calendar2)
        self.left_hbox2.addStretch()
        self.left_hbox2.addWidget(self.end_time_label)
        self.left_hbox2.addWidget(self.end_hour)
        self.left_hbox2.addWidget(self.end_minute)
        self.left_hbox2.addWidget(self.end_second)
        self.left_hbox2.addStretch()
        self.left_hbox2.addWidget(self.get_data_button)
        self.leftlayout.addRow(QLabel("Final Date:"), self.left_hbox2)
        
        self.left_hbox5.addWidget(self.step_number_qlabel)
        self.left_hbox5.addWidget(self.step_number_txtbox)
        self.left_hbox5.addWidget(self.step_button)
        self.left_hbox5.addStretch()
        self.left_hbox5.addWidget(self.analysis_qlabel)
        self.left_hbox5.addWidget(self.analysis_button)
        self.leftlayout.addRow(self.left_hbox5)

        self.left_vbox1.addWidget(self.result_list) 
        self.leftlayout.addRow(self.left_vbox1) 
        
        self.left_hbox4.addWidget(self.pbar)
        self.leftlayout.addRow(self.left_hbox4)        
        
        self.left_hbox3.addWidget(self.csv_qlabel)
        self.left_hbox3.addWidget(self.csv_button)
        self.left_hbox3.addStretch()
        self.left_hbox3.addWidget(self.report_qlabel)
        self.left_hbox3.addWidget(self.txt_button)
        self.leftlayout.addRow(self.left_hbox3)

        self.leftlayoutGroupBox.setLayout(self.leftlayout)
    
        self.mainlayout.addWidget(self.leftlayoutGroupBox, 50)
        self.mainlayout.addWidget(self.rightlayoutGroupBox, 50)
        self.tab1.setLayout(self.mainlayout)

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=10, height=8, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self, x, y, color, variable_name):

        ax = self.figure.add_subplot(111)
        ax.plot(x, y, color = color, label = variable_name)
        ax.set_xlabel("Time")
        ax.set_ylabel("Beam intensity")
        plt.grid('on')
        ax.legend()

        if len(x) <= 86400:
            xfmt = mdates.DateFormatter('%H:%M')
        else:
            xfmt = mdates.DateFormatter('%m-%d %H:%M')

        ax.xaxis.set_major_formatter(xfmt)
        self.fig.autofmt_xdate()
        self.draw()

    def clear(self):

        self.fig.clf()

class DateEdit1(QDateEdit):

    def __init__(self, parent = None):

        super().__init__(parent, calendarPopup = True)
        self.calendarWidget().setGridVisible(True)
        today = QDate.currentDate()
        self.calendarWidget().setSelectedDate(today)
        self.calendarWidget().clicked.connect(self.printDateInfo)

    def printDateInfo(self, QDate):

        start_date["start_day"] = QDate.day()
        start_date["start_month"]  = QDate.month()
        start_date["start_year"]  = QDate.year()

class DateEdit2(QDateEdit):

    def __init__(self, parent = None):

        super().__init__(parent, calendarPopup = True)
        self.calendarWidget().setGridVisible(True)
        today = QDate.currentDate()
        self.calendarWidget().setSelectedDate(today)
        self.calendarWidget().clicked.connect(self.printDateInfo)

    def printDateInfo(self, QDate):

        end_date["end_day"] = QDate.day()
        end_date["end_month"] = QDate.month()
        end_date["end_year"] = QDate.year()

def main():

    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())

if __name__ == "__main__":

    main()