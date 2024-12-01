import os
import face_recognition
import cv2
import numpy as np
from database import Database

known_face_encodings = []
known_face_names = []

def load_known_faces(db):
    """
    Load and encode all known faces from the database.
    """
    db.cursor.execute("SELECT id, face_encoding FROM students")
    records = db.cursor.fetchall()
    
    known_face_encodings = []
    known_face_ids = []
    for record in records:
        student_id = record[0]
        encoding = np.frombuffer(record[1], dtype=np.float64)
        known_face_encodings.append(encoding)
        known_face_ids.append(student_id)
    
    return known_face_encodings, known_face_ids

def check_liveness(frame):
    """Check if the face is real using basic liveness detection"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    return blur > 100  # Threshold for blur detection

def recognize_faces(frame, db):
    """
    Detect and recognize faces in the given frame.
    Returns the annotated frame and a list of recognized student IDs.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
    
    recognized_students = []
    
    known_face_encodings, known_face_ids = load_known_faces(db)
    
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        
        if len(face_distances) == 0:
            continue  # Skip if no known faces to compare
        
        best_match_index = np.argmin(face_distances)
        
        if matches[best_match_index]:
            student_id = known_face_ids[best_match_index]
            recognized_students.append((student_id, f"Student {student_id}"))
    
    # Annotate frame with rectangles and names
    for (top, right, bottom, left), (student_id, name) in zip(face_locations, recognized_students):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    
    return frame, recognized_students

def register_face(frame):
    """
    Capture and process a new face from the frame for registration.
    Returns the face image and a message.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    
    if len(face_locations) != 1:
        return None, "Please ensure exactly one face is visible."
    
    top, right, bottom, left = face_locations[0]
    face_image = frame[top:bottom, left:right]
    
    return face_image, "Face captured successfully."

def register_new_face(image_path, db):
    """
    Encode and save the new face to the database.
    """
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)
    
    if not face_encodings:
        return False, "No face encoding found in the image."
    
    face_encoding = face_encodings[0]
    face_encoding_blob = face_encoding.tobytes()
    
    # Insert into the database
    try:
        db.cursor.execute("""
            INSERT INTO students (name, face_encoding)
            VALUES (%s, %s)
        """, ("Unknown", face_encoding_blob))
        db.connection.commit()
        return True, "Face registered successfully."
    except mysql.connector.Error as err:
        print(f"Error registering face: {err}")
        return False, "Database error during registration."