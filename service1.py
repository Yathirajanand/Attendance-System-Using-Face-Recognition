import os
import cv2
import numpy as np
import face_recognition

from StudentAttendanceMonitoring.settings import BASE_DIR

# Define directories

FACE_DATA_DIR = os.path.join(BASE_DIR, "face_data")
print(FACE_DATA_DIR )
MODEL_DIR = os.path.join(BASE_DIR, "model")

# Ensure directories exist
os.makedirs(FACE_DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Load Haar cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
recognizer = cv2.face.LBPHFaceRecognizer_create()


def register_face(face_id):
    cap = cv2.VideoCapture(0)
    count = 0

    while count < 300:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10)

        for (x, y, w, h) in faces:
            if w < 50 or h < 50:
                continue

            face_roi = gray[y:y + h, x:x + w]
            eyes = eye_cascade.detectMultiScale(face_roi)

            if len(eyes) >= 2:
                face_img = cv2.equalizeHist(face_roi)
                img_path = os.path.join(FACE_DATA_DIR, f"User.{face_id}.{count}.jpg")
                cv2.imwrite(img_path, face_img)
                count += 1
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow('Registering Face', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def find_encodings(image_files):
    encode_list = []
    face_ids = []
    for file in image_files:
        parts = file.split('.')
        if len(parts) == 4 and parts[0] == "User":
            try:
                img_path = os.path.join(FACE_DATA_DIR, file)
                img = cv2.imread(img_path)
                if img is not None:
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    encodes = face_recognition.face_encodings(img)
                    if encodes:
                        encode_list.append(encodes[0])
                        face_ids.append(parts[1])  # Extracting face_id only if encoding is successful
            except Exception as e:
                print(f"Error processing {file}: {e}")

    return encode_list, face_ids


def recognize_faces():
    print(FACE_DATA_DIR)
    image_files = [f for f in os.listdir(FACE_DATA_DIR) if f.endswith(('jpg', 'png', 'jpeg'))]
    print(image_files)
    encode_list_known, face_ids = find_encodings(image_files)

    print('Encoding Complete')

    cap = cv2.VideoCapture(0)
    UNKNOWN_THRESHOLD = 0.55
    recognized_students = set()

    while True:
        success, img = cap.read()
        if not success:
            break

        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            faceDis = face_recognition.face_distance(encode_list_known, encodeFace)
            if len(faceDis) == 0:
                continue
            matchIndex = np.argmin(faceDis)
            probability = 1 - faceDis[matchIndex]

            if probability > UNKNOWN_THRESHOLD:
                name = face_ids[matchIndex].upper()
                recognized_students.add(name)
            else:
                name = "UNKNOWN"

            y1, x2, y2, x1 = [v * 4 for v in faceLoc]
            color = (0, 255, 0) if name != "UNKNOWN" else (0, 0, 255)
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), color, cv2.FILLED)
            cv2.putText(img, f"{name} ({probability:.2f})", (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1,
                        (255, 255, 255), 2)

        cv2.imshow('Webcam', img)
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return list(recognized_students)  # Return the list of recognized student numbers