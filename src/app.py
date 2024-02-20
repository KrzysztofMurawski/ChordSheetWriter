import os
import sys
import subprocess
from tex_generator import TexGenerator
from input_parser import InputParser
from config_provider import config
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt


def create_separator():
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.VLine)
    return separator


def show_error_message(text="ERROR"):
    msg = QMessageBox()
    msg.setWindowTitle("ERROR")
    msg.setText(text)
    msg.setIcon(QMessageBox.Icon.Information)
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


def validate_tex_syntax(tex_file_path):
    command = "lacheck " + tex_file_path
    result = subprocess.getoutput(command)
    return result


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.project_name = "unnamedproject"

        self.setWindowTitle("ChordSheetWriter")
        self.setMinimumSize(int(config.get("gui", "main_window_width")), int(config.get("gui", "main_window_height")))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)
        central_widget.setLayout(self.layout)

        self.tool_bar = QHBoxLayout()
        self.tool_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        button_size = int(config.get("gui", "toolbar_button_size"))

        self.save_button = QPushButton(QIcon("../resources/icons/save.png"), "", self)
        self.save_button.setFixedSize(button_size, button_size)
        self.tool_bar.addWidget(self.save_button)

        self.load_button = QPushButton(QIcon("../resources/icons/load.png"), "", self)
        self.load_button.setFixedSize(button_size, button_size)
        self.tool_bar.addWidget(self.load_button)

        self.start_button = QPushButton(QIcon("../resources/icons/start.png"), "", self, clicked=self.generate_pdf)
        self.start_button.setFixedSize(button_size, button_size)
        self.tool_bar.addWidget(self.start_button)

        self.tool_bar.addWidget(create_separator())

        self.undo_button = QPushButton(QIcon("../resources/icons/undo.png"), "", self)
        self.undo_button.setFixedSize(button_size, button_size)
        self.tool_bar.addWidget(self.undo_button)

        self.redo_button = QPushButton(QIcon("../resources/icons/redo.png"), "", self)
        self.redo_button.setFixedSize(button_size, button_size)
        self.tool_bar.addWidget(self.redo_button)

        self.tool_bar.addWidget(create_separator())

        self.settings_button = QPushButton(QIcon("../resources/icons/settings.png"), "", self)
        self.settings_button.setFixedSize(button_size, button_size)
        self.tool_bar.addWidget(self.settings_button)

        self.layout.addLayout(self.tool_bar)

        self.text_input = QTextEdit()
        self.layout.addWidget(self.text_input)

        self.show()

    def generate_pdf(self):
        input_content = [line for line in self.text_input.toPlainText().splitlines() if line != "" and line[0] not in "#%$"]
        print("Read input")

        parser = InputParser(input_content)
        print("Parser initialized")

        try:
            metadata, parsed_song = parser.parse()
        except Exception:
            print("Can't parse input")
            show_error_message("Invalid syntax. Unable to compile")
            return
        else:
            print("Input parsed")

        tex_generator = TexGenerator(metadata, parsed_song)
        print("Tex generator initialilzed")

        parse_and_tex_generation_success = tex_generator.generate_temp_tex_file()
        print("Temporary file generated")

        os.chdir("../")

        with open(f"{self.project_name}.tex", "w") as tex_file:
            tex_file.write(tex_generator.tmp_file.read())
        print("Tex file generated")

        if parse_and_tex_generation_success:
            err_code = os.system(f"pdflatex -interaction=nonstopmode {self.project_name}.tex")
            print(err_code)
            if err_code != 0:
                show_error_message("Invalid syntax. Unable to compile")

            os.system(f"del {self.project_name}.aux")
            os.system(f"del {self.project_name}.tex")
            os.system(f"del {self.project_name}.log")
        else:
            show_error_message("Invalid syntax. Unable to compile")
        os.chdir("src/")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
