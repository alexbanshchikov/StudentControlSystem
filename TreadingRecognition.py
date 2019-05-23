import dlib
from scipy.spatial import distance
from datetime import datetime
from tkinter import *
import cv2
import json
from tkinter import ttk
import tkinter as tk
from sqlalchemy import create_engine


time_list_report = []
time_list_buffer = []

connection_string = "postgresql+psycopg2://admin:password@localhost/student_control"

faceCascade = cv2.CascadeClassifier('RecognitionFiles/haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

sp = dlib.shape_predictor('RecognitionFiles/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('RecognitionFiles/dlib_face_recognition_resnet_model_v1.dat')
detector = dlib.get_frontal_face_detector()


class GuiApp(object):
    def __init__(self, q, lesson_data):
        self.root = Tk()
        self.root.title("StudentControlSystem")

        toolbar_lesson = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar_lesson.pack(side=tk.TOP, fill=tk.X)

        if type(lesson_data[1]) is str:
            self.label_group = tk.Label(toolbar_lesson, text='Учебная группа: ' + lesson_data[1])
        else:
            self.label_group = tk.Label(toolbar_lesson, text='Учебные группы: ' + ', '.join(lesson_data[1]))

        self.label_group.pack(side=tk.LEFT)

        self.label_lesson = tk.Label(toolbar_lesson, text='Текущее занятие: ' + lesson_data[0])
        self.label_lesson.pack(side=tk.BOTTOM)

        self.label_teacher = tk.Label(toolbar_lesson, text='ФИО преподавателя: ' + lesson_data[2])
        self.label_teacher.pack(side=tk.BOTTOM)

        self.tree = ttk.Treeview(columns=('student', 'group', 'time-in', 'time-out'),
                                 height=15, show='headings')

        self.tree.column("student", width=170, anchor=tk.CENTER)
        self.tree.column("group", width=130, anchor=tk.CENTER)
        self.tree.column("time-in", width=150, anchor=tk.CENTER)
        self.tree.column("time-out", width=100, anchor=tk.CENTER)

        self.tree.heading("student", text='Студент')
        self.tree.heading("group", text='Учебная группа')
        self.tree.heading("time-in", text='Время прибытия')
        self.tree.heading("time-out", text='Время ухода')

        self.tree.pack()

        toolbar_buttons = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar_buttons.pack(side=tk.BOTTOM, fill=tk.X)

        btn_cancel = ttk.Button(toolbar_buttons, text='Завершить работу', command=lambda: self.close_program(lesson_data))
        btn_cancel.pack(side=tk.RIGHT)

        self.root.after(1000, self.check_queue_poll, q)

    def check_queue_poll(self, c_queue):
        try:
            result = c_queue.get(0)

            [self.tree.delete(i) for i in self.tree.get_children()]

            for item in result:
                self.tree.insert('', 'end', values=(item['name'], item['group'], item['time1'], item['time2']))

            if len(list) == 0:
                print('Очередь пуста!')
                pass
        except:
            self.root.after(1000, self.check_queue_poll, c_queue)

    def close_program(self, lesson_data):
        engine = create_engine(connection_string)
        students_list = []
        [students_list.append(self.tree.item(child, "values")) for child in self.tree.get_children()]
        for item in students_list:
            insert_query = 'INSERT INTO "recognitionHistory" ("date", "corpse", "auditory", "lessonName", ' \
                           '"studentName", "timeIn", "timeOut", "teacherName", "studyGroup") ' \
                            "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')"\
                                                            .format(datetime.strftime(datetime.now(), '%Y-%m-%d'),
                                                                    lesson_data[3],
                                                                    lesson_data[4],
                                                                    lesson_data[0],
                                                                    item[0],
                                                                    item[2],
                                                                    item[3],
                                                                    lesson_data[2],
                                                                    item[1])

            engine.execute(insert_query)

        self.root.destroy()
        cap.release()
        cv2.destroyAllWindows()


def get_report(array, time_list_report):
    for item in array:
        flag = False
        for human in time_list_report:
            if item['name'] == human['name']:
                human['time2'] = item['time']
                flag = True
                break
        if flag is False:
            time_list_report.append({'name': item['name'], 'group': item['group'],
                                     'time1': item['time'], 'time2': item['time']})
    array.clear()


def recognition(q):
    with open('student_data.json', 'r') as f:
        data = json.loads(f.read())
        count_descriptors = len(data)

        time_list_buffer = []

    while True:
        ret, img2 = cap.read()
        gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(20, 20)
        )

        for (x, y, w, h) in faces:
            dets_webcam = detector(img2, 1)
            for k, d in enumerate(dets_webcam):
                shape = sp(img2, d)
                face_descriptor2 = facerec.compute_face_descriptor(img2, shape)

            i = 0
            descriptors_raw = []

            while i < count_descriptors:
                descriptors_raw.append(data[i]['Descriptor'])
                current_descriptor = tuple(float(item) for item in descriptors_raw[i].split('\n'))
                try:
                    a = distance.euclidean(current_descriptor, face_descriptor2)
                    if a < 0.53:
                        time_list_buffer.append({'name': data[i]['Name'],
                                                 'group': data[i]['Group'],
                                                 'time': datetime.strftime(datetime.now(), "%H:%M:%S")})
                        break
                    i += 1
                except NameError:
                    break

            cv2.rectangle(img2, (x, y), (x + w, y + h), (255, 0, 0), 2)

            if len(time_list_buffer) != 0:
                get_report(time_list_buffer, time_list_report)
                q.put(time_list_report)
