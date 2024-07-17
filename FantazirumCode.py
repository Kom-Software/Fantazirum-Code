from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from threading import *
from PyQt5.QtCore import Qt

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
        super(Window, self).__init__()

        self.menuBar = None
        font  = QFont("Consolas", 15)

        self.setWindowTitle("Fantazirum Code")
        self.setWindowIcon(QtGui.QIcon("spacetext.png"))
        self.setStyleSheet("background-color: rgb(40, 40, 40); color: rgb(255, 255, 255)")
        self.setFixedSize(1000, 500)

        self.text_edit = QtWidgets.QTextEdit(self)
        self.text_edit.setStyleSheet('background-color: rgb(58, 58, 58); color: rgb(255, 255, 255)')
        self.text_edit.setFont(font)
        self.setCentralWidget(self.text_edit)

        self.highlighter = Highlighter()
        self.highlightSettings()
        self.thread()

        self.createMenuBar()

    def createMenuBar(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        fileMenu = QMenu("&Файл", self)
        self.menuBar.addMenu(fileMenu)
        projectMenu = QMenu("&Проект", self)
        self.menuBar.addMenu(projectMenu)

        fileMenu.addAction('Открыть', self.action_clicked)
        fileMenu.addAction('Сохранить', self.action_clicked)

        projectMenu.addAction('Запустить', self.action_clicked)


    @QtCore.pyqtSlot()
    def action_clicked(self):
        action = self.sender()
        if action.text() == "Открыть":
            filter = "Space Text Files (*.spct)"
            filename = QFileDialog.getOpenFileName(self, filter=filter)[0]

            try:
                f = open(filename, 'r')
                with f:
                    data = f.read()
                    self.text_edit.setText(data)

                f.close()
            except FileNotFoundError:
                print("No such file")

        elif action.text() == "Сохранить":
            filter = "Space Text Files (*.spct)"
            filename = QFileDialog.getSaveFileName(self, filter=filter)[0]

            try:
                f = open(filename, 'w')
                text = self.text_edit.toPlainText()
                f.write(text)
                f.close()
            except FileNotFoundError:
                print("No such file")

        elif action.text() == "Запустить":
            program = self.text_edit.toPlainText()
            interpreter.interpret(program)


    def highlightSettings(self):

        pattern = [r'console.get', r'console.say', r'".+?"', r'#.*$', r'ent', r'=', r'bool', r'\d']

        for p in pattern:

            if p == r'console.say':
                self.highlighter.add_mapping(p, QColor(155,42,192)) 
            elif p == r'console.get':
                self.highlighter.add_mapping(p, QColor(155,42,192))
            elif p == r'".+?"':
                self.highlighter.add_mapping(p, QColor(0, 255, 0))
            elif p == r'#.*$':
                parameters = QTextCharFormat()
                parameters.setForeground(QColor(12,146,7))
                parameters.setFontItalic(True)
                self.highlighter.add_mapping(p, parameters)
            elif p == r'ent':
                self.highlighter.add_mapping(p, QColor(42,245,248))
            elif p == r'=':
                self.highlighter.add_mapping(p, QColor(17,115,176))
            elif p == r'bool':
                self.highlighter.add_mapping(p, QColor(42,245,248))

            self.highlighter.setDocument(self.text_edit.document())

class MainInterpreter:
    def __init__(self):
        self.console = {}
        self.functions = {}

    def interpret(self, program):
        lines = program.split("\n")
        for line in lines:

            if line.startswith("console.say"):
                parts = line.split(" ")
                if parts[1] in self.console:
                    print(self.console[parts[1]])
                elif parts[1].startswith('"') and parts[1].endswith('"'):
                    print(parts[1])
                else:
                    print("Ошибка 100: Переменная без значения: " + parts[1])

            elif line.startswith("console.get"):
                parts = line.split(" ")
                if len(parts) == 2:
                    print(f"{self.console.get(parts[1])}")
                else:
                    print("Ошибка 200: Неправильное построение. Имели вы в виду: console.get название_переменной?")

            elif line.startswith("ent"):
                parts = line.split(" ")
                if len(parts) == 4:  # проверка на то, что, правильно ли пользователь указал построение? (тип название значение)
                    if parts[2] == "=":
                        try:
                            self.console[parts[1]] = int(parts[3])
                        except:
                            print(
                                'Ошибка 101: Неверное значение числовой переменной. Значение должно быть целым и от -2 147 483 648 до 2 147 483 647.')
                    else:
                        print("Ошибка 300: Неверный знак присвоения или сравнения.")
                else:
                    print("Ошибка 201: Неправильное построение. Имели вы в виду: тип название = значение?")

            elif line.startswith("frac"):
                parts = line.split(" ")
                if len(parts) == 4:  # проверка на то, что, правильно ли пользователь указал построение? (тип название значение)
                    if parts[2] == "=":
                        try:
                            self.console[parts[1]] = float(parts[3])
                        except:
                            print(
                                "Ошибка 102: Неправильное значение числовой переменной. Значение должно быть дробным и от -3.4028235E+38 до 3.4028235E+38.")
                    else:
                        print("Ошибка 300: Неверный знак присвоения или сравнения.")
                else:
                    print("Ошибка 201: Неправильное построение. Имели вы в виду: тип название = значение?")

            elif line.startswith("lin"):
                parts = line.split(" ")
                if len(parts) == 4:  # проверка на то, что, правильно ли пользователь указал построение? (тип название значение)
                    if parts[2] == "=":
                        if parts[3].startswith('"') and parts[3].endswith('"'):
                            try:
                                self.console[parts[1]] = str(parts[3])
                            except:
                                print(
                                    "Ошибка 103: Неверное значение строчной переменной. Значение должно состоять из букв и цифр.")
                    else:
                        print("Ошибка 300: Неверный знак присвоения или сравнения.")
                else:
                    print("Ошибка 201: Неправильное построение. Имели вы в виду: тип название = значение?")

            elif line.startswith("bool"):
                parts = line.split(" ")
                if len(parts) == 4:  # проверка на то, что, правильно ли пользователь указал построение? (тип название значение)
                    if parts[2] == "=":
                        if parts[3] == "true":
                            self.console[parts[1]] = True
                        elif parts[3] == "false":
                            self.console[parts[1]] = False
                        else:
                            print(
                                "Ошибка 104: Неверное значение булевой переменной. Оно должно равняться 'true' или 'false'.")
                    else:
                        print("Ошибка 300: Неверный знак присвоения или сравнения.")
                else:
                    print("Ошибка 201: Неправильное построение. Имели вы в виду: тип название = значение?")

            elif line.startswith("start"):
                pass

            elif line.startswith("FD"):
                print(f"P: {program}")
                print(f"L: {lines}")
                print(f"C: {self.console}")
                print("!WARNING! FD-Mode in beta test, if you find bug(s) write me on GitHub")

            else:
                print("Ошибка: Неизвестная команда.")

interpreter = MainInterpreter()

def application():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = Window()

    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    application()
