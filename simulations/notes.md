## Recommended Simulation Apps

- LTspice (Analog Circuit & Transient Audio Simulation):  

The industry standard for modeling Big Muff BJT stages, transistor biasing, and $1\text{N}4148$ diode clipping. LTspice allows importing raw audio via .wave "input.wav" and exporting simulated pedal audio directly to .wav via .wave "output.wav" 16 44100 V(Out).
- KiCad & Ngspice:  

Excellent for schematic capture, 3D component footprint alignment inside enclosure boundaries, and native SPICE simulation.

- DIYLC (DIY Layout Creator): 

Ideal for verifying physical off-board wiring (3PDT footswitch, DC jack, input/output jacks, potentiometer spacing) against your enclosure layout.

- Falstad Circuit Simulator: 

Fast web-based simulator for visualizing real-time current flow and voltage clipping across individual BJT gain stages.

## My scripts 

### ```analyse.py```
Goal : Tone Stack Transfer Function & Bode Plot.  
The passive Big Muff tone stack consists of a low-pass filter ($R_{17} = 20\text{k}\Omega, C_{11} = 10\text{nF}$) and a high-pass filter ($R_{18} = 22\text{k}\Omega, C_{10} = 3.9\text{nF}$) connected across a $100\text{k}\Omega$ linear potentiometer ($P_2$).

### ```C DSP Processor``` 
Goal : Audio WAV Processing Engine  
This C program reads a 16-bit mono WAV file, applies input boost ($Q_1$), double diode soft-clipping ($Q_2/Q_3$ back-to-back $1\text{N}4148$ pairs via hyperbolic tangent modeling), digital biquad tone filtering, and output level control.

### ```comparison.py``` 
Python Verification & Empirical Comparison Script
This script takes three WAV audio files (Original Input, C DSP Output, and Analog Pedal Recording), calculates empirical frequency responses via cross-spectral density transfer function estimation, and plots Bode magnitude, Gain, and THD comparisons side-by-side.