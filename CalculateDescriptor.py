import dlib
from skimage import io
import json

sp = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')
detector = dlib.get_frontal_face_detector()
img = io.imread("/home/banshchikovalex/Изображения/UIRS/!Kondratieva.jpg") # Считывание дескриптора с фото

win1 = dlib.image_window()
win1.clear_overlay()
win1.set_image(img)

dets = detector(img, 1)
for k, d in enumerate(dets):
    shape = sp(img, d)
    win1.clear_overlay()
    win1.add_overlay(d)
    win1.add_overlay(shape)

face_descriptor1 = facerec.compute_face_descriptor(img, shape)

descriptor = str(face_descriptor1) # Запись в JSON
name = ''

dict = {'Name': name, 'Descriptor': descriptor}

# while True:
#    continue

with open('data.json', 'a') as f:
    myobjectJson = json.dumps(dict)
    f.write(myobjectJson)

