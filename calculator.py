import numpy as np


class Calculator:
    def __init__(self, info_mouse: dict, info_arena: dict, time_frame: tuple[int, int]):
        self.info_mouse = info_mouse
        self.info_arena = info_arena
        self.time_frame = time_frame

    def calculate(self):
        row_data = [self.time_frame]
        xy = self.calculate_xy_mouse()
        row_data.append(xy)

        zoning = self.calculate_zone_mouse()
        row_data.append(zoning)

        angle = self.calculate_angle_head_body()
        row_data.append(angle)

        return row_data

    def calculate_center_of_mouse(self) -> tuple[int, int]:
        center_head = (self.info_mouse['point_nose'][0] // 2 + self.info_mouse['point_near'][0] // 2,
                       self.info_mouse['point_nose'][1] // 2 + self.info_mouse['point_near'][1] // 2)
        center_body = (self.info_mouse['point_near'][0] // 2 + self.info_mouse['point_tail'][0] // 2,
                       self.info_mouse['point_near'][1] // 2 + self.info_mouse['point_tail'][1] // 2)

        center_mouse = (center_head[0] // 2 + center_body[0] // 2, center_head[1] // 2 + center_body[1] // 2)
        return center_mouse

    def change_coordinate_system(self, x_old: int, y_old: int) -> tuple[int, int]:
        x_center, y_center = (self.info_arena['x_center'], self.info_arena['y_center'])
        new_x = x_old - x_center
        new_y = y_center - y_old
        return new_x, new_y

    def calculate_xy_mouse(self) -> tuple[int, int]:
        x_mouse, y_mouse = self.calculate_center_of_mouse()
        new_x_mouse, new_y_mouse = self.change_coordinate_system(x_mouse, y_mouse)
        return new_x_mouse, new_y_mouse

    def calculate_zone_mouse(self) -> tuple[bool, ...]:
        zoning_dict = {
            self.info_arena['central_zone']: 0,
            self.info_arena['internal_zone']: 0,
            self.info_arena['middle_zone']: 0,
            self.info_arena['outer_zone']: 0
        }
        for keypoint in self.info_mouse.values():
            new_x, new_y = self.change_coordinate_system(keypoint[0], keypoint[1])
            distance = np.sqrt((new_x - self.info_arena['x_center'])**2 +
                               (new_y - self.info_arena['y_center'])**2)
            for (r_min, r_max), value in zoning_dict.items():
                if r_min < distance < r_max:
                    value += 1
        values = list(zoning_dict.values())
        max_index = values.index(max(values))
        result = [False] * len(values)
        result[max_index] = True

        return tuple(result)

    def calculate_angle_head_body(self):
        vector_body = (self.info_mouse['point_near'][0] - self.info_mouse['point_tail'][0],
                       self.info_mouse['point_near'][1] - self.info_mouse['point_tail'][1])

        vector_head = (self.info_mouse['point_near'][0] - self.info_mouse['point_tail'][0],
                       self.info_mouse['point_nose'][1] - self.info_mouse['point_nose'][1])

        length_vector_body = np.linalg.norm(vector_body)
        length_vector_head = np.linalg.norm(vector_head)

        cos_angle = np.dot(vector_body, vector_head) / (length_vector_head * length_vector_body)
        return np.arccos(cos_angle)




