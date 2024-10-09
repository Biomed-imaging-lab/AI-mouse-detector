import numpy as np
import pandas
import os
import csv

from ultralytics import YOLO

COUNT_FRAMES_IN_COMPOSITE_IMG = 21


class BehaviorAnalyzer:
    def __init__(self, height, width, path_to_behavior_weight_yolo, path_to_video):
        self.buffer_img = []
        self.buffer_behaviors = []
        self.info_behavior_of_mouse = None

        self.height = height
        self.width = width
        self.model = YOLO(path_to_behavior_weight_yolo)
        self.shift = None

        self.output_name_csv = self.get_name_output_csv(path_to_video)
        self.init_csv_file()

    def init_csv_file(self):
        row = []
        for value in self.model.names.values():
            row.append(value)
        with open(f'{self.output_name_csv}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)


    def set_shift(self, frame_number):
        if self.shift is None:
            self.shift = frame_number

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

    def update_buffer(self, frame):
        if self.buffer_is_full():
            self.buffer_img.pop(0)
            self.buffer_img.append(frame)
        else:
            self.buffer_img.append(frame)

    def buffer_is_full(self):
        return len(self.buffer_img) >= COUNT_FRAMES_IN_COMPOSITE_IMG

    def analyze(self):
        composite_img = self.create_composite_frame()
        results = self.model(composite_img)
        for result in results:
            probs = result.probs
            print(probs.data)
            print(probs.top5conf)
            print(self.model.names)
            probs_behavior_mouse = []
            for key in self.model.names.keys():
                probs_behavior_mouse.append(round(float(probs.data[key]), 3))

        #self.info_behavior_of_mouse = info_behavior_mouse
        self.export_to_csv(probs_behavior_mouse)

    def get_name_output_csv(self, path_to_video):
        output_filename = os.path.basename(path_to_video)
        name = output_filename.split('.')[0] + '_beh'
        return name

    def export_to_csv(self, probs_behavior_mouse):
        with open(f'{self.output_name_csv}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(probs_behavior_mouse)





