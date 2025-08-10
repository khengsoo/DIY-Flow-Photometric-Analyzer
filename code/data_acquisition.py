import serial
import csv
import time
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Set up the serial connection (adjust 'COM3' to your Arduino's port)
ser = serial.Serial('COM3', 9600, timeout=1)
time.sleep(1)  # Give some time for the connection to establish

# Variables for baseline calculation
baseline_data = []
baseline_ready = False
I0 = None  # Baseline intensity (initial intensity)

# Lists for plotting
absorbance_data = []

# Open a CSV file to save the data
with open('absorbance_data.csv', 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Absorbance"])  # Write the header

    # Set up the real-time plot
    fig, ax = plt.subplots()
    line, = ax.plot([], [], label='Absorbance', color='red')
    ax.set_xlim(0, 100)  # Adjust as needed
    ax.set_ylim(-1, 1)  # Adjust based on expected absorbance range
    ax.set_xlabel("Time (data points)")
    ax.set_ylabel("Absorbance")
    plt.legend()

    def update_plot(frame):
        global I0, baseline_ready

        try:
            # Read data from Arduino
            line_data = ser.readline().decode('utf-8').strip()

            if line_data:
                print(line_data)  # Print raw reading
                transmittance = float(line_data)

                # Baseline calculation
                if not baseline_ready:
                    baseline_data.append(transmittance)

                    # Check for stability after collecting at least 5 readings
                    if len(baseline_data) >= 5:
                        if max(baseline_data) - min(baseline_data) < 15:  # Stability threshold
                            I0 = sum(baseline_data) / len(baseline_data)  # Calculate average
                            baseline_ready = True
                            print(f"Baseline established: I0 = {I0}")
                        else:
                            baseline_data.pop(0)  # Keep only the last 5 readings
                    return  # Skip plotting until baseline is ready

                # Absorbance calculation
                if I0 and transmittance > 0:
                    absorbance = math.log10(I0 / transmittance)
                    absorbance_data.append(absorbance)

                    # Save to CSV
                    csvwriter.writerow([absorbance])

                    # Update plot
                    line.set_data(range(len(absorbance_data)), absorbance_data)
                    ax.set_xlim(0, len(absorbance_data) + 10)
                    return line

        except KeyboardInterrupt:
            print("Logging stopped.")
            ser.close()
            plt.close()
            exit()
        except Exception as e:
            print(f"Error: {e}")

    # Animate the plot, update every 100 milliseconds
    ani = animation.FuncAnimation(fig, update_plot, interval=100, cache_frame_data=False)

    plt.show()

ser.close()
