import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from sqlalchemy import create_engine
from CalculateDescriptor import calculate
from ScheduleParser import parse_lesson as pl
import json


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()

    def init_main(self):
        btn_start_work = ttk.Button(text='Начать работу', command=self.open_lesson_information_form)
        btn_start_work.place(x=150, y=50)

        btn_add_student = ttk.Button(text='Добавить студента', command=self.open_add_student_form)
        btn_add_student.place(x=150, y=80)

        btn_add_group = ttk.Button(text='Добавить группу', command=self.open_add_group_form )
        btn_add_group.place(x=150, y=110)

        '''btn_show_group = ttk.Button(text='Просмотреть группы', command=self.open_show_group_form)
        btn_show_group.place(x=150, y=140)'''

    def open_add_group_form(self):
        AddGroupForm()

    def open_add_student_form(self):
        AddStudentForm()

    def open_lesson_information_form(self):
        LessonInformationForm()

    '''def open_show_group_form(self):
        ShowGroupForm()'''


'''class ShowGroupForm(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_show_group_form()

    def init_show_group_form(self):
        self.title("Показать группу")
        self.geometry("400x220+400+300")
        self.resizable(False, False)

        label_description = tk.Label(self, text='Название группы:')
        label_description.place(x=50, y=50)

        self.combobox_groups = ttk.Combobox(self, values=[u'8И5А', u'1263'])  # Добавить заполнение вариантов из БД
        self.combobox_groups.current(0)
        self.combobox_groups.place(x=200, y=50)

        self.tree = ttk.Treeview(self, columns=("ID", "Name"), height=10, show="headings")

        self.tree.column("ID", width=55, anchor=tk.E)
        self.tree.column("Name", width=150, anchor=tk.E)

        self.tree.heading("ID", text="Номер")
        self.tree.heading("Name", text="Фамилия Имя")

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.place(x=30, y=50)

        self.tree.pack()

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=300, y=170)

        btn_ok = ttk.Button(self, text='Показать', command=lambda: self.show_group())  # Скобки
        btn_ok.place(x=220, y=170)

        self.grab_set()
        self.focus_set()'''

