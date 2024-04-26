import numpy as np
import cv2
import time
from picamera2 import Picamera2
import pyrebase
import depthai as dai


# Init Firebase
firebaseConfig = {
	'apiKey': "AIzaSyCPInwTkfl4IRlnD3NSrUqoMYhe0RkM34g",
	'authDomain': "thesis-thinh-f1f37.firebaseapp.com",
	'databaseURL': "https://thesis-thinh-f1f37-default-rtdb.firebaseio.com",
	'projectId': "thesis-thinh-f1f37",
	'storageBucket': "thesis-thinh-f1f37.appspot.com",
	'messagingSenderId': "719145362801",
	'appId': "1:719145362801:web:2ffe1455853f205a53c2d0",
	'measurementId': "G-30F3MDXYX7"

}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()


# Initialize the camera(USB Camera)
# cap = cv2.VideoCapture(0)

# Raspberry Pi Camera V3
# picam2 = Picamera2()
# picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
# picam2.start()

# Initialize the video
# cap = cv2.VideoCapture('video.mp4')
# if not cap.isOpened():
#     print("Error: Could not open camera.")
#     exit()

# OAK-D Camera
# Create pipeline
pipeline = dai.Pipeline()

# Define source and output
camRgb = pipeline.create(dai.node.ColorCamera)
xoutRgb = pipeline.create(dai.node.XLinkOut)

xoutRgb.setStreamName("rgb")

# Properties
camRgb.setPreviewSize(640, 480)
camRgb.setInterleaved(False)
camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

# Linking
camRgb.preview.link(xoutRgb.input)

# Load YOLOv3 configuration and weights
network = cv2.dnn.readNetFromDarknet('yolov3-custom.cfg', 'yolov3-custom_final_2.weights')

# Load class labels
with open('classes.txt') as f:
    labels = [line.strip() for line in f]

layers_names_all = network.getLayerNames()
layers_names_output = [layers_names_all[i - 1] for i in network.getUnconnectedOutLayers().flatten()]

probability_minimum = 0.7
threshold = 0.3

colours = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')
last_time = time.time()

with dai.Device(pipeline) as device:
    # Main loop to continuously capture images and detect objects
        # Output queue will be used to get the rgb frames from the output defined above
    qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
# Main loop to continuously capture images and detect objects
    while True:

        current_time = time.time()
        if current_time - last_time >= 5:
        
            #Camera USB or Video --> use
            # ret, image_BGR = cap.read()
            # if not ret:
            #     print("Error: Could not read frame.")
            #     break

            #Oak-D Camera
            inRgb = qRgb.get()  # blocking call, will wait until a new data has arrived
            # img_BGR = inRgb.getCvFrame()
            image_BGR = inRgb.getCvFrame()
        
            
            #Pi Camera V3
            # img_BGR = picam2.capture_array()
            # Chuyển đổi hình ảnh sang không gian màu RGB
            # image_BGR = cv2.cvtColor(img_BGR, cv2.COLOR_RGB2BGR)  

            h, w = image_BGR.shape[:2]
            blob = cv2.dnn.blobFromImage(image_BGR, 1 / 255.0, (416, 416), swapRB=True, crop=False)
            network.setInput(blob)

            start = time.time()
            output_from_network = network.forward(layers_names_output)
            end = time.time()

            print('Image processed in {:.5f} seconds'.format(end - start))

            bounding_boxes = []
            confidences = []
            class_numbers = []

            for result in output_from_network:
                for detected_objects in result:
                    scores = detected_objects[5:]
                    class_current = np.argmax(scores)
                    confidence_current = scores[class_current]

                    if confidence_current > probability_minimum:
                        box_current = detected_objects[0:4] * np.array([w, h, w, h])
                        x_center, y_center, box_width, box_height = box_current
                        x_min = int(x_center - (box_width / 2))
                        y_min = int(y_center - (box_height / 2))

                        bounding_boxes.append([x_min, y_min, int(box_width), int(box_height)])
                        confidences.append(float(confidence_current))
                        class_numbers.append(class_current)

                    # print('x= ', x_center)
                    # print('y= ',y_center)
                    # print('width= ',box_width)
                    # print('height= ', box_height)

            results = cv2.dnn.NMSBoxes(bounding_boxes, confidences, probability_minimum, threshold)

            counter = 1

            if len(results) > 0:
                for i in results.flatten():
                    x_min, y_min = bounding_boxes[i][0], bounding_boxes[i][1]
                    box_width, box_height = bounding_boxes[i][2], bounding_boxes[i][3]

                    colour_box_current = colours[class_numbers[i]].tolist()
                    cv2.rectangle(image_BGR, (x_min, y_min), (x_min + box_width, y_min + box_height), colour_box_current, 2)

                    text_box_current = '{}: {:.4f}'.format(labels[int(class_numbers[i])], confidences[i])
                    cv2.putText(image_BGR, text_box_current, (x_min, y_min - 5), cv2.FONT_HERSHEY_COMPLEX, 0.7, colour_box_current, 2)

                    counter += 1

            print('Number of objects detected:', counter - 1)

            # cv2.imshow('Detections', image_BGR)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_image_path = f'output/{timestamp}_{counter - 1}_detected_image.jpg'
            cv2.imwrite(output_image_path, image_BGR)

            # Chuyển đổi mảng hình ảnh thành một đối tượng bytes
            _, img_encoded = cv2.imencode('.jpg', image_BGR)
            image_bytes = img_encoded.tobytes()

            # Gửi tệp hình ảnh đã mã hóa lên Firebase Storage
            storage.child(f'{timestamp}_{counter - 1}_detected_image.jpg').put(image_bytes)
            print("Image sent")

            print(f"Processed and saved image at {output_image_path}")
            
            # Xử lý sao mỗi 5s
            if cv2.waitKey(5000) & 0xFF == ord('q'):
                break                                                   

cv2.destroyAllWindows()
