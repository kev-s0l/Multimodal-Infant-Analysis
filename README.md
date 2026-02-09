# Multimodal Infant Analysis Pipeline

This repository contains a modular analysis pipeline for infant movement, sleep, and language data. The code is intended for research use and supports feature extraction, visualization, and cross-modality analysis.

The project is organized into four main areas:
- Movement Analysis (H5 accelerometer data)
- Sleep Analysis (EDF and sleep profile text files)
- Language Analysis (LENA ITS files)
- Multimodal Analysis (combined analyses across modalities)

The code is designed to be reproducible, scriptable from the command line, and modular. No patient data is included in this repository.

---

## Project Structure

Multimodal-Infant-Analysis/
│
├── Movement Analysis/
│   ├── src/
│   │   ├── core/          # Computation only (no plotting, no file output)
│   │   ├── cli/           # Command-line scripts (print results, save CSV)
│   │   ├── plots/         # Plotting scripts
│   │   └── multimodal/    # Cross-modality analyses (e.g., CoV + Sleep)
│   ├── Graphs/            # Generated figures (not tracked in git)
│   └── movement_outputs/  # Generated CSV files (not tracked in git)
│
├── Sleep Analysis/
│   ├── src/
│   └── Graphs/
│
├── Language Analysis/
│   ├── src/
│   ├── lena_outputs/
│   └── Graphs/
│
├── Multimodal Analysis/
│   └── src/               # High-level combined analyses
│
├── LICENSE
└── README.md

---

## Data Privacy

Patient data is not included in this repository.

All raw data files (H5, EDF, ITS, sleep profiles, etc.) should be stored locally on your machine and must not be committed to this repository. Only code, configuration, and documentation are tracked in version control.

---

## Movement Analysis

The movement pipeline supports the following metrics computed in 30-second epochs:

- Acceleration magnitude
- Coefficient of Variation (CoV)
- Bowley-Galton skewness
- Scalar speed
- Velocity (X, Y, Z components)
- Zero-Crossing Rate (ZCR)
- Raw accelerometer visualization (downsampled)

Each metric is split into:
- core/  : computation only
- cli/   : command-line scripts that print results and save CSV files
- plots/ : scripts that generate figures

Example commands:

python -m src.cli.speed "C:\Path\To\File.h5" 16162  
python -m src.plots.plot_speed "C:\Path\To\File.h5" 16162  

---

## Sleep Analysis

Sleep analysis scripts handle:
- EDF-based signal processing
- Sleep stage parsing
- Sleep profile visualization
- Stage timelines and distributions

These scripts follow a similar structure to the movement analysis code.

---

## Language Analysis

The language analysis pipeline supports:
- Parsing LENA ITS files
- Extracting metadata
- Segment-level data extraction
- CTC, CVC, and AWC metrics
- Hourly and summary statistics
- CSV outputs and plots

---

## Multimodal Analysis

The Multimodal Analysis folder contains scripts that combine information from multiple data sources, such as sleep and movement.

An example is the CoV and sleep stage synchronization analysis, which:
- Loads movement data from an H5 file
- Loads sleep stages from a text file
- Cleans and filters the movement signal
- Computes 30-second CoV
- Aligns sleep stages to the movement timeline
- Produces two plots (full timeline and compressed sleep-only view)
- Prints summary statistics, including sleep efficiency

Example command:

python src/multimodal/cov_sleep_analysis.py \
  --h5 "C:\Path\To\Movement\File.h5" \
  --sensor 16162 \
  --sleep "C:\Path\To\SleepProfile.txt"

---

## Requirements

Typical dependencies include:

pip install numpy pandas matplotlib scipy h5py mne seaborn

The exact set of packages depends on which parts of the project are used.

---

## Design Notes

- core/ contains computation only and no plotting or file output
- cli/ contains scripts intended for batch or command-line use
- plots/ contains scripts that only generate figures
- multimodal/ contains higher-level analyses that combine data sources
- File paths are passed through command-line arguments rather than hard-coded
- Output files (figures and CSVs) are generated locally and should not be committed

---

## Project Context

This project supports multimodal analysis of infant development using:
- Movement data from accelerometers
- Sleep data from EEG and sleep staging
- Language environment data from LENA recordings

The code is intended for research workflows, exploratory analysis, and generation of figures and tables for reports or publications.

