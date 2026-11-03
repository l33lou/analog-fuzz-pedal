#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

#pragma pack(push, 1)
typedef struct {
    char     chunk_id[4];
    uint32_t chunk_size;
    char     format[4];
    char     subchunk1_id[4];
    uint32_t subchunk1_size;
    uint16_t audio_format;
    uint16_t num_channels;
    uint32_t sample_rate;
    uint32_t byte_rate;
    uint16_t block_align;
    uint16_t bits_per_sample;
    char     subchunk2_id[4];
    uint32_t subchunk2_size;
} WAVHeader;
#pragma pack(pop)

// Soft clipping function simulating 1N4148 feedback diode pair
double diode_clip(double input, double drive) {
    double x = input * drive;
    // Non-linear saturation model (tanh approximation)
    return tanh(x);
}

// First-order IIR Low-Pass Filter
double lpf(double input, double *state, double cutoff, double fs) {
    double rc = 1.0 / (2.0 * M_PI * cutoff);
    double dt = 1.0 / fs;
    double alpha = dt / (rc + dt);
    *state = *state + alpha * (input - *state);
    return *state;
}

// First-order IIR High-Pass Filter
double hpf(double input, double *in_prev, double *out_prev, double cutoff, double fs) {
    double rc = 1.0 / (2.0 * M_PI * cutoff);
    double dt = 1.0 / fs;
    double alpha = rc / (rc + dt);
    double out = alpha * (*out_prev + input - *in_prev);
    *in_prev = input;
    *out_prev = out;
    return out;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        printf("Usage: %s <input.wav> <output.wav> <sustain: 1.0-50.0> <tone: 0.0-1.0>\n", argv[0]);
        return 1;
    }

    float sustain = atof(argv[3]);
    float tone = atof(argv[4]);

    FILE *fin = fopen(argv[1], "rb");
    FILE *fout = fopen(argv[2], "wb");

    if (!fin || !fout) {
        perror("File opening error");
        return 1;
    }

    WAVHeader header;
    fread(&header, sizeof(WAVHeader), 1, fin);
    fwrite(&header, sizeof(WAVHeader), 1, fout);

    uint32_t num_samples = header.subchunk2_size / (header.bits_per_sample / 8);
    double fs = (double)header.sample_rate;

    // Filter states
    double lpf_state = 0.0;
    double hpf_in_prev = 0.0, hpf_out_prev = 0.0;

    int16_t raw_sample;
    while (fread(&raw_sample, sizeof(int16_t), 1, fin)) {
        // Convert integer PCM to normalized double [-1.0, 1.0]
        double x = (double)raw_sample / 32768.0;

        // Stage 1: Input Booster (Q1)
        double stage1 = x * 2.5;

        // Stage 2 & 3: Clipping Stages (Q2/Q3 with 1N4148 feedback pairs)
        double stage2 = diode_clip(stage1, sustain);
        double stage3 = diode_clip(stage2, sustain * 0.8);

        // Stage 4: Passive Tone Control blending
        double lp_out = lpf(stage3, &lpf_state, 795.0, fs); // Low-pass ~800 Hz
        double hp_out = hpf(stage3, &hpf_in_prev, &hpf_out_prev, 1850.0, fs); // High-pass ~1.8 kHz

        // Blend low and high pass signals based on tone control knob
        double tone_blended = (1.0 - tone) * lp_out + tone * hp_out;

        // Output level scaling & Hard Safety Limiting
        double y = tone_blended * 0.8;
        if (y > 1.0) y = 1.0;
        if (y < -1.0) y = -1.0;

        int16_t out_pcm = (int16_t)(y * 32767.0);
        fwrite(&out_pcm, sizeof(int16_t), 1, fout);
    }

    fclose(fin);
    fclose(fout);
    printf("DSP simulation complete: %s generated successfully.\n", argv[2]);
    return 0;
}