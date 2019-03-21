import tkinter as tk
from tkinter import ttk
from sqlalchemy import create_engine


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()

    def init_main(self):
        btn_start_work = ttk.Button(text='Начать работу', command=root.destroy)
        btn_start_work.place(x=150, y=50)

        btn_add_student = ttk.Button(text='Добавить студента')
        btn_add_student.place(x=150, y=80)

        btn_add_group = ttk.Button(text='Добавить группу', command=self.open_dialog )
        btn_add_group.place(x=150, y=110)

    def open_dialog(self):
        Child()


class Child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_add_group()

    def init_add_group(self):
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

        query = "INSERT INTO studygroup (name) VALUES ('{0}')".format(str(group_name))

        try:
            engine.execute(query)

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
