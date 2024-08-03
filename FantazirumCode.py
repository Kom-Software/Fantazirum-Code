from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys
import re

class Highlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._mapping = {}

    def add_mapping(self, pattern, pattern_format):
        self._mapping[pattern] = pattern_format

    def highlightBlock(self, text_block):
        for pattern, fmt in self._mapping.items():
            for match in re.finditer(pattern, text_block):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.intepret: MainInterpreter

        self.menuBar = None
        font  = QFont("Consolas", 15)

        self.setWindowTitle("Fantazirum Code")
        self.setWindowIcon(QtGui.QIcon("FR code.png"))
        self.setStyleSheet("background-color: rgb(40, 40, 40); color: rgb(255, 255, 255)")
        self.setFixedSize(1000, 500)
        self.centralwidget = QtWidgets.QWidget(self)

        self.code_edit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.code_edit.setStyleSheet('background-color: rgb(58, 58, 58); color: rgb(255, 255, 255)')
        self.code_edit.setFont(font)
        self.code_edit.setGeometry(QtCore.QRect(10, 0, 750, 470))
        self.console_edit = QtWidgets.QTextEdit(self.centralwidget)
        self.console_edit.setGeometry(QtCore.QRect(770, 0, 221, 470))
        self.console_edit.setStyleSheet('background-color: rgb(58, 58, 58); color: rgb(255, 255, 255)')
        self.console_edit.setFont(font)
        self.console_edit.setReadOnly(True)
        self.setCentralWidget(self.centralwidget)

        self.highlighter = Highlighter()
        self.highlightSettings()
        self.thread()

        self.createMenuBar()

    def createMenuBar(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        fileMenu = QMenu("&File", self)
        self.menuBar.addMenu(fileMenu)
        projectMenu = QMenu("&Project", self)
        self.menuBar.addMenu(projectMenu)

        fileMenu.addAction('Open', self.action_clicked)
        fileMenu.addAction('Save', self.action_clicked)

        projectMenu.addAction('Run', self.action_clicked)


    @QtCore.pyqtSlot()
    def action_clicked(self):
        action = self.sender()
        if action.text() == "Open":
            filter = "Fantazirum Files (*.frt)"
            filename = QFileDialog.getOpenFileName(self, filter=filter)[0]

            try:
                f = open(filename, 'r')
                with f:
                    data = f.read()
                    self.text_edit.setText(data)

                f.close()
            except FileNotFoundError:
                print("No such file")

        elif action.text() == "Save":
            filter = "Fantazirum Files (*.frt)"
            filename = QFileDialog.getSaveFileName(self, filter=filter)[0]

            try:
                f = open(filename, 'w')
                text = self.text_edit.toPlainText()
                f.write(text)
                f.close()
            except FileNotFoundError:
                print("No such file")

        elif action.text() == "Run":
            program = self.code_edit.toPlainText()
            self.intepret.before_interpret(program)
    def highlightSettings(self):

        pattern = [r'console.get', r'console.say', r'feature', r'ent', r'bool', r'frac', r'lin', r'".+?"', r'#.*$', r'\d', r'\d\.\d', r'{', r'}']

        for p in pattern:

            if p == r'console.say':
                self.highlighter.add_mapping(p, QColor(48,213,200))
            elif p == r'console.get':
                self.highlighter.add_mapping(p, QColor(48,213,200))
            elif p == r'feature':
                self.highlighter.add_mapping(p, QColor(255,201,128))
            elif p == r'".+?"':
                self.highlighter.add_mapping(p, QColor(159,239,170))
            elif p == r'#.*$':
                parameters = QTextCharFormat()
                parameters.setForeground(QColor(12,146,7))
                parameters.setFontItalic(True)
                self.highlighter.add_mapping(p, parameters)
            elif p == r'ent':
                self.highlighter.add_mapping(p, QColor(42,245,248))
            elif p == r'bool':
                self.highlighter.add_mapping(p, QColor(42,245,248)) 
            elif p == r'frac':
                self.highlighter.add_mapping(p, QColor(42,245,248))
            elif p == r'lin':
                self.highlighter.add_mapping(p, QColor(42,245,248))
            elif p == r'\d':
                self.highlighter.add_mapping(p, QColor(210,252,198))
            elif p == r'\d\.\d':
                self.highlighter.add_mapping(p, QColor(42,60,248))
            elif p == r'{':
                self.highlighter.add_mapping(p, QColor(127,199,255))
            elif p == r'}':
                self.highlighter.add_mapping(p, QColor(127,199,255))

            self.highlighter.setDocument(self.code_edit.document())

    def write(self, data):
        data = data
        self.console_edit.append(str(data))

    def setInterpret(self, data):
        self.intepret = data

class MainInterpreter:
    def __init__(self):
        self.console = {}
        self.functions = {}
        self.window: Window

    def setWindow(self, data):
        self.window = data

    def before_interpret(self, program):
        lines = program.split("\n")
        for line in lines:
            if re.fullmatch(r'feature .+?', line):
                index = lines.index(line)
                dataParts = line.split(" ")
                self.functions[dataParts[1]] = ""
                self.functions[dataParts[1]] += ""
                index += 1
                if lines[index] == '{':
                    lines[index] = ''
                    while lines[index] != '}':
                        index = index + 1
                        if lines[index] == '}':
                            lines[index] = ''
                            break
                        self.functions[dataParts[1]] += lines[index] + '\n'
                        lines[index] = ''
        self.interpret(lines)
            

    def interpret(self, data):
        lines = data
                    
        for line in lines:
            
            if re.fullmatch(r'ent .+? = .+?', line):
                parts = line.split(" ")
                try:
                    self.console[parts[1]] = int(parts[3])
                except:
                    print(
                    'Ошибка 101: Неверное значение числовой переменной. Значение должно быть целым и от -2 147 483 648 до 2 147 483 647.')

            elif re.fullmatch(r'frac .+? = .+?', line):
                parts = line.split(" ")
                try:
                    self.console[parts[1]] = float(parts[3])
                except:
                    print(
                    'Ошибка 102: Неправильное значение числовой переменной. Значение должно быть дробным и от -3.4028235E+38 до 3.4028235E+38.')

            elif re.fullmatch(r'bool .+? = .+?', line):
                parts = line.split(" ")
                try:
                    if parts[3] == "true":
                        self.console[parts[1]] = True
                    elif parts[3] == "false":
                        self.console[parts[1]] = False
                    else:
                        print(
                        'Ошибка 104: Неверное значение булевой переменной. Оно должно равняться "true" или "false".')
                except:
                    print(
                    'Ошибка 201: Неправильное построение. Имели вы в виду: тип название = значение?')

            elif re.fullmatch(r'lin .+? = ".+?"', line):
                parts = line.split(" ")
                lin_parts = line.split('"')
                try:
                    self.console[parts[1]] = lin_parts[1]
                except:
                    print(
                    'Ошибка 103: Неверное значение строчной переменной. Значение должно состоять из букв и цифр.')

            elif re.fullmatch(r'console.say ".+?"', line):
                console_lin_parts = line.split('"')
                if re.match(r'.+?', console_lin_parts[1]):
                    self.window.write(console_lin_parts[1])
                else:
                    print(
                    'Ошибка 300')

            elif re.fullmatch(r'console.say .+?', line):
                parts = line.split(" ")
                if parts[1] in self.console:
                    self.window.write(self.console[parts[1]])
                else:
                    print(
                    'Ошибка 100: Не найденная переменная: ' + parts[1])

            elif re.fullmatch(r'console.get .+?', line):
                parts = line.split(" ")
                if parts[1] in self.console:
                    self.window.write('true')
                else:
                    self.window.write('false')

            elif re.fullmatch(r'.+?\(\)', line):
                keys = self.functions.keys()
                parts = line.split("(")
                if parts[0] in keys:
                    i = self.functions[parts[0]].split("\n")
                    self.interpret(i)

def application():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    interpreter = MainInterpreter()
    window = Window()
    window.setInterpret(interpreter)
    interpreter.setWindow(window)

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    application()
