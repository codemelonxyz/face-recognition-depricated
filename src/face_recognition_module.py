import os
import face_recognition
import cv2
import numpy as np

known_face_encodings = []
known_face_names = []

def load_known_faces():
    faces_dir = "known_faces"
    if not os.path.exists(faces_dir):
        os.makedirs(faces_dir)
    try:
        for filename in os.listdir(faces_dir):
            if filename.endswith((".jpg", ".jpeg", ".png")):
                path = os.path.join(faces_dir, filename)
                name = os.path.splitext(filename)[0]
                image = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    encoding = encodings[0]
                    known_face_encodings.append(encoding)
                    known_face_names.append(name)
    except Exception as e:
        print(f"Failed to load known faces: {str(e)}")
    return known_face_encodings, known_face_names

def recognize_faces(frame, known_face_encodings, known_face_names):
    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    # Find all faces and face encodings in the current frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if len(distances) > 0:
            min_distance = min(distances)
            min_index = np.argmin(distances)
            if min_distance < 0.6:
                name = known_face_names[min_index]
            else:
                name = "Unknown"
        else:
            name = "Unknown"
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
    return frame

def register_face(frame):
    """
    Detects and extracts a face from the given frame.
    Returns the cropped face image and a message.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    if len(face_locations) == 0:
        return None, "No face detected."
    # Assume only one face
    top, right, bottom, left = face_locations[0]
    face_image = frame[top:bottom, left:right]
    return face_image, "Face captured successfully."

def register_new_face(name, face_image):
    """
    Saves the face image and updates the known faces list.
    Returns True if successful, False otherwise.
    """
    try:
        # Save the face image
        cv2.imwrite(name, face_image)
        # Load and encode the new face
        image = face_recognition.load_image_file(name)
        encodings = face_recognition.face_encodings(image)
        if len(encodings) > 0:
            encoding = encodings[0]
            known_face_encodings.append(encoding)
            known_face_names.append(os.path.splitext(os.path.basename(name))[0])
            return True
        else:
            return False
    except Exception as e:
        print(f"Failed to register new face: {str(e)}")
        return False