import cv2
import numpy as np

from ultralytics import YOLO
from analytic_image_processor import AnalyticImageProcessor

class MouseDetector:
    def __init__(self, path_to_video: str, path_to_weight_yolo: str, do_output_video: bool = False):
        self.input_video = cv2.VideoCapture(path_to_video)
        self.model = YOLO(path_to_weight_yolo)
        self.do_output_video = do_output_video

    def search_center_and_zones(self, video: cv2.VideoCapture) -> dict:
        _, frame = video.read()
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


    def detect(self):
        if self.do_output_video:
            output_video = cv2.VideoWriter('output_video_2.mp4',
                                           cv2.VideoWriter_fourcc(*'mp4v'),
                                           self.input_video.get(cv2.CAP_PROP_FPS),
                                           (int(self.input_video.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                            int(self.input_video.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        info_arena = self.search_center_and_zones(self.input_video)
        
        while True:
            ret, frame = self.input_video.read()
            if not ret:
                break
            info_mouse = self.search_mouse(frame)

            # модуль экспорта данных в эксель

            if self.do_output_video:
                frame_with_all = self.draw(frame, info_mouse, info_arena)
                output_video.write(frame_with_all)

        self.input_video.release()
        if self.do_output_video:
            output_video.release()
        cv2.destroyAllWindows()

    def draw(self, frame: np.ndarray, info_mouse: dict, info_arena: dict) -> np.ndarray:
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), 2, (0, 0, 255), -1)
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), info_arena['central_zone'][1], (0, 0, 255), 2)
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), info_arena['internal_zone'][1], (0, 255, 0), 2)
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), info_arena['middle_zone'][1], (255, 0, 0), 2)
        frame = cv2.circle(frame, (info_arena['x_center'], info_arena['y_center']), info_arena['outer_zone'][1], (255, 0, 255), 2)

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


