import dlib
from skimage import io

sp = dlib.shape_predictor('RecognitionFiles/shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('RecognitionFiles/dlib_face_recognition_resnet_model_v1.dat')
detector = dlib.get_frontal_face_detector()


def calculate(image_path):
    img = io.imread(image_path)  # Считывание дескриптора с фото

    win1 = dlib.image_window()
    win1.clear_overlay()
    win1.set_image(img)

    dets = detector(img, 1)
    for k, d in enumerate(dets):
        shape = sp(img, d)
        win1.clear_overlay()
        win1.add_overlay(d)
        win1.add_overlay(shape)

    face_descriptor = str(facerec.compute_face_descriptor(img, shape))

    return face_descriptor

