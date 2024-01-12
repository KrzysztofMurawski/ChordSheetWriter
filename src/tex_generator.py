import tempfile
from music_sheet_elements import *


class TexGenerator:
    def __init__(self, metadata: dict, song: list[list]):
        self.tmp_file = tempfile.NamedTemporaryFile("a+t")
        self.metadata = metadata
        self.song = song

    def generate_temp_tex_file(self):
        self.write_preamble_to_file()
        self.begin_document()
        self.write_title_and_author()
        self.write_metadata()
        self.centering()
        self.begin_table()
        self.generate_table_content()
        self.end_table()
        self.end_document()
        self.tmp_file.seek(0)

    def begin_table(self):
        columns_number, index = self.get_max_columns_per_line()
        self.tmp_file.write(f"\\begin{{tabularx}}{{\\textwidth}}{{{self.get_column_types(index)}}} \n")

    def generate_table_content(self):
        for line in self.song:
            self.write_table_line_to_file(line)

    def write_table_line_to_file(self, line):
        time_signature = False
        elements_tex_codes = []
        for element in line:
            if isinstance(element, TimeSignature):
                time_signature = True
            elements_tex_codes.append(element.get_tex_code())
        if time_signature:
            self.tmp_file.write(" & ".join(elements_tex_codes) + " \\\\ \n")
        else:
            self.tmp_file.write(" & " + " & ".join(elements_tex_codes) + " \\\\ \n")

    def end_table(self):
        self.tmp_file.write("\\end{tabularx}\n\n")

    def get_column_types(self, max_column_index):
        columns = []
        for element in self.song[max_column_index]:
            if isinstance(element, BarChords):
                columns += ["C"]*len(element.chords)
            else:
                columns += ["B"]
        return " ".join(columns)

    def get_max_columns_per_line(self):
        max_columns = 0
        index = 0
        for i, line in enumerate(self.song):
            cols = 0
            for el in line:
                if isinstance(el, BarChords):
                    cols += len(el.chords)
                else:
                    cols += 1
            if cols > max_columns:
                max_columns = cols
                index = i
        return max_columns, index

    def write_preamble_to_file(self):
        with open("../resources/preamble.txt") as file:
            lines = file.readlines()
        for line in lines:
            self.tmp_file.write(line)

    def write_title_and_author(self):
        self.tmp_file.write(
            f"\\LARGE {self.metadata['title']} \\hfill  {self.metadata['author']} \\newline\\tiny\\newline\\small \n")

    def write_metadata(self):
        if self.metadata.get("key") != "N/A":
            self.tmp_file.write(f"\\hfill Key: {self.metadata.get('key')} \\hfill")

        if self.metadata.get("chords") != "N/A":
            self.tmp_file.write(
                f"\\hfill Chords: {'\\hspace{0.2cm} '.join(['\\writechord{' + chord.replace("#", "\\#") + '}' 
                                                            for chord in self.metadata.get('chords')])} \\hfill")

        if self.metadata.get("capo") != "N/A":
            self.tmp_file.write("\\hfill " + self.parse_capo() + " \\hfill ")

        if self.metadata.get("tempo") != "N/A":
            self.tmp_file.write(" \\hfill Tempo: " + self.metadata.get("tempo"))

        self.tmp_file.write("\\newline\\rule{\\linewidth}{0.3pt}\\newline \n\n")

    def begin_document(self):
        self.tmp_file.write("\\begin{document} \n")

    def end_document(self):
        self.tmp_file.write("\\end{document} \n")

    def parse_capo(self):
        match self.metadata.get("capo", 0):
            case "1":
                return "\\hfill Capo: 1\\textsuperscript{st} fret \\hfill"
            case "2":
                return "\\hfill Capo: 2\\textsuperscript{nd} fret \\hfill"
            case "3":
                return "\\hfill Capo: 1\\textsuperscript{rd} fret \\hfill"
            case num:
                return f"\\hfill Capo: {num}\\textsuperscript{{th}} fret \\hfill"

    def centering(self):
        self.tmp_file.write("\n \\centering \n\n")