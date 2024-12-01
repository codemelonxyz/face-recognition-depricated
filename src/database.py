import mysql.connector
from mysql.connector import errorcode
import numpy as np

class Database:
    def __init__(self):
        self.host = "localhost"
        self.port = 3306
        self.user = "root"
        self.password = "vaiditya@2501"
        self.database = "test"
        self.connection = None
        self.cursor = None
        self.connect_database()
        self.create_tables()
    
    def connect_database(self):
        try:
            # Connect without specifying the database to create it if it doesn't exist
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            self.connection.database = self.database
            self.cursor.close()
            self.connection.close()
            
            # Reconnect to the specific database
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            else:
                print(err)
            exit(1)
    
    def create_tables(self):
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    face_encoding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    subject VARCHAR(100),
                    start_time DATETIME,
                    end_time DATETIME,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id INT,
                    class_id INT,
                    timestamp DATETIME,
                    FOREIGN KEY (student_id) REFERENCES students(id),
                    FOREIGN KEY (class_id) REFERENCES classes(id)
                )
            """)
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Failed creating tables: {err}")
            exit(1)
    
    def insert_student(self, name, face_encoding):
        try:
            face_encoding_blob = face_encoding.tobytes()
            self.cursor.execute("""
                INSERT INTO students (name, face_encoding)
                VALUES (%s, %s)
            """, (name, face_encoding_blob))
            self.connection.commit()
            return True
        except mysql.connector.Error as err:
            print(f"Error inserting student: {err}")
            return False
    
    def fetch_students(self):
        try:
            self.cursor.execute("SELECT id, name, face_encoding FROM students")
            records = self.cursor.fetchall()
            
            students = []
            for record in records:
                student_id = record[0]
                name = record[1]
                face_encoding = np.frombuffer(record[2], dtype=np.float64)
                students.append((student_id, name, face_encoding))
            return students
        except mysql.connector.Error as err:
            print(f"Error fetching students: {err}")
            return []
    
    def close(self):
        self.cursor.close()
        self.connection.close()