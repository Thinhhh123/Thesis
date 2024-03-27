import numpy as np
import cv2
import time

# Initialize the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# Load YOLOv3 configuration and weights
network = cv2.dnn.readNetFromDarknet(
    'F:\\python3.9\\video_test_fish\\yolov3-custom.cfg',
    'F:\\python3.9\\yolov3-custom_final_2.weights'
)

# Load class labels
with open('F:\\python3.9\\video_test_fish\\classes.txt') as f:
    labels = [line.strip() for line in f]

layers_names_all = network.getLayerNames()
layers_names_output = [layers_names_all[i - 1] for i in network.getUnconnectedOutLayers().flatten()]

probability_minimum = 0.01
threshold = 0.01

colours = np.random.randint(0, 255, size=(len(labels), 3), dtype='uint8')
last_time = time.time()
# Main loop to continuously capture images and detect objects
while True:

    # ret, image_BGR = cap.read()
    # if not ret:
    #     print("Error: Could not read frame.")
    #     break
    current_time = time.time()
    if current_time - last_time >= 5:
        ret, image_BGR = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

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

                    print('x= ', x_center)
                    print('y= ',y_center)
                    print('width= ',box_width)
                    print('height= ', box_height)

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

        cv2.imshow('Detections', image_BGR)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_image_path = f'F:\\python3.9\\code\\TestPic\\detected_image_{timestamp}.jpg'
        cv2.imwrite(output_image_path, image_BGR)

        print(f"Processed and saved image at {output_image_path}")

        # Xử lý sao mỗi 5s
        if cv2.waitKey(5000) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()