import numpy as np
import cv2
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import os
from scipy.io import loadmat
from numpy import corrcoef

# ----------- CONFIG -----------

TR_DURATION = 2.01  # seconds per TR/bin
SKIP_TRS = 4        # how many TRs to skip before alignment starts - accounts for hemodynamic response

# ----------- USER INPUT -----------

movie_path = input("Enter path to movie file (e.g., .mp4): ")
data_path = input("Enter path to voxel x TRs matrix (.npy, .csv, or .mat): ")

# Load voxel x TRs matrix
if data_path.endswith('.npy'):
    data = np.load(data_path)
elif data_path.endswith('.csv'):
    data = np.loadtxt(data_path, delimiter=',')
elif data_path.endswith('.mat'):
    mat = loadmat(data_path)
    key = [k for k in mat.keys() if not k.startswith('__')][0]
    data = mat[key]
else:
    raise ValueError("Unsupported file format. Use .npy, .csv or .mat")

print(f"[INFO] Loaded voxel x TRs matrix of shape {data.shape}")

# Compute TR x TR correlation matrix
corr_matrix = np.corrcoef(data.T)
n_bins = corr_matrix.shape[0]
print(f"[INFO] Computed correlation matrix of shape {corr_matrix.shape}")

# Load movie and extract frames
cap = cv2.VideoCapture(movie_path)
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
print(f"[INFO] Loaded video with {total_frames} frames at {fps:.2f} FPS")

# Align movie to TR bins
start_time = SKIP_TRS * TR_DURATION
start_frame = int(start_time * fps)
frames_per_bin = int(TR_DURATION * fps)

avg_frames = []
bin_times = []

for t in range(n_bins):
    idx = start_frame + t * frames_per_bin
    frame_block = []

    for f in range(idx, min(idx + frames_per_bin, total_frames)):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_block.append(frame.astype(np.float32))

    if frame_block:
        avg = np.mean(frame_block, axis=0).astype(np.uint8)
    else:
        avg = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)

    avg_frames.append(avg)
    bin_times.append(idx / fps)

cap.release()

print(f"[INFO] Computed averaged movie frames for {len(avg_frames)} TR bins")

# ----------- GUI Visualization -----------

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
plt.subplots_adjust(bottom=0.2)

frame_disp = ax1.imshow(avg_frames[0])
ax1.set_title(f"TR 1 - Time {bin_times[0]:.2f}s")

im = ax2.imshow(corr_matrix, cmap='jet', vmin=-1, vmax=1)
vline = ax2.axvline(0, color='k', linewidth=2)
ax2.set_title("TR × TR Correlation Matrix")
fig.colorbar(im, ax=ax2)
ax2.set_xlabel("TR")
ax2.set_ylabel("TR")

ax_slider = plt.axes([0.2, 0.05, 0.6, 0.03])
slider = Slider(ax_slider, 'TR', 1, n_bins, valinit=1, valstep=1)

def update(val):
    t = int(slider.val) - 1
    frame_disp.set_data(avg_frames[t])
    ax1.set_title(f"TR {t+1} - Time {bin_times[t]:.2f}s")
    vline.set_xdata(t)
    fig.canvas.draw_idle()
    print(f"[NAV] Moved to TR {t+1} (Time: {bin_times[t]:.2f}s)")

slider.on_changed(update)

print("[INFO] GUI ready. Use the slider to navigate TRs.")
plt.show()
