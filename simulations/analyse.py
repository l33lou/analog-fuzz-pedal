import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# --- Circuit Component Values (Green Russian / Civil War BMP) ---
R17 = 20e3      # Low-pass resistor (20k)
C11 = 10e-9     # Low-pass capacitor (10nF)
R18 = 22e3      # High-pass resistor (22k)
C10 = 3.9e-9    # High-pass capacitor (3.9nF)
R_pot = 100e3   # Tone potentiometer P2 (100k)

def tone_stack_transfer_function(alpha, freq):
    """
    Computes complex frequency response H(f) of the Big Muff tone stack.
    alpha: potentiometer position (0.0 = full bass, 0.5 = mid scoop, 1.0 = full treble)
    """
    s = 2j * np.pi * freq
    
    # Split potentiometer resistance based on wiper position alpha
    R_bass = alpha * R_pot
    R_treble = (1.0 - alpha) * R_pot
    
    # Admittances of individual branches
    Z_lp = R17 + R_bass + (1.0 / (s * C11))
    Z_hp = R18 + R_treble + (1.0 / (s * C10))
    
    # Transfer function V_out / V_in
    Y_lp = 1.0 / Z_lp
    Y_hp = 1.0 / Z_hp
    
    # Blended voltage divider ratio across wiper
    H = (Y_lp * (R_bass / (R17 + R_bass + 1.0/(s*C11))) + 
         Y_hp * (R18 / (R18 + R_treble + 1.0/(s*C10)))) / (Y_lp + Y_hp)
    return H

# Frequency sweep (10 Hz to 20 kHz)
freqs = np.logspace(1, 4.301, 1000)

plt.figure(figsize=(10, 6))
positions = [0.0, 0.25, 0.5, 0.75, 1.0]
labels = ['0.0 (Full Bass)', '0.25', '0.50 (Mid Scoop)', '0.75', '1.0 (Full Treble)']

for alpha, label in zip(positions, labels):
    H = tone_stack_transfer_function(alpha, freqs)
    mag_db = 20 * np.log10(np.abs(H))
    plt.semilogx(freqs, mag_db, label=f'Tone = {label}')

plt.title('Green Russian Big Muff Tone Stack Frequency Response')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Magnitude (dB)')
plt.grid(True, which='both', linestyle='--', alpha=0.6)
plt.legend()
plt.ylim(-30, 5)
plt.savefig('muff_tone_stack_bode.png')
plt.show()