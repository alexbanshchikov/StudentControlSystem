import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from sqlalchemy import create_engine
from CalculateDescriptor import calculate


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()

    def init_main(self):
        btn_start_work = ttk.Button(text='Начать работу', command=root.destroy)
        btn_start_work.place(x=150, y=50)

        btn_add_student = ttk.Button(text='Добавить студента', command=self.open_add_student_form)
        btn_add_student.place(x=150, y=80)

        btn_add_group = ttk.Button(text='Добавить группу', command=self.open_add_group_form )
        btn_add_group.place(x=150, y=110)

    def open_add_group_form(self):
        AddGroupForm()

    def open_add_student_form(self):
        AddStudentForm()


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
        connection_string = "postgresql+psycopg2://admin:password@localhost/student_control"  # Запилить получение дескриптора и сформировать запрос к бд

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


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("StudentControlSystem")
    root.geometry("400x300+300+200")
    root.resizable(False, False)
    root.mainloop()
