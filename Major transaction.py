import sys
import numpy as np
import cv2
import face_recognition
import random
import csv
import time
from datetime import datetime

# Step 1: Assign sender's details
f = open("data1.txt", "r")
lines = f.readlines()
sender_details = lines[0].strip()
f.close()

person_details = input('Enter Your Person Details:')
if person_details == sender_details:
    print('Your Details Correct, please go to the next step')
    
    # Step 2: OTP based
    def otp_based():
        # Check if the person's details are correct before generating OTP
        if person_details == sender_details:
            number = random.randint(1000, 9999)
            f = open('data.txt', 'w')
            f.write(str(number))
            f.close()

            my_msg = str(number)

            f = open("data.txt", "r")
            lines = f.readlines()
            test = lines[0].strip()
            f.close()

            # Here, you can add code to send OTP to the sender's phone number

            print("Your OTP has been sent")
            otp = input('Enter your OTP:')

            if otp == test:
                print('Correct OTP, you can continue the procedure')
                return True
            else:
                print('Wrong OTP, transaction cancelled')
                return False
        else:
            print('Wrong Number. Transaction Cancelled.')
            return False

    # Check if OTP verification is successful
    if otp_based():
        # Step 3: Face recognition for the receiver
        # Get a reference to webcam #0 (the default one)
        video_capture = cv2.VideoCapture(0)

        # Get the frame width, height, and frames per second (fps)
        frame_width = int(video_capture.get(3))
        frame_height = int(video_capture.get(4))
        fps = int(video_capture.get(5))

        # Define the codec and create a VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, fps, (frame_width, frame_height))

        # Load a sample picture and learn how to recognize it.
        sender_image = face_recognition.load_image_file("Sender.jpg")
        sender_face_encoding = face_recognition.face_encodings(sender_image)[0]

        # Create arrays of known face encodings and their names
        known_face_encodings = [sender_face_encoding]
        known_face_names = ["Sender"]

        while True:
            # Capture a single frame of video
            ret, frame = video_capture.read()

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown Person"

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

            # Display the resulting image
            cv2.imshow('Video', frame)

            # Write the frame into the output video file
            out.write(frame)

            # If the sender's face is recognized, take a photo and break out of the loop
            if "Sender" in face_names:
                cv2.imwrite('Sender_photo.jpg', frame)
                print("Sender's Face Recognized")
                break

            # Break the loop when 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Read receiver details from a CSV file
        with open('receiver_details.csv', 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            receiver_details = list(reader)

        # Prompt for receiver's phone number
        receiver_phone_number = input("Enter Receiver's Phone Number:")

        # Find receiver details by phone number in the CSV file
        receiver_name = None
        receiver_amount = None
        for row in receiver_details:
            expected_receiver_name, expected_receiver_phone_number, expected_receiver_amount = row
            expected_receiver_amount = int(expected_receiver_amount) if expected_receiver_amount else None
            if receiver_phone_number == expected_receiver_phone_number:
                receiver_name = expected_receiver_name
                receiver_amount = expected_receiver_amount
                break

        # Check if receiver details are found
        if receiver_name is not None:
            print(f"Receiver's Name: {receiver_name}")

            receiver_amount = input("Enter Amount:")

            # Validate receiver details
            if (
                receiver_phone_number == expected_receiver_phone_number
                and (receiver_amount == expected_receiver_amount or expected_receiver_amount is None)
            ):
                valid_receiver = True
            else:
                valid_receiver = False
                print("Transaction Failed. Incorrect Receiver Details")
        else:
            valid_receiver = False
            print("Receiver not found. Transaction Cancelled.")

        # Perform transaction if receiver details are correct
        if valid_receiver:
            print("Transaction Successful")
            print(f"Phone Number: {receiver_phone_number}")
            print(f"Amount: {receiver_amount}")

        # Print current date and time with seconds
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        print("Transaction Time:", current_time)

        # Release the VideoWriter and handle to the webcam
        out.release()
        video_capture.release()
        cv2.destroyAllWindows()
    else:
        print('Transaction Cancelled')
else:
    print('Wrong Number')
    time.sleep(1)
    # Print current date and time with seconds for canceled transaction
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print("Transaction Time:", current_time)
    print('Transaction Cancelled')
