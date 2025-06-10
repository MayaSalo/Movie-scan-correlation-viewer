# Movie-scan-correlation-viewer

This code visualizes neural pattern correlation matrices alongside a video stimulus. It allows users to interactively explore averaged time bins from a movie and inspect their corresponding positions in a time-point-by-time-point correlation matrix.
It allows the examination of specific scenes as they are divided by the brain (data-driven division).

🧠 Features
Loads a full movie (e.g., .mp4) and a precomputed correlation matrix (e.g., .mat).

Averages frames over specified time bins (default: 2.01 seconds).

Computes a population vector correlation matrix from the neural data. 

Aligns bins to start after a specific time point (default: from the 3rd bin).

Displays:

Left panel: the averaged movie frame for the current time bin.

Right panel: the correlation matrix, with a vertical line indicating the selected bin.

Interactive slider to explore time bins manually.

Progress and navigation messages printed to the MATLAB Command Window.

📂 Inputs
Movie file: Any standard format (e.g., .mp4), readable via VideoReader.

Neural activity: a 2D matrix of neural activity with dimensions: [voxels × TRs].

