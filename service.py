import cv2
import numpy as np
import os

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

face_data_dir=ROOT+"/face_data"
if not os.path.exists(face_data_dir):
    os.makedirs(face_data_dir)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()

def register_face(face_id):
    cap = cv2.VideoCapture(0)
    count = 0
    print("1")
    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1,
                                              minNeighbors=10)  # Increased minNeighbors for better accuracy
        print("2")
        for (x, y, w, h) in faces:
            if w < 50 or h < 50:  # Skip small detections
                continue

            print("3")
            face_roi = gray[y:y + h, x:x + w]
            eyes = eye_cascade.detectMultiScale(face_roi)  # Detect eyes within face
            if len(eyes) >= 2:  # Only proceed if two eyes are detected
                print("4")
                face_img = cv2.equalizeHist(face_roi)  # Normalize lighting
                print("path",f"{face_data_dir}/User.{face_id}.{count}.jpg")
                cv2.imwrite(f"{face_data_dir}/User.{face_id}.{count}.jpg", face_img)
                count += 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                print("5")
        cv2.imshow('Registering Face', frame)
        print("6")
        if count >= 300 or cv2.waitKey(1) == ord('q'):
            print("7")
            break

        print("8")
    cap.release()
    cv2.destroyAllWindows()

    print("9")

def train_recognizer():
    faces, ids = [], []
    for filename in os.listdir(face_data_dir):
        if filename.startswith("User"):
            img = cv2.imread(os.path.join(face_data_dir, filename), cv2.IMREAD_GRAYSCALE)
            face_id = int(filename.split(".")[1])
            faces.append(img)
            ids.append(face_id)

    recognizer.train(faces, np.array(ids))
    recognizer.write(ROOT+"/model/face_trainer.yml")
    print("Training completed.")


def recognize_faces():

    global face_id

    recognizer.read(ROOT+"/model/face_trainer.yml")
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10)

        for (x, y, w, h) in faces:
            face_img = gray[y:y + h, x:x + w]
            face_img = cv2.equalizeHist(face_img)
            face_id, confidence = recognizer.predict(face_img)

            if confidence < 40:
                name = f"User {face_id}"
            else:
                name = "Unknown"
                face_id="Unknown"

            cv2.putText(frame, f"{name} ({round(confidence, 2)})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return face_id