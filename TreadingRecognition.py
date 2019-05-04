import dlib
from scipy.spatial import distance
from datetime import datetime
from tkinter import *
import cv2
import json
from tkinter import ttk
import tkinter as tk


time_list_report = []
time_list_buffer = []

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
        self.root.title("Отчет")

        toolbar = tk.Frame(bg='#d7d8e0', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.label_group = tk.Label(toolbar, text='Учебные группы: ' + lesson_data[1])
        self.label_group.pack(side=tk.LEFT)

        self.label_lesson = tk.Label(toolbar, text='Текущее занятие: ' + lesson_data[0])
        self.label_lesson.pack(side=tk.BOTTOM)

        self.label_teacher = tk.Label(toolbar, text='ФИО преподавателя: ' + lesson_data[2])
        self.label_teacher.pack(side=tk.BOTTOM)

        self.tree = ttk.Treeview(columns=('student', 'time-in', 'time-out'),
                                 height=15, show='headings')

        self.tree.column("student", width=300, anchor=tk.CENTER)
        self.tree.column("time-in", width=150, anchor=tk.CENTER)
        self.tree.column("time-out", width=100, anchor=tk.CENTER)

        self.tree.heading("student", text='ФИО студента')
        self.tree.heading("time-in", text='Время прибытия')
        self.tree.heading("time-out", text='Время ухода')

        self.tree.pack()

        self.root.after(1000, self.CheckQueuePoll, q)

    def CheckQueuePoll(self, c_queue):
        try:
            result = c_queue.get(0)

            [self.tree.delete(i) for i in self.tree.get_children()]

            for item in result:
                self.tree.insert('', 'end', values=(item['name'],  item['time1'], item['time2']))

            if len(list) == 0:
                print('Очередь пуста!')
                pass
        except:
            self.root.after(1000, self.CheckQueuePoll, c_queue)


def get_report(array, time_list_report):
    for item in array:
        flag = False
        for human in time_list_report:
            if item['name'] == human['name']:
                human['time2'] = item['time']
                flag = True
                break
        if flag is False:
            time_list_report.append({'name': item['name'], 'time1': item['time'], 'time2': item['time']})
    array.clear()


def Recognition(q):
    with open('student_data.json', 'r') as f:
        data = json.loads(f.read())
        countDescriptors = len(data)

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
            dets_webcam = detector(img2, 1)  # Здесь начался HOG, нужно убрать
            for k, d in enumerate(dets_webcam):
                shape = sp(img2, d)
                face_descriptor2 = facerec.compute_face_descriptor(img2, shape)

            i = 0
            descriptorsRaw = []

            while i < countDescriptors:
                descriptorsRaw.append(data[i]['Descriptor'])
                currentDescriptor = tuple(float(item) for item in descriptorsRaw[i].split('\n'))
                try:
                    a = distance.euclidean(currentDescriptor, face_descriptor2)
                    if a < 0.65:
                        time_list_buffer.append({'name': data[i]['Name'],
                                               'time': datetime.strftime(datetime.now(),
                                                                         "%H:%M:%S")})
                        break
                    i += 1
                except NameError:
                    break

            cv2.rectangle(img2, (x, y), (x + w, y + h), (255, 0, 0), 2)

            if len(time_list_buffer) != 0:
                get_report(time_list_buffer, time_list_report)
                q.put(time_list_report)

        cv2.imshow('video', img2)

        k = cv2.waitKey(30) & 0xff
        if k == 27:  # press 'ESC' to quit
            cap.release()
            cv2.destroyAllWindows()
            break
