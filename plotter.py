import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

from scipy.ndimage import gaussian_filter
from scipy.signal import savgol_filter

from calculator_speed import RADUIS_ARENA_IN_METERS

class Plotter:
    def __init__(self, path_to_beh, radius_arena):
        self.video_name = f'{path_to_beh[:len(path_to_beh) - 4]}'
        self.path_to_data = f'mouse_data\\{self.video_name}_data.xlsx'
        self.path_to_plots = f'mouse_data\\{self.video_name}_plots'
        os.makedirs(self.path_to_plots, exist_ok=True)
        self.df = pd.read_excel(self.path_to_data)
        self.radius_arena = radius_arena
        self.meters_in_px = RADUIS_ARENA_IN_METERS / self.radius_arena


    def plot(self):
        pass

    def plot_trajectory(self):
        start_x, start_y = self.df['X, px'].iloc[0], self.df['Y, px'].iloc[0]
        end_x, end_y = self.df['X, px'].iloc[-1], self.df['Y, px'].iloc[-1]

        plt.figure(figsize=(10, 10))

        plt.plot(self.df['X, px'], self.df['Y, px'], color='darkorange')

        circle = plt.Circle((0, 0), self.radius_arena, color='black', fill=False, linestyle='--', linewidth=1.5)
        plt.gca().add_artist(circle)

        plt.scatter(start_x, start_y, color='white', edgecolor='black', zorder=5, s=65, label="Start")
        plt.scatter(end_x, end_y, color='black', edgecolor='black', zorder=5, s=65, label="Finish")
        plt.scatter(0, 0, color='red', edgecolor='red', s=75, zorder=5, label="center")

        plt.xlim(-self.radius_arena, self.radius_arena)
        plt.ylim(-self.radius_arena, self.radius_arena)
        plt.gca().set_aspect('equal', adjustable='box')

        xticks_px = plt.gca().get_xticks()
        yticks_px = plt.gca().get_yticks()

        xticks_m = xticks_px * self.meters_in_px 
        yticks_m = yticks_px * self.meters_in_px

        plt.xticks(xticks_px, labels=[f"{tick:.2f}" for tick in xticks_m])  
        plt.yticks(yticks_px, labels=[f"{tick:.2f}" for tick in yticks_m])

        plt.title("Trajectory in Arena")
        plt.xlabel("X (m)")
        plt.ylabel("Y (m)")
        plt.legend()
        filename = os.path.join(self.path_to_plots, f'trajectory_{self.video_name}.png')
        plt.savefig(filename)

    def plot_speed(self):
        tick_positions = range(0, len(self.df), 30)
        tick_labels = self.df["Time, m:s"].iloc[tick_positions]

        window_length = 91
        polyorder = 4

        self.df['Smoothed Speed (Savitzky-Golay)'] = savgol_filter(self.df['Speed, m/s'], window_length, polyorder)

        plt.figure(figsize=(10, 5))
        plt.plot(self.df['Time, m:s'], self.df['Speed, m/s'], color='green', alpha=0.3, label="Original Speed")
        plt.plot(self.df['Time, m:s'], self.df['Smoothed Speed (Savitzky-Golay)'], color='red', label="Smoothed Speed (Savitzky-Golay)")
        plt.xticks(ticks=tick_positions, labels=tick_labels, rotation=45)
        plt.title("Speed over Time (Smoothed with Savitzky-Golay)")
        plt.xlabel("Time, m:s")
        plt.ylabel("Speed, m/s")
        plt.legend()
        filename = os.path.join(self.path_to_plots, f'speed_{self.video_name}.png')
        plt.savefig(filename)

    def plot_position_heatmap(self):
        x = self.df['X, px']
        y = self.df['Y, px']

        heatmap, xedges, yedges = np.histogram2d(x, y, bins=75, range=[[-self.radius_arena, self.radius_arena], [-self.radius_arena, self.radius_arena]])

        heatmap = gaussian_filter(heatmap, sigma=1.5)

        heatmap_log = np.log1p(heatmap)

        plt.figure(figsize=(10, 10))

        extent = [-self.radius_arena, self.radius_arena, -self.radius_arena, self.radius_arena]
        im = plt.imshow(heatmap_log.T, origin='lower', cmap='plasma', interpolation='bilinear', extent=extent)

        circle = plt.Circle((0, 0), self.radius_arena, color='white', fill=False, linestyle='--', linewidth=1.5)
        plt.gca().add_artist(circle)
        plt.scatter(0, 0, color='white', edgecolor='white', s=75, zorder=5, label="Center")
        plt.xlim(-self.radius_arena, self.radius_arena)
        plt.ylim(-self.radius_arena, self.radius_arena)
        plt.gca().set_aspect('equal', adjustable='box')

        xticks_px = plt.gca().get_xticks()
        yticks_px = plt.gca().get_yticks()

        xticks_m = xticks_px * self.meters_in_px 
        yticks_m = yticks_px * self.meters_in_px

        plt.xticks(xticks_px, labels=[f"{tick:.2f}" for tick in xticks_m])  
        plt.yticks(yticks_px, labels=[f"{tick:.2f}" for tick in yticks_m])

        cbar = plt.colorbar(im, label="Density")
        cbar.set_label("Density")
        plt.title("Position Heatmap (Log Scale)")
        plt.xlabel("X (px)")
        plt.ylabel("Y (px)")

        filename = os.path.join(self.path_to_plots, f'position_heatmap_log_{self.video_name}.png')
        plt.savefig(filename)


    def plot_velocity_heatmap(self):
        x = self.df['X, px']
        y = self.df['Y, px']
        speeds = self.df['Speed, m/s']

        speed_sum, xedges, yedges = np.histogram2d(
            x, y, weights=speeds, bins=75, range=[[-self.radius_arena, self.radius_arena], [-self.radius_arena, self.radius_arena]])
        count, _, _ = np.histogram2d(
            x, y, bins=75, range=[[-self.radius_arena, self.radius_arena], [-self.radius_arena, self.radius_arena]]
        )

        average_speed = np.divide(speed_sum, count, out=np.zeros_like(speed_sum), where=(count > 0))

        average_speed = gaussian_filter(average_speed, sigma=1.5)

        plt.figure(figsize=(10, 10))
        extent = [-self.radius_arena, self.radius_arena, -self.radius_arena, self.radius_arena]
        im = plt.imshow(average_speed.T, origin='lower', cmap='hot', interpolation='bilinear', extent=extent)

        circle = plt.Circle((0, 0), self.radius_arena, color='white', fill=False, linestyle='--', linewidth=1.5)
        plt.gca().add_artist(circle)

        plt.scatter(0, 0, color='white', edgecolor='white', s=75, zorder=5, label="Center")

        plt.xlim(-self.radius_arena, self.radius_arena)
        plt.ylim(-self.radius_arena, self.radius_arena)
        plt.gca().set_aspect('equal', adjustable='box')
        xticks_px = plt.gca().get_xticks()
        yticks_px = plt.gca().get_yticks()

        xticks_m = xticks_px * self.meters_in_px 
        yticks_m = yticks_px * self.meters_in_px

        plt.xticks(xticks_px, labels=[f"{tick:.2f}" for tick in xticks_m])  
        plt.yticks(yticks_px, labels=[f"{tick:.2f}" for tick in yticks_m])
        cbar = plt.colorbar(im, label="Average Speed (m/s)")
        plt.title("Mouse Velocity Heatmap (Average Speed)")
        plt.xlabel("X (px)")
        plt.ylabel("Y (px)")
        filename = os.path.join(self.path_to_plots, f'position_average_speed_{self.video_name}.png')
        plt.savefig(filename)