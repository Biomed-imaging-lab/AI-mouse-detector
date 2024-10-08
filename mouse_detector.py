import cv2
import numpy as np
import os
import csv

from typing import List
from ultralytics import YOLO
from analytic_image_processor import AnalyticImageProcessor
from calculator import Calculator
from calculator_speed import CalculatorSpeed


class MouseDetector:
    def __init__(self, path_to_video: str, path_to_weight_yolo: str, do_output_video: bool = False):
        self.path_to_video = path_to_video
        self.input_video = cv2.VideoCapture(path_to_video)
        self.do_output_video = do_output_video
        self.output_video = self.create_output_video()

        if not self.input_video.isOpened():
            self.input_video.release()
            raise ValueError(f"[ERROR]: Couldn't open the video {path_to_video}")

        self.output_name_csv = self.get_name_output_csv(path_to_video)
        self.model = YOLO(path_to_weight_yolo)
        self.calculator_speed = CalculatorSpeed()

        with open(f'{self.output_name_csv}.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time, m:s', '(X, Y), (px, px)', 'Central zone',
                             'Internal zone', 'Middle zone', 'Outer zone', 'Angle btw head&body, degrees', 'Speed, m/s'])

    def detect(self):
        info_arena = self.search_center_and_zones()

        self.processing_video(info_arena)

    def processing_video(self, info_arena):
        frame_number = 0
        fps = self.input_video.get(cv2.CAP_PROP_FPS)

        while True:
            ret, frame = self.input_video.read()
            if not ret:
                break

            info_mouse = self.search_mouse(frame)

            if self.is_mouse_found(info_mouse):
                time_frame = self.get_time_frame(frame_number, fps)
                static_data = self.calculate_static_parameters_of_mouse(info_mouse, info_arena, time_frame)

                speed = self.calculate_speed(info_mouse, frame_number, fps)
                static_data.append(speed)

                self.export_to_csv(static_data)

            frame_number += 1

            if self.do_output_video:
                frame_with_all = self.draw(frame, info_mouse, info_arena)
                self.output_video.write(frame_with_all)

        self.release_video()

    def search_center_and_zones(self) -> dict:
        _, frame = self.input_video.read()
        frame_analyzer = AnalyticImageProcessor(frame)
        frame_analyzer.search_zones()
        info_arena = {
            'x_center': frame_analyzer.x_center,
            'y_center': frame_analyzer.y_center,
            'radius_arena': frame_analyzer.radius_arena,
            'central_zone': frame_analyzer.central_zone,
            'internal_zone': frame_analyzer.internal_zone,
            'middle_zone': frame_analyzer.middle_zone,
            'outer_zone': frame_analyzer.outer_zone
        }
        return info_arena

    def search_mouse(self, image: np.ndarray) -> dict:
        results = self.model(image)
        xy = results[0].keypoints.xy.cpu().numpy().astype(int)
        if len(xy[0]) != 0:
            info_mouse = {
                'point_nose': xy[0][0],
                'point_r_ear': xy[0][1],
                'point_l_ear': xy[0][2],
                'point_near': xy[0][3],
                'point_r_side': xy[0][4],
                'point_l_side': xy[0][5],
                'point_tail': xy[0][6]
            }
            return info_mouse
        else:
            return {}

    def is_mouse_found(self, info_mouse: dict) -> bool:
        return len(info_mouse) != 0

    def create_output_video(self):
        if self.do_output_video:
            output_video = cv2.VideoWriter(f'processed_{self.path_to_video}',
                                           cv2.VideoWriter_fourcc(*'mp4v'),
                                           self.input_video.get(cv2.CAP_PROP_FPS),
                                           (int(self.input_video.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                            int(self.input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))))
            return output_video
        else:
            return None

    def release_video(self):
        self.input_video.release()
        if self.do_output_video:
            self.output_video.release()
        cv2.destroyAllWindows()

    def get_time_frame(self, frame_number: int, fps: float):
        current_time_seconds = frame_number / fps
        minutes, seconds = divmod(current_time_seconds, 60)
        minutes_str = f'{int(minutes):02d}'
        seconds_str = f'{seconds:05.2f}'.replace('.', ',')
        return minutes_str, seconds_str

    def calculate_static_parameters_of_mouse(self, info_mouse: dict, info_arena: dict, time_frame: tuple[str, str]) -> List:
        calculator = Calculator(info_mouse, info_arena, time_frame)
        return calculator.calculate()

    def calculate_speed(self, info_mouse, frame_number, fps):
        current_time_seconds = frame_number / fps
        speed = self.calculator_speed.update(info_mouse, current_time_seconds)
        return speed

    def get_name_output_csv(self, path_to_video: str):
        output_filename = os.path.basename(path_to_video)
        name = output_filename.split('.')[0]
        return name

    def export_to_csv(self, row_data: list):
        with open(f'{self.output_name_csv}.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row_data)

    def draw(self, frame: np.ndarray, info_mouse: dict, info_arena: dict) -> np.ndarray:
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), 2, (0, 0, 255), -1)
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), info_arena['central_zone'][1], (0, 0, 255), 2)
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), info_arena['internal_zone'][1], (0, 255, 0), 2)
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), info_arena['middle_zone'][1], (255, 0, 0), 2)
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), info_arena['outer_zone'][1], (255, 0, 255), 2)

        if self.is_mouse_found(info_mouse):
            frame = cv2.line(frame, (info_mouse['point_nose'][0], info_mouse['point_nose'][1]), (info_mouse['point_r_ear'][0], info_mouse['point_r_ear'][1]), (0, 255, 255), 2)
            frame = cv2.line(frame, (info_mouse['point_nose'][0], info_mouse['point_nose'][1]), (info_mouse['point_l_ear'][0], info_mouse['point_l_ear'][1]), (0, 255, 255), 2)
            frame = cv2.line(frame, (info_mouse['point_r_ear'][0], info_mouse['point_r_ear'][1]), (info_mouse['point_near'][0], info_mouse['point_near'][1]), (0, 255, 255), 2)
            frame = cv2.line(frame, (info_mouse['point_l_ear'][0], info_mouse['point_l_ear'][1]), (info_mouse['point_near'][0], info_mouse['point_near'][1]), (0, 255, 255), 2)
            frame = cv2.line(frame, (info_mouse['point_near'][0], info_mouse['point_near'][1]), (info_mouse['point_r_side'][0], info_mouse['point_r_side'][1]), (0, 255, 255), 2)
            frame = cv2.line(frame, (info_mouse['point_near'][0], info_mouse['point_near'][1]), (info_mouse['point_l_side'][0], info_mouse['point_l_side'][1]), (0, 255, 255), 2)
            frame = cv2.line(frame, (info_mouse['point_l_side'][0], info_mouse['point_l_side'][1]), (info_mouse['point_tail'][0], info_mouse['point_tail'][1]), (0, 255, 255), 2)
            frame = cv2.line(frame, (info_mouse['point_r_side'][0], info_mouse['point_r_side'][1]), (info_mouse['point_tail'][0], info_mouse['point_tail'][1]), (0, 255, 255), 2)

            frame = cv2.circle(frame, (info_mouse['point_nose'][0], info_mouse['point_nose'][1]), 3, (0, 0, 255), -1)
            frame = cv2.circle(frame, (info_mouse['point_r_ear'][0], info_mouse['point_r_ear'][1]), 3, (0, 255, 0), -1)
            frame = cv2.circle(frame, (info_mouse['point_l_ear'][0], info_mouse['point_l_ear'][1]), 3, (0, 255, 0), -1)
            frame = cv2.circle(frame, (info_mouse['point_near'][0], info_mouse['point_near'][1]), 3, (0, 0, 255), -1)
            frame = cv2.circle(frame, (info_mouse['point_r_side'][0], info_mouse['point_r_side'][1]), 3, (255, 0, 0), -1)
            frame = cv2.circle(frame, (info_mouse['point_l_side'][0], info_mouse['point_l_side'][1]), 3, (255, 0, 0), -1)
            frame = cv2.circle(frame, (info_mouse['point_tail'][0], info_mouse['point_tail'][1]), 3, (0, 0, 255), -1)

        return frame


