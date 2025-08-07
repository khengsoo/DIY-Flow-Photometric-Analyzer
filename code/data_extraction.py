import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Step 1: Load the Data
file_path = "absorbance_data.csv"  # Replace with your file's name if different
data = pd.read_csv(file_path)

# Clean column names (strip extra spaces)
data.columns = data.columns.str.strip()

# Extract absorbance and create a time column
absorbance = data['absorbance']
data['time'] = range(len(data))
time = data['time']

# Load predefined concentration intervals
concentration_ranges = pd.read_csv("concentration_ranges.csv")  # Expected columns: concentration, start_time, end_time

# Step 2: Detect Peaks
peaks, properties = find_peaks(
    absorbance,
    height=0.001,
    prominence=0.01,
    distance=3
)

# Step 3: Filter out bubble peaks using derivative method
derivative = np.gradient(absorbance)
filtered_peaks = []
decay_threshold = -0.5  # Adjust based on data

for p in peaks:
    if p + 1 < len(derivative) and derivative[p + 1] >= decay_threshold:
        filtered_peaks.append(p)

# Step 4: Compute peak height relative to baseline
baseline_window = 5  # Number of points before peak to determine baseline
relative_peak_heights = {}

for peak in filtered_peaks:
    baseline_region = absorbance[max(0, peak - baseline_window):peak]
    baseline = np.min(baseline_region) if len(baseline_region) > 0 else 0
    relative_peak_heights[peak] = absorbance[peak] - baseline

# Step 5: Classify peaks based on predefined concentration time frames
classified_peaks = {row['concentration']: [] for _, row in concentration_ranges.iterrows()}

for peak in filtered_peaks:
    peak_time = time[peak]
    for _, row in concentration_ranges.iterrows():
        if row['start_time'] <= peak_time <= row['end_time']:
            classified_peaks[row['concentration']].append(relative_peak_heights[peak])
            break

# Step 6: Find the maximum filtered peak for each concentration
max_absorbance = {}
for conc, values in classified_peaks.items():
    if values:
        max_absorbance[conc] = max(values)
    else:
        max_absorbance[conc] = np.nan

# Step 7: Visualize classified peaks before saving
plt.figure(figsize=(10, 5))
plt.plot(time, absorbance, label='Absorbance')
colors = plt.cm.viridis(np.linspace(0, 1, len(classified_peaks)))

for (conc, values), color in zip(classified_peaks.items(), colors):
    peak_times = [time[filtered_peaks[i]] for i, val in enumerate(relative_peak_heights.values()) if val in values]
    peak_values = [val for val in relative_peak_heights.values() if val in values]
    plt.scatter(peak_times, peak_values, color=color, label=f'Conc {conc}', edgecolors='black')

plt.title("Classified Peaks in Absorbance-Time Plot")
plt.xlabel("Time (s)")
plt.ylabel("Relative Absorbance (Peak Height)")
plt.legend()
plt.grid()
plt.show()

# Step 8: Save processed data to CSV
decision = input("Confirm saving processed data? (yes/no): ")
if decision.lower() == 'yes':
    output_data = pd.DataFrame(list(max_absorbance.items()), columns=['Concentration', 'Max Absorbance'])
    output_data.to_csv("processed_absorbance_data_maximum.csv", index=False)
    print("Processed data saved successfully.")
else:
    print("Data saving aborted.")
