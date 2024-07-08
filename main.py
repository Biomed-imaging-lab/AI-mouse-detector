from mouse_detector import MouseDetector

PATH_TO_WEIGHT_YOLO = 'weights/weights_yolo.pt'
PATH_TO_VIDEO = 'test3.mp4'

if __name__ == "__main__":
    mouse_detector = MouseDetector(PATH_TO_VIDEO, PATH_TO_WEIGHT_YOLO, True)
    mouse_detector.detect()
