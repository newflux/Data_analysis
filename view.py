# ==========================================
# EDF VISUALIZER AND CROPPER
# ==========================================
# This script lets you view your raw EDF, find the exact timestamp
# you want to start from, crop the data, and save a clean copy.

import mne

# 1. Configuration
input_file = 'D:\\Desktop\\data_analysis\\CogniSync_Log_HARSHITH_P_SN170_20260622_185330.edf'
output_file = 'aligned_data-raw.fif'  # Saving as .fif (MNE's native format) is much safer and faster than re-encoding to EDF

# 2. Load the Raw Data
print(f"Loading {input_file}...")
raw = mne.io.read_raw_edf(input_file, preload=True)

# Apply a basic filter just so it's easier to look at visually
raw.filter(l_freq=0.5, h_freq=40.0)

# 3. Interactive Visualization
print("\n>>> OPENING INTERACTIVE VIEWER <<<")
print("- Use your arrow keys to scroll left/right.")
print("- Look at the X-axis (bottom) to find the exact time (in seconds) where you want to cut.")
print("- Close the window when you have your start and end times written down.")
raw.plot(block=True, title="Raw EEG Viewer (Find your cut times)", duration=10.0)

# 4. Prompt User for Cropping
print("\nViewer closed.")
start_time_str = input("Enter the START time to cut from (in seconds, e.g., 12.5) or press Enter to keep the start: ")
end_time_str = input("Enter the END time to cut at (in seconds, e.g., 300.0) or press Enter to keep the end: ")

# Convert inputs to floats (or None if left blank)
tmin = float(start_time_str) if start_time_str.strip() else 0.0
tmax = float(end_time_str) if end_time_str.strip() else raw.times[-1]

# 5. Crop and Save
print(f"\nCropping data from {tmin}s to {tmax}s...")
raw_cropped = raw.crop(tmin=tmin, tmax=tmax)

print(f"Saving aligned data to {output_file}...")
raw_cropped.save(output_file, overwrite=True)

print("\nDONE! You can now use this aligned .fif file in your main ERP analysis script.")