import multiprocessing
from tkinter import filedialog as fd
from sqlalchemy import create_engine
from CalculateDescriptor import calculate
from ScheduleParser import parse_lesson as pl
from TreadingRecognition import *

connection_string = "postgresql+psycopg2://admin:password@localhost/student_control"


def init_groups_list():
    result = []

    engine = create_engine(connection_string)

    get_group_query = "SELECT name FROM studygroup"
    data = engine.execute(get_group_query)

    for item in data:
        result.append(str(item[0]))

    return result

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

        btn_show_group = ttk.Button(text='Просмотреть группы', command=self.open_show_group_form)
        btn_show_group.place(x=150, y=140)

    def open_add_group_form(self):
        AddGroupForm()

    def open_add_student_form(self):
        AddStudentForm()

    def open_lesson_information_form(self):
        LessonInformationForm()

    def open_show_group_form(self):
        ShowGroupForm()


class ShowGroupForm(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        groups_list = init_groups_list()
        self.init_show_group_form(groups_list)

    def init_show_group_form(self, groups_list):
        self.title("Показать группу")
        self.geometry("400x220+400+300")
        self.resizable(False, False)

        toolbar = tk.Frame(self, bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        button_bar = tk.Frame(self, bg='#d7d8e0', bd=2)
        button_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.label_name = tk.Label(toolbar, text='Выберите группу:')
        self.label_name.pack(side=tk.LEFT)

        self.combobox_groups = ttk.Combobox(toolbar, values=groups_list)
        self.combobox_groups.current(0)
        self.combobox_groups.pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(self, columns=("ID", "Name"), height=10, show="headings")

        self.tree.column("ID", width=70, anchor=tk.E)
        self.tree.column("Name", width=300, anchor=tk.E)

        self.tree.heading("ID", text="Номер")
        self.tree.heading("Name", text="Фамилия Имя")

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.place(x=30, y=50)

        self.tree.pack()

        btn_cancel = ttk.Button(button_bar, text='Закрыть', command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

        btn_ok = ttk.Button(button_bar, text='Показать', command=lambda: self.show_group(str(self.combobox_groups.get())))
        btn_ok.pack(side=tk.RIGHT)

        self.grab_set()
        self.focus_set()

    def show_group(self, group):
        engine = create_engine(connection_string)

        get_group_query = "SELECT s.name, s.descriptor FROM student s " \
                                 "JOIN studygroup sg ON s.groupid = sg.id " \
                                 "WHERE sg.name = '{0}'".format(group)
        data = engine.execute(get_group_query)

        [self.tree.delete(i) for i in self.tree.get_children()]

        i = 1
        for item in data:
            self.tree.insert('', 'end', values=(i, item[0]))
            i = i + 1

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
        engine = create_engine(connection_string)

        query = "INSERT INTO studygroup (name) VALUES ('{0}')".format(group_name)

        try:
            engine.execute(query)

        except BaseException as e:
            print("Query error: {}".format(e))


class AddStudentForm(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        groups_list = init_groups_list()
        self.init_add_student_form(groups_list)

    def init_add_student_form(self, groups_list):
        self.title("Добавить студента")
        self.geometry("400x300+400+300")
        self.resizable(False, False)

        self.label_name = tk.Label(self, text='Фамилия и имя:')
        self.label_name.place(x=50, y=50)

        self.entry_name = ttk.Entry(self)
        self.entry_name.place(x=200, y=50)

        self.label_group = tk.Label(self, text='Группа:')
        self.label_group.place(x=50, y=80)

        self.combobox_group = ttk.Combobox(self, values=groups_list)
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
        engine = create_engine(connection_string)

        if type(lesson_data[1]) is str:
            get_students_query = "SELECT s.name, s.descriptor, sg.name FROM student s " \
                                 "JOIN studygroup sg ON s.groupid = sg.id " \
                                 "WHERE sg.name = '{0}'".format(lesson_data[1])

        else:
            get_students_query = "SELECT s.name, s.descriptor, sg.name FROM student s " \
                                 "JOIN studygroup sg ON s.groupid = sg.id " \
                                 "WHERE sg.name = '{0}'".format(lesson_data[1][0])

            if len(lesson_data[1]) > 1:
                for group in lesson_data[1]:
                    get_students_query += " OR sg.name = '{0}'".format(group)

        students_data = engine.execute(get_students_query)

        students_data_list = []

        for student in students_data:
            students_data_list.append({'Name': student[0], 'Descriptor': student[1], 'Group': student[2]})
        with open('student_data.json', 'w') as f:
            student_data = json.dumps(students_data_list, ensure_ascii=False)
            student_data = student_data.replace("\\\\", "\\")
            f.write(student_data)

            root.destroy()

            q = multiprocessing.Queue()
            q.cancel_join_thread()
            gui = GuiApp(q, lesson_data)
            t1 = multiprocessing.Process(target=recognition, args=(q,))
            t1.start()
            gui.root.mainloop()


if __name__ == "__main__":
    root = Tk()
    app = Main(root)
    app.pack()
    root.title("StudentControlSystem")
    root.geometry("400x300+300+200")
    root.resizable(False, False)
    root.mainloop()
