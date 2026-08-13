# Face Recognition Attendance System

## Final Year Project Report

### Submitted by
Your Name

### Department
Artificial Intelligence / Computer Science

### Institution
Your College Name

### Academic Year
2025-2026

---

## 1. Abstract

Attendance management is a crucial activity in educational and professional institutions. Traditional manual attendance systems are time-consuming, prone to errors, and vulnerable to proxy attendance. To address these challenges, this project proposes an intelligent and automated attendance system based on facial recognition.

The developed system uses computer vision and machine learning techniques to detect faces from live webcam input, recognize enrolled users, and automatically mark attendance. The solution is implemented using Python, OpenCV, LBPH face recognition, SQLite, and a modern desktop graphical interface. The system also includes features such as user enrollment, live camera scanning, attendance logs, dashboard statistics, and report export in Excel and CSV formats.

This project demonstrates how artificial intelligence can be effectively applied to solve real-world administrative problems with accuracy, efficiency, and minimal human intervention.

---

## 2. Introduction

The rapid growth of technology has transformed many traditional processes into intelligent automated systems. Attendance tracking is one such process that benefits greatly from automation. In schools, colleges, and workplaces, attendance is often recorded manually, which consumes time and creates opportunities for mistakes or misuse.

Face recognition provides a reliable and contactless solution for identifying individuals. By leveraging computer vision and machine learning, it is possible to build a smart attendance system that can recognize a person in real time and record their presence automatically.

The aim of this project is to design and implement a face recognition-based attendance system that is practical, secure, and easy to use.

---

## 3. Problem Statement

Manual attendance systems have several drawbacks:

- They are slow and inefficient for large groups.
- They are prone to human error.
- They are vulnerable to proxy attendance.
- They make record management difficult and time consuming.

Therefore, there is a strong need for a smart, automated, and reliable attendance management solution.

---

## 4. Objectives of the Project

The main objectives of this project are:

1. To build an automated attendance system using face recognition.
2. To detect faces from live webcam input.
3. To recognize registered individuals with acceptable confidence.
4. To store attendance data in a database for future use.
5. To provide an interactive dashboard and reporting features.
6. To reduce manual effort and improve attendance accuracy.

---

## 5. Scope of the Project

The project focuses on developing a desktop-based attendance application with the following features:

- Registration of new users with sample face images
- Training of the recognition model
- Real-time face detection and recognition
- Automatic attendance marking
- Dashboard showing attendance statistics
- Export of attendance reports to CSV and Excel

---

## 6. Literature Review

Face recognition is one of the most promising applications of computer vision and artificial intelligence. It has been widely used in security systems, access control, mobile authentication, and surveillance. In attendance systems, face recognition offers a non-intrusive method of identity verification.

Several approaches have been used for facial recognition, including Eigenfaces, Fisherfaces, and Local Binary Patterns Histograms (LBPH). Among these, LBPH is popular because it is lightweight, efficient, and suitable for real-time applications. The Haar Cascade classifier is also commonly used for quick and reliable face detection.

This project combines both techniques to create a cost-effective and practical real-time attendance solution.

---

## 7. Proposed System

The proposed system works in the following steps:

1. A user enrolls their face by capturing or uploading sample images.
2. The system preprocesses and trains the face recognition model.
3. During attendance, the webcam captures live frames.
4. Faces are detected from each frame.
5. The detected face is compared with the trained dataset.
6. If the face matches with sufficient confidence, the attendance is marked automatically.
7. The attendance record is stored in the database and displayed in the dashboard.

This workflow makes the system automated, fast, and user friendly.

---

## 8. Methodology

### 8.1 Face Detection
The system uses the Haar Cascade Classifier to detect the presence of human faces in video frames.

### 8.2 Image Preprocessing
The face images are improved using preprocessing techniques such as illumination normalization to make recognition more reliable.

### 8.3 Face Recognition
The LBPH algorithm is used for recognizing faces based on local texture patterns. It is suitable for this project because it is simple, efficient, and works well for small to medium-sized datasets.

### 8.4 Attendance Logging
Once a recognized face is detected, the system records the date, time, confidence value, and attendance status in the database.

### 8.5 Database Management
SQLite is used to store student or employee records and attendance logs. This provides a lightweight and portable database solution.

---

## 9. System Architecture

The system architecture consists of the following major modules:

- Input Module: Webcam or image input
- Detection Module: Face detection using Haar Cascade
- Recognition Module: Face recognition using LBPH
- Database Module: Storage of users and attendance logs
- GUI Module: User interaction through an interactive desktop application
- Report Module: Export of reports in CSV and Excel format

This modular design makes the system easy to understand, maintain, and extend.

---

## 10. Tools and Technologies Used

The project is developed using the following tools and technologies:

- Python
- OpenCV
- CustomTkinter
- SQLite
- Pillow
- Pandas
- OpenPyXL
- ReportLab

These technologies were chosen because they are open-source, reliable, and suitable for building a complete AI-based desktop application.

---

## 11. Application Interface and Working

The system provides an easy-to-use desktop interface with multiple functional sections:

- Dashboard: Displays total registered users, present today, late today, and absent today.
- Live Scanner: Captures live video and recognizes faces in real time.
- Enrollment: Allows users to register new faces by capturing or importing sample images.
- Attendance Logs: Shows historical attendance records and allows filtering.
- Registered Users: Displays all registered users and related information.

This interface makes the project more practical for real-world use in colleges and offices.

### Screenshot Placeholder

The application screenshots can be added here during presentation:

- Dashboard view
- Live scanner view
- Enrollment view
- Attendance logs view

> Add screenshots of the application in the final PDF to make the report visually attractive and easier to explain during viva.

---

## 12. Advantages of the Project

The project offers several benefits:

- Reduces manual attendance work
- Increases accuracy and reliability
- Prevents proxy attendance
- Provides real-time monitoring
- Stores attendance records securely
- Offers user-friendly management features

---

## 13. Limitations and Future Scope

Although the system is effective, it has some limitations:

- Recognition accuracy may be affected by poor lighting.
- Performance may depend on camera quality.
- Extreme face angles may reduce recognition accuracy.

Future improvements may include:

- Liveness detection to prevent spoofing
- Cloud-based database integration
- Mobile application support
- Deep learning-based face recognition for higher accuracy

---

## 14. Results and Discussion

The implemented system successfully demonstrated real-time face detection and recognition. During testing, registered individuals were recognized and attendance records were stored correctly. The dashboard and report modules also worked as expected, making the solution suitable for academic and practical use.

The project proves that face recognition can be applied effectively to simplify attendance management and improve operational efficiency.

---

## 15. Conclusion

The Face Recognition Attendance System is an effective and modern solution for automated attendance tracking. The project combines artificial intelligence, computer vision, and software engineering to create a practical system that reduces human effort and improves reliability.

This work highlights the importance of using technology to solve everyday problems and demonstrates the potential of AI-based applications in real-world environments.

---

## 16. Viva Preparation Notes

During the viva, the following points should be explained clearly:

- What problem the project solves
- Why face recognition was chosen over traditional methods
- How the system detects and recognizes faces
- How attendance is stored and retrieved from the database
- What the dashboard and report modules do
- What improvements can be made in future versions

These points will help present the project confidently and professionally.

---

## 17. References

1. OpenCV Documentation
2. Python Documentation
3. LBPH Face Recognition Principles
4. SQLite Documentation
5. CustomTkinter Documentation
