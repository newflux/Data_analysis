# Master ERP Analysis Script using MNE-Python (CSV Marker Version)
# Fully configured for your N170 Data

import mne
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
# Path to your raw EEG file (EDF)
file_path = r'D:\Desktop\data_analysis\CogniSync_Log_HARSHITH_P_SN170_20260622_185330.edf'

# Path to your PsychoPy output CSV file
csv_file_path = r'D:\Desktop\data_analysis\psychopy.csv'

# The exact offset calculated from your script
time_offset_seconds = 1.0  

# CSV Column Names
timestamp_column = 'faces.started'  

# ⚠️ ACTION REQUIRED HERE ⚠️
# Open your CSV and find the column that tells you if the image was a face or not.
# It is likely 'imageFile' or 'sameOrDiff'. Change these two variables to match your CSV!
condition_column = 'sameOrDiff'         
target_label = 'different' # What exact text is in that column when a target face is shown?

# Event Dictionary
event_id_map = {
    'Standard': 0, 
    'Target': 1    
}

# Epoch window (in seconds)
# -0.2 (200ms before) to 0.6 (600ms after) is perfect for the N170 wave
tmin = -0.2
tmax = 0.6

# The channel you want to look at. For N170 (Faces), P7, P8, O1, or O2 are the best!
target_channel = 'P7' 

# ==========================================
# 2. LOAD AND FILTER DATA
# ==========================================
print("Loading raw data...")
raw = mne.io.read_raw_edf(file_path, preload=True)

# Set the standard 10-20 montage
montage = mne.channels.make_standard_montage('standard_1020')
raw.set_montage(montage, on_missing='ignore')

# Apply a Bandpass Filter
print("Filtering data (0.5 - 30 Hz)...")
raw.filter(l_freq=0.5, h_freq=30.0)

# ==========================================
# 3. ICA (INDEPENDENT COMPONENT ANALYSIS)
# ==========================================
print("Running ICA to find and remove eye blinks...")
ica = mne.preprocessing.ICA(n_components=None, random_state=97, max_iter=800)
ica.fit(raw)

print(">>> Look at the pop-up window. Click the component that looks like a blink to exclude it, then close the window.")
ica.plot_components(inst=raw)

print("Applying ICA cleaning to data...")
raw = ica.apply(raw)

# ==========================================
# 4. LOAD MARKERS FROM CSV AND CREATE EPOCHS
# ==========================================
print("Loading events from CSV...")
df = pd.read_csv(csv_file_path)

# Remove any rows where the timestamp is missing
df = df.dropna(subset=[timestamp_column])

# Get the sampling rate of your EEG board
sfreq = raw.info['sfreq']

# Build the events array manually
events = []

for index, row in df.iterrows():
    # 1. Get the timestamp and add your manual offset
    adjusted_time_sec = row[timestamp_column] + time_offset_seconds
    
    # 2. Convert seconds into exact EEG sample numbers
    sample_index = int(adjusted_time_sec * sfreq)
    
    # 3. Figure out if this row was a Target or a Standard
    if str(row[condition_column]) == target_label:
        event_code = event_id_map['Target']
    else:
        event_code = event_id_map['Standard']
        
    # MNE events require a 3-item list: [sample_number, 0, event_code]
    # We only add the event if it actually falls within our recorded EEG data
    if sample_index < len(raw.times):
        events.append([sample_index, 0, event_code])

# Convert list to numpy array
events = np.array(events, dtype=int)

# --- DEBUG INFO ---
print("\n" + "="*40)
print("🔍 DEBUG INFO")
print("="*40)
print(f"1. Total EEG Recording Length: {len(raw.times) / sfreq:.2f} seconds")
print(f"2. Valid Images found in CSV:  {len(df)} images")
if not df.empty:
    first_target_sec = df[timestamp_column].iloc[0] + time_offset_seconds
    last_target_sec = df[timestamp_column].iloc[-1] + time_offset_seconds
    print(f"3. First face looking at:      {first_target_sec:.2f} seconds")
    print(f"4. Last face looking at:       {last_target_sec:.2f} seconds")
print("="*40 + "\n")

print(f"Successfully injected {len(events)} events from CSV!")

print("Slicing data into epochs...")
epochs = mne.Epochs(
    raw, 
    events, 
    event_id=event_id_map,
    tmin=tmin, 
    tmax=tmax, 
    baseline=(None, 0), 
    preload=True
)

# ==========================================
# 5. AVERAGE AND PLOT THE ERP CURVES
# ==========================================
print("Averaging slices...")

target_evoked = epochs['Target'].average()
standard_evoked = epochs['Standard'].average()

fig, ax = plt.subplots(figsize=(10, 6))

mne.viz.plot_compare_evokeds(
    dict(Target=target_evoked, Standard=standard_evoked),
    picks=[target_channel] if target_channel in raw.ch_names else None,
    axes=ax,
    title=f'N170 ERP Comparison at Electrode {target_channel} (Offset: {time_offset_seconds}s)',
    show_sensors=False
)

plt.show()