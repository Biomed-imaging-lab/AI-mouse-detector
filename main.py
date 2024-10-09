from mouse_detector import MouseDetector

import time

PATH_TO_WEIGHT_YOLO = 'weights/weights_yolo.pt'
PATH_TO_BEHAVIOR_WEIGHT_YOLO = 'weights/behavior_weights_yolo.pt'
PATH_TO_VIDEO = 'test5.mp4'

if __name__ == "__main__":
    start = time.time()

    mouse_detector = MouseDetector(PATH_TO_VIDEO, PATH_TO_WEIGHT_YOLO, PATH_TO_BEHAVIOR_WEIGHT_YOLO, False)
    mouse_detector.detect()

    end = time.time()
    print('Время работы: ', end - start)