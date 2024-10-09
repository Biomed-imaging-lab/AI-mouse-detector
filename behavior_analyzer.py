import numpy as np

from ultralytics import YOLO

COUNT_FRAMES_IN_COMPOSITE_IMG = 21


class BehaviorAnalyzer:
    def __init__(self, height, width, path_to_behavior_weight_yolo):
        self.buffer_img = []
        self.buffer_behaviors = []

        self.height = height
        self.width = width
        self.model = YOLO(path_to_behavior_weight_yolo)
        self.index_frame = None

    def set_index_frame(self, frame_number):
        if self.index_frame is None:
            self.index_frame = frame_number

    def create_composite_frame(self):
        composite_img = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        index_current_img = COUNT_FRAMES_IN_COMPOSITE_IMG // 2

        green_component = 0
        for i in range(index_current_img):
            green_component += self.buffer_img[i][:, :, 1]
        green_component = green_component // index_current_img  # mean

        red_component = self.buffer_img[index_current_img][:, :, 2]

        blue_component = 0
        for i in range(index_current_img + 1, len(self.buffer_img)):
            blue_component += self.buffer_img[i][:, :, 0]

        composite_img[:, :, 1] = green_component
        composite_img[:, :, 2] = red_component
        composite_img[:, :, 0] = blue_component

        return composite_img

    def analyze(self):
        composite_img = self.create_composite_frame()
        results = self.model(composite_img)
        for result in results:
            probs = result.probs
            info_behavior_mouse = {}
            for key, value in self.model.names:
                info_behavior_mouse[value] = float(probs.data[key])


