import multiprocessing
from tkinter import filedialog as fd
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

def init_corps_list():
    result = []

    engine = create_engine(connection_string)

    get_corps_query = "SELECT name FROM corps"
    data = engine.execute(get_corps_query)

    for item in data:
        result.append(str(item[0]))

    return result


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()

    def init_main(self):
        btn_start_work = tk.Button(text='Начать работу', height="1", width="16", font="14", command=self.open_lesson_information_form)
        btn_start_work.place(x=110, y=50)

        btn_add_student = tk.Button(text='Добавить студента', height="1", width="16", font="14", command=self.open_add_student_form)
        btn_add_student.place(x=110, y=90)

        btn_add_group = tk.Button(text='Добавить группу', height="1", width="16", font="14", command=self.open_add_group_form)
        btn_add_group.place(x=110, y=130)

        btn_show_group = tk.Button(text='Просмотреть группы', height="1", width="16", font="14", command=self.open_show_group_form)
        btn_show_group.place(x=110, y=170)

        btn_report = tk.Button(text='Построить отчет', height="1", width="16", font="14", command=self.open_report_form)
        btn_report.place(x=110, y=210)

    def open_add_group_form(self):
        AddGroupForm()

    def open_add_student_form(self):
        AddStudentForm()

    def open_lesson_information_form(self):
        LessonInformationForm()

    def open_show_group_form(self):
        ShowGroupForm()

    def open_report_form(self):
        ReportForm()