class AddGroupForm(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_add_group_form()

    def init_add_group_form(self):
        self.title("Добавить группу")
        self.geometry("400x220+400+300")
        self.resizable(False, False)

        label_description = tk.Label(self, text='Название группы:')
        label_description.place(x=50, y=50)

        self.entry_group_name = ttk.Entry(self)
        self.entry_group_name.place(x=200, y=50)

        btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        btn_cancel.place(x=300, y=170)

        btn_ok = ttk.Button(self, text='Добавить', command=lambda: self.get_arguments())
        btn_ok.place(x=220, y=170)

        self.grab_set()
        self.focus_set()

    def get_arguments(self):
        group_name = str(self.entry_group_name.get())
        self.add_group(group_name)

    def add_group(self, group_name):
        connection_string = "postgresql+psycopg2://admin:password@localhost/student_control"

        engine = create_engine(connection_string)

        query = "INSERT INTO studygroup (name) VALUES ('{0}')".format(group_name)

        try:
            engine.execute(query)

        except BaseException as e:
            print("Query error: {}".format(e))


class AddStudentForm(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_add_student_form()

    def init_add_student_form(self):
        self.title("Добавить студента")
        self.geometry("400x300+400+300")
        self.resizable(False, False)

        self.label_name = tk.Label(self, text='Фамилия и имя:')
        self.label_name.place(x=50, y=50)

        self.entry_name = ttk.Entry(self)
        self.entry_name.place(x=200, y=50)

        self.label_group = tk.Label(self, text='Группа:')
        self.label_group.place(x=50, y=80)

        self.combobox_group = ttk.Combobox(self, values=[u'8И5А', u'1263'])  # Добавить заполнение вариантов из БД
        self.combobox_group.current(0)
        self.combobox_group.place(x=200, y=80)

        self.label_photo = tk.Label(self, text='Фотография:')
        self.label_photo.place(x=50, y=110)

        self.btn_open_photo = ttk.Button(self, text='Открыть фото', command=lambda: self.download_photo())
        self.btn_open_photo.place(x=200, y=110)

        self.label_photo_container = tk.Label(self, text='Здесь будет имя файла')
        self.label_photo_container.place(x=50, y=140)

        self.btn_cancel = ttk.Button(self, text='Закрыть', command=self.destroy)
        self.btn_cancel.place(x=300, y=170)

        self.btn_ok = ttk.Button(self, text='Добавить', command=lambda: self.get_arguments())
        self.btn_ok.place(x=220, y=170)

        self.grab_set()
        self.focus_set()

    def download_photo(self):
        file_name = fd.askopenfilename(filetypes=(("JPEG files", "*.jpg"),
                                                    ("PNG files", "*.png")))
        self.label_photo_container.config(text=file_name)
        return file_name

    def get_arguments(self):
        student_name = str(self.entry_name.get())
        student_group = str(self.combobox_group.get())
        student_photo_path = str(self.label_photo_container.cget('text'))
        self.add_student(student_name, student_group, student_photo_path)

    def add_student(self, student_name, student_group, student_photo_path):
        connection_string = "postgresql+psycopg2://admin:password@localhost/student_control"

        engine = create_engine(connection_string)

        descriptor = calculate(student_photo_path)

        get_group_query = "SELECT id FROM studygroup WHERE name = '{0}'".format(student_group)
        data = engine.execute(get_group_query)

        group_id = ''

        for item in data:
            group_id = str(item[0])

        insert_query = "INSERT INTO student (name, descriptor, groupid) VALUES ('{0}', '{1}', '{2}')"\
            .format(student_name, descriptor, group_id)

        try:
            engine.execute(insert_query)

        except BaseException as e:
            print("Query error: {}".format(e))


class LessonInformationForm(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_lesson_information_form()

    def init_lesson_information_form(self):
        self.title("Информация о занятии")
        self.geometry("400x220+400+300")
        self.resizable(False, False)

        label_corps = tk.Label(self, text='Выберете корпус:')
        label_corps.place(x=50, y=50)

        self.combobox_corps = ttk.Combobox(self, values=[u'Учебный корпус № 10', u'Учебный корпус № 19'])  # Добавить заполнение вариантов из БД
        self.combobox_corps.current(0)
        self.combobox_corps.place(x=200, y=50)

        label_auditory = tk.Label(self, text='Введите аудиторию:')
        label_auditory.place(x=50, y=80)

        self.entry_auditory = ttk.Entry(self)
        self.entry_auditory.place(x=200, y=80)

        self.btn_start_recognition = ttk.Button(self, text='Начать', command=self.get_lesson_information)
        self.btn_start_recognition.place(x=150, y=120)

        self.grab_set()
        self.focus_set()

    def get_lesson_information(self):
        corps = str(self.combobox_corps.get())
        auditory = str(self.entry_auditory.get())
        lesson_data = pl(corps, auditory)
        self.get_students_from_groups(lesson_data)

    def get_students_from_groups(self, lesson_data):
        connection_string = "postgresql+psycopg2://admin:password@localhost/student_control"

        engine = create_engine(connection_string)

        get_students_query = "SELECT s.name, s.descriptor FROM student s " \
                             "JOIN studygroup sg ON s.groupid = sg.id " \
                             "WHERE sg.name = '{0}'".format(lesson_data[1][0])

        if len(lesson_data[1]) > 1:
            for group in lesson_data[1]:
                get_students_query += " OR sg.name = '{0}'".format(group)

        students_data = engine.execute(get_students_query)

        students_data_list = []

        for student in students_data:
            students_data_list.append({'Name': student[0], 'Descriptor': student[1]})
        with open('student_data.json', 'w') as f:
            student_data = json.dumps(students_data_list, ensure_ascii=False)
            student_data = student_data.replace("\\\\", "\\")
            f.write(student_data)

            root.destroy()

            exec(open('/home/banshchikovalex/GitHub/StudentControlSystem/Recognition.py').read())


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("StudentControlSystem")
    root.geometry("400x300+300+200")
    root.resizable(False, False)
    root.mainloop()
