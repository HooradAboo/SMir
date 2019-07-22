import face_recognition
import cv2
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep


class FaceRecognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 32

    def take_picture_and_train(self, username):
        image_file_path = '/home/pi/pics/{}.jpg'.format(username)
        self.camera.capture(image_file_path)
        new_image = face_recognition.load_image_file(image_file_path)
        new_face_encoding = face_recognition.face_encodings(new_image)[0]
        self.known_face_encodings.append(new_face_encoding)
        self.known_face_names.append(username)
        return

    def recognize_from_camera(self):
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True
        rawCapture = PiRGBArray(self.camera, size=(640, 480))

        for frame in self.camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame.array, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"

                    # # If a match was found in known_face_encodings, just use the first one.
                    # if True in matches:
                    #     first_match_index = matches.index(True)
                    #     name = known_face_names[first_match_index]

                    # Or instead, use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]

                    face_names.append(name)

            process_this_frame = not process_this_frame

            return face_names

