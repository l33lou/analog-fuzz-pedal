import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal

def analyze_audio_pair(input_path, output_path):
    """
    Computes empirical transfer function magnitude (Bode) and RMS Gain.
    """
    fs_in, x = wavfile.read(input_path)
    fs_out, y = wavfile.read(output_path)

    # Convert PCM to normalized float
    if x.dtype == np.int16: x = x / 32768.0
    if y.dtype == np.int16: y = y / 32768.0

    # Truncate to matching sample length
    min_len = min(len(x), len(y))
    x, y = x[:min_len], y[:min_len]

    # Calculate transfer function estimate H(f) = Pxy(f) / Pxx(f)
    f, Pxx = signal.welch(x, fs=fs_in, nperseg=4096)
    f, Pxy = signal.csd(x, y, fs=fs_in, nperseg=4096)
    
    H = Pxy / (Pxx + 1e-12)
    gain_db = 20 * np.log10(np.abs(H) + 1e-6)

    # Calculate overall RMS Gain
    rms_in = np.sqrt(np.mean(x**2))
    rms_out = np.sqrt(np.mean(y**2))
    overall_gain_db = 20 * np.log10(rms_out / rms_in)

    return f, gain_db, overall_gain_db

# --- Execution & Comparison ---
raw_wav = "clean_bass.wav"
c_sim_wav = "c_processed.wav"
analog_wav = "pedal_recorded.wav"

try:
    f_c, mag_c, rms_gain_c = analyze_audio_pair(raw_wav, c_sim_wav)
    f_hw, mag_hw, rms_gain_hw = analyze_audio_pair(raw_wav, analog_wav)

    plt.figure(figsize=(11, 6))
    plt.semilogx(f_c, mag_c, label=f'C DSP Model (RMS Gain: {rms_gain_c:.2f} dB)', color='blue')
    plt.semilogx(f_hw, mag_hw, label=f'Physical Analog Pedal (RMS Gain: {rms_gain_hw:.2f} dB)', color='orange', linestyle='--')

    plt.title('Empirical Bode Comparison: C DSP Model vs Physical Pedal Hardware')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Measured Transfer Gain (dB)')
    plt.xlim(20, 20000)
    plt.grid(True, which='both', linestyle=':', alpha=0.7)
    plt.legend()
    plt.savefig('comparison_bode_plot.png')
    plt.show()

except FileNotFoundError:
    print("Place 'clean_bass.wav', 'c_processed.wav', and 'pedal_recorded.wav' in the working directory to execute comparison.")