class ReportForm(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        groups_list = init_groups_list()
        self.init_report_form(groups_list)

    def init_report_form(self, groups_list):
        self.title("Отчет по посещаемости")
        self.geometry("800x400+400+300")
        self.resizable(False, False)

        toolbar_date = tk.Frame(self, bg='#d7d8e0', bd=2)
        toolbar_date.pack(side=tk.TOP, fill=tk.X)

        toolbar_lesson = tk.Frame(self, bg='#d7d8e0', bd=2)
        toolbar_lesson.pack(side=tk.TOP, fill=tk.X)

        button_bar = tk.Frame(self, bg='#d7d8e0', bd=2)
        button_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.label_date_to = tk.Label(toolbar_date, text='                Дата начала:')
        self.label_date_to.pack(side=tk.LEFT)

        self.entry_date_from = ttk.Entry(toolbar_date)
        self.entry_date_from.pack(side=tk.LEFT)

        self.entry_date_to = ttk.Entry(toolbar_date)
        self.entry_date_to.pack(side=tk.RIGHT)

        self.label_date_to = tk.Label(toolbar_date, text='Дата окончания:')
        self.label_date_to.pack(side=tk.RIGHT)

        self.label_lesson = tk.Label(toolbar_lesson, text='Название дисциплины:')
        self.label_lesson.pack(side=tk.LEFT)

        self.entry_lesson_name = ttk.Entry(toolbar_lesson)
        self.entry_lesson_name.pack(side=tk.LEFT)

        self.combobox_groups = ttk.Combobox(toolbar_lesson, values=groups_list)
        self.combobox_groups.pack(side=tk.RIGHT)

        self.label_group = tk.Label(toolbar_lesson, text='Номер группы:')
        self.label_group.pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(self, columns=('date', 'lesson_name', 'student', 'time-in', 'time-out', 'duration'),
                                 height=15, show='headings')

        self.tree.column("date", width=100, anchor=tk.CENTER)
        self.tree.column("lesson_name", width=170, anchor=tk.CENTER)
        self.tree.column("student", width=170, anchor=tk.CENTER)
        self.tree.column("time-in", width=130, anchor=tk.CENTER)
        self.tree.column("time-out", width=100, anchor=tk.CENTER)
        self.tree.column("duration", width=130, anchor=tk.CENTER)

        self.tree.heading("date", text='Дата')
        self.tree.heading("lesson_name", text='Дисциплина')
        self.tree.heading("student", text='Студент')
        self.tree.heading("time-in", text='Время прибытия')
        self.tree.heading("time-out", text='Время ухода')
        self.tree.heading("duration", text='Общее время')

        self.tree.pack()

        btn_cancel = ttk.Button(button_bar, text='Закрыть', command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

        btn_ok = ttk.Button(button_bar, text='Показать',
                            command=lambda: self.build_report(str(self.entry_lesson_name.get()),
                                                              str(self.entry_date_from.get()),
                                                              str(self.entry_date_to.get()),
                                                              str(self.combobox_groups.get())))
        btn_ok.pack(side=tk.RIGHT)

        self.grab_set()
        self.focus_set()

    def build_report(self, lesson_name, date_from, date_to, group):
        engine = create_engine(connection_string)

        get_report_query = 'SELECT date, "lessonName", "studentName", "timeIn", "timeOut", ' \
                            'ceil(extract(epoch from ("timeOut"::time - "timeIn"::time)) / 60) duration ' \
                            'FROM "recognitionHistory" ' \
                            """WHERE "lessonName" LIKE '{0}%%' """ \
                            """AND "studyGroup" LIKE '{1}' """ \
                            """AND (date, date) OVERLAPS ('{2}'::DATE, '{3}'::DATE) """ \
                            'ORDER BY "date" ASC'.format(lesson_name, group, date_from, date_to)

        data = engine.execute(get_report_query)

        [self.tree.delete(i) for i in self.tree.get_children()]

        for item in data:
            self.tree.insert('', 'end', values=(item[0], item[1], item[2], item[3], item[4], int(item[5])))


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
                                 "WHERE sg.name = '{0}' " \
                                 "ORDER BY s.name ASC".format(group)
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
        self.geometry("400x150+400+300")
        self.resizable(False, False)

        button_bar = tk.Frame(self, bg='#d7d8e0', bd=2)
        button_bar.pack(side=tk.BOTTOM, fill=tk.X)

        label_description = tk.Label(self, text='Номер группы:')
        label_description.place(x=50, y=50)

        self.entry_group_name = ttk.Entry(self)
        self.entry_group_name.place(x=200, y=50)

        btn_cancel = ttk.Button(button_bar, text='Закрыть', command=self.destroy)
        btn_cancel.pack(side=tk.RIGHT)

        btn_ok = ttk.Button(button_bar, text='Добавить', command=lambda: self.get_arguments())
        btn_ok.pack(side=RIGHT)

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
        self.geometry("400x250+400+300")
        self.resizable(False, False)

        button_bar = tk.Frame(self, bg='#d7d8e0', bd=2)
        button_bar.pack(side=tk.BOTTOM, fill=tk.X)

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

        self.btn_cancel = ttk.Button(button_bar, text='Закрыть', command=self.destroy)
        self.btn_cancel.pack(side=RIGHT)

        self.btn_ok = ttk.Button(button_bar, text='Добавить', command=lambda: self.get_arguments())
        self.btn_ok.pack(side=RIGHT)

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
        corps_list = init_corps_list()
        self.init_lesson_information_form(corps_list)

    def get_update_auditory(self, event):
        result = []

        engine = create_engine(connection_string)

        get_auditory_query = "SELECT a.name FROM auditory a " \
                                 'JOIN corps c ON a."corpsId" = c.id ' \
                                 "WHERE c.name = '{0}'".format(self.combobox_corps.get())

        data = engine.execute(get_auditory_query)

        for item in data:
            result.append(str(item[0]))

        self.combobox_auditory['values'] = result

    def init_lesson_information_form(self, corps_list):
        self.title("Информация о занятии")
        self.geometry("400x180+400+300")
        self.resizable(False, False)

        label_corps = tk.Label(self, text='Выберете корпус:')
        label_corps.place(x=50, y=50)

        self.combobox_corps = ttk.Combobox(self, values=corps_list)
        self.combobox_corps.bind('<<ComboboxSelected>>', self.get_update_auditory)
        self.combobox_corps.place(x=200, y=50)

        label_auditory = tk.Label(self, text='Выберете аудиторию:')
        label_auditory.place(x=50, y=80)

        self.combobox_auditory = ttk.Combobox(self)
        self.combobox_auditory.place(x=200, y=80)

        self.btn_start_recognition = ttk.Button(self, text='Начать', command=self.get_lesson_information)
        self.btn_start_recognition.place(x=150, y=120)

        self.grab_set()
        self.focus_set()

    def get_lesson_information(self):
        corps = str(self.combobox_corps.get())
        auditory = str(self.combobox_auditory.get())
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
