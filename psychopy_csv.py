# ==========================================
# CSV TIMESTAMP EXTRACTOR & EDF ALIGNER
# ==========================================
# This script reads your PsychoPy CSV and uses your manual notes
# to calculate the exact offset needed for your main ERP script.

import pandas as pd
import sys

# 1. Configuration
csv_file_path = 'D:\\Desktop\\data_analysis\\psychopy.csv'

# Column Names (Check your CSV to confirm these match exactly)
timestamp_column = 'faces.started'  
condition_column = 'condition'         

# --- EDF ALIGNMENT DATA (From your manual notes) ---
# When did you press spacebar to start the test in the EDF recording?
edf_spacebar_min = 14
edf_spacebar_sec = 57

# When did the EDF recording end?
edf_end_min = 20
edf_end_sec = 45

# 2. Load and Clean CSV
print(f"Loading {csv_file_path}...")
try:
    df = pd.read_csv(csv_file_path)
except FileNotFoundError:
    print(f"\n❌ ERROR: Could not find the file '{csv_file_path}'. Check your file path!")
    sys.exit()

# 3. Handle Column Name Errors Safely
try:
    # Drop rows that don't have a stimulus timestamp
    df = df.dropna(subset=[timestamp_column])
except KeyError:
    print(f"\n❌ ERROR: Could not find the column '{timestamp_column}' in your CSV.")
    print("Here are the columns that ACTUALLY exist in your file:")
    print("-" * 50)
    for col in df.columns:
        if 'started' in str(col).lower() or 'time' in str(col).lower():
            print(f"  👉 '{col}'")
        else:
            print(f"  - '{col}'")
    sys.exit()

# 4. Extract Timeline and Calculate Offsets
if df.empty:
    print(f"\nERROR: The column '{timestamp_column}' exists, but it has no valid numbers in it!")
else:
    # PsychoPy Times
    first_stimulus_time = df[timestamp_column].iloc[0]
    last_stimulus_time = df[timestamp_column].iloc[-1]
    total_stimulus_duration = last_stimulus_time - first_stimulus_time
    total_trials = len(df)
    
    # EDF Times
    edf_start_sec = (edf_spacebar_min * 60) + edf_spacebar_sec
    edf_end_sec_total = (edf_end_min * 60) + edf_end_sec
    edf_total_duration = edf_end_sec_total - edf_start_sec
    
    # Offset Calculation
    # Assuming PsychoPy's t=0 is close to when the spacebar was pressed.
    # We subtract PsychoPy's first stimulus time so we can give MNE a master offset.
    master_offset = edf_start_sec - first_stimulus_time
    
    print("\n" + "="*50)
    print("🎯 ALIGNMENT REPORT: PSYCHOPY vs EDF")
    print("="*50)
    print(f"Total Trials:              {total_trials} images flashed")
    print(f"PsychoPy Task Duration:    {total_stimulus_duration:.2f} seconds")
    print(f"EDF Recorded Duration:     {edf_total_duration:.2f} seconds")
    print("-" * 50)
    print(f"Spacebar Pressed in EDF @  {edf_start_sec:.2f} seconds ({edf_spacebar_min}m {edf_spacebar_sec}s)")
    print(f"First Face in PsychoPy  @  {first_stimulus_time:.2f} seconds")
    print("="*50)
    
    print("\n>>> HOW TO USE THIS IN MNE (erp_analysis.py):")
    print("You DO NOT need to crop your EDF file! Just open your main ERP analysis script")
    print("and set the time_offset_seconds variable to exactly this number:")
    print(f"\n      time_offset_seconds = {master_offset:.3f}\n")
    
    print("Why? Because MNE will take PsychoPy's first face time (e.g. 2.5s), add your offset")
    print(f"({master_offset:.3f}s), and perfectly slice the EDF at exactly {edf_start_sec:.3f}s!")