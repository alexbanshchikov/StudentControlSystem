import dlib
from scipy.spatial import distance
from datetime import datetime
from tkinter import *
import cv2
import json

time_list_report = []


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


faceCascade = cv2.CascadeClassifier('RecognitionFiles/haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

sp = dlib.shape_predictor('RecognitionFiles/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('RecognitionFiles/dlib_face_recognition_resnet_model_v1.dat')
detector = dlib.get_frontal_face_detector()

with open('student_data.json', 'r') as f:
    data = json.loads(f.read())
    countDescriptors = len(data)

timeListBuffer = []

while True:
    ret, img2 = cap.read()
    gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=5,
        minSize=(20, 20)
    )

    for (x,y,w,h) in faces:
        dets_webcam = detector(img2, 1)                                         # Здесь начался HOG, нужно убрать
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
                if a < 0.55:
                    timeListBuffer.append({'name': data[i]['Name'],
                                           'time': datetime.strftime(datetime.now(),
                                           "%H:%M:%S")})
                    break
                i += 1
            except NameError:
                break

        cv2.rectangle(img2, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img2[y:y+h, x:x+w]

    cv2.imshow('video', img2)

    k = cv2.waitKey(30) & 0xff
    if k == 27:  # press 'ESC' to quit
        break
    if k == 13:
        get_report(timeListBuffer, time_list_report)
        root = Tk()                           # Добавить форму со списком студентов, названием занятия, преподавателем
        root.title("Отчет")
        text = Text(width=70, height=25)
        text.grid(columnspan=3)

        for item in time_list_report:
            string = str(item['name']) + " " + str(item['time1']) + ' ' + str(item['time2']) + '\n'
            text.insert(1.0, string)

        root.mainloop()

cap.release()
cv2.destroyAllWindows()
