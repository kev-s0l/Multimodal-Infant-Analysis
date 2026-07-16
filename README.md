# Multimodal Infant Analysis

This repository contains Python analysis pipelines for infant language, movement,
sleep, and multimodal movement-sleep data. The code is organized as independent
modules that can be run from each module's `src` directory.

## Analyses Included

- **Language Analysis**: parses LENA `.its` XML files, extracts segment and
  conversation data, computes AWC/CVC/CTC metrics, and creates daily summary
  plots.
- **Movement Analysis**: loads accelerometer data from H5 sensor files and
  computes movement features such as raw acceleration, acceleration magnitude,
  velocity, speed, coefficient of variation, skewness, Bowley-Galton skewness,
  and zero-crossing rate.
- **Sleep Analysis**: supports text-based infant sleep profile parsing and an
  EDF fallback workflow using MNE and YASA sleep staging with infant-stage
  mapping.
- **Multimodal Analysis**: combines accelerometer movement variability with
  sleep profile data and compares CoV-based movement summaries across paired
  subjects.

## Installation

Create and activate a Python environment, then install the project dependencies:

```bash
pip install -r requirements.txt
```

The scripts are written as local module pipelines. Run commands from the `src`
directory for the analysis area you want to use so imports such as `core` and
`plots` resolve correctly.

## Desktop Application

This repository also includes a PySide6 desktop UI for running analyses without
automatic CSV or PNG output. Results appear in app tables/messages, and graphs
render inside the application.

```bash
python -m app.main
```

To build a Windows one-folder executable:

```powershell
.\scripts\build_desktop_app.ps1
```

The executable is written to `dist\MultimodalInfantAnalysis\`.

## Repository Structure

```text
Language Analysis/
  src/
    cli/
    core/
    plots/

Movement Analysis/
  src/
    cli/
    core/
    plots/

Sleep Analysis/
  src/
    edf_fallback/
      cli/
      core/
      plot/
    txt_sleep_profile/
      cli/
      core/
      plots/

Multimodal Analysis/
  src/
    cli/
    core/
    plots/
```

## Language Analysis

The language pipeline processes a LENA `.its` XML file and produces language
development metrics over the recording period.

It extracts:

- Recording metadata
- Segment-level language data
- Conversation-level data
- Adult Word Count (AWC)
- Child Vocalization Count (CVC)
- Conversational Turn Count (CTC)
- Hourly and daily summaries

### Run ITS Extraction

```bash
cd "Language Analysis/src"
python -m cli.run_extraction --its "path/to/file.its"
```

This creates `lena_extraction_output/` with:

- `recording_info.csv`
- `segments.csv`
- `conversations.csv`
- `summary_statistics.csv`
- `hourly_analysis.csv` when hourly data is available

### Run Daily Summary

```bash
cd "Language Analysis/src"
python -m cli.run_daily_summary
```

This reads from `lena_extraction_output/` and creates:

- `lena_visualizations/daily_summary_AWC_CVC_CTC.png`

## Movement Analysis

The movement pipeline reads accelerometer data from H5 files. Each command
requires:

- `--h5`: path to the input H5 file
- `--sensor-id`: sensor ID under the file's `Sensors` group

Run these commands from `Movement Analysis/src`.

```bash
cd "Movement Analysis/src"
```

### Raw Acceleration

```bash
python -m cli.run_raw_accel --h5 "path/to/file.h5" --sensor-id "SENSOR_ID"
```

Optional:

```bash
python -m cli.run_raw_accel --h5 "path/to/file.h5" --sensor-id "SENSOR_ID" --step 500
```

### Acceleration Magnitude

```bash
python -m cli.run_acc_magnitude --h5 "path/to/file.h5" --sensor-id "SENSOR_ID"
```

### Velocity Statistics

```bash
python -m cli.run_velocity --h5 "path/to/file.h5" --sensor-id "SENSOR_ID"
```

### Speed Statistics

```bash
python -m cli.run_speed --h5 "path/to/file.h5" --sensor-id "SENSOR_ID"
```

### Coefficient of Variation

```bash
python -m cli.run_cov --h5 "path/to/file.h5" --sensor-id "SENSOR_ID"
```

### Skewness

```bash
python -m cli.run_skewness --h5 "path/to/file.h5" --sensor-id "SENSOR_ID"
```

### Bowley-Galton Skewness

```bash
python -m cli.run_bowley_skew --h5 "path/to/file.h5" --sensor-id "SENSOR_ID"
```

### Zero-Crossing Rate

```bash
python -m cli.run_zcr --h5 "path/to/file.h5" --sensor-id "SENSOR_ID"
```

Movement outputs are saved in `movement_outputs/`. File names use the input H5
file stem and the metric name, for example:

- `<input>_raw_accel.csv`
- `<input>_raw_accel_plot.png`
- `<input>_acc_magnitude_per_epoch.csv`
- `<input>_acceleration_magnitude_plot.png`
- `<input>_velocity_stats.csv`
- `<input>_velocity_plot.png`
- `<input>_speed_stats.csv`
- `<input>_speed_plot.png`
- `<input>_cov.csv`
- `<input>_cov_plot.png`
- `<input>_skewness.csv`
- `<input>_skewness_plot.png`
- `<input>_bowley_skew.csv`
- `<input>_bowley_skew_plot.png`
- `<input>_zcr.csv`
- `<input>_zcr_plot.png`

## Sleep Analysis

Sleep analysis has two workflows: one for text sleep profile files and one EDF
fallback workflow for sleep staging.

### Text Sleep Profile Workflow

Run from `Sleep Analysis/src/txt_sleep_profile`.

```bash
cd "Sleep Analysis/src/txt_sleep_profile"
python -m cli.run_txt_sleep_profile_main --sleep-file "path/to/sleep_profile.txt"
```

The parser expects semicolon-delimited sleep-stage rows with a timestamp before
the semicolon, such as `HH:MM:SS,fff;Stage`. Artifact rows marked `A` are skipped.

The workflow prints sleep-stage statistics and saves:

- `sleep_visualizations/sleep_profile_line_graph.png`

### EDF Fallback Workflow

Run from `Sleep Analysis/src/edf_fallback`.

```bash
cd "Sleep Analysis/src/edf_fallback"
python -m cli.run_edf_sleep_fallback --edf "path/to/file.edf"
```

Optional channel arguments:

```bash
python -m cli.run_edf_sleep_fallback --edf "path/to/file.edf" --eeg "C4:M1" --eog "E1:M2" --emg "EMG1"
```

Optional movement relabeling:

```bash
python -m cli.run_edf_sleep_fallback --edf "path/to/file.edf" --use-movement
```

This workflow:

- Loads EDF data with MNE.
- Runs YASA sleep staging.
- Maps YASA sleep stages to infant-oriented labels.
- Prints stage counts and prediction previews.
- Displays a hypnogram plot interactively.

## Multimodal Analysis

The multimodal workflows combine H5 accelerometer data with text sleep profile
data.

### CoV and Sleep Analysis

Run from `Multimodal Analysis/src`.

```bash
cd "Multimodal Analysis/src"
python -m cli.run_cov_sleep --h5 "path/to/file.h5" --sensor-id "SENSOR_ID" --sleep-file "path/to/sleep_profile.txt"
```

Optional title prefix:

```bash
python -m cli.run_cov_sleep --h5 "path/to/file.h5" --sensor-id "SENSOR_ID" --sleep-file "path/to/sleep_profile.txt" --title-prefix "Subject 01"
```

This workflow:

- Parses sleep start time and sleep states from the text sleep profile.
- Loads accelerometer data from the selected H5 sensor.
- Filters acceleration magnitude and computes 30-second CoV windows.
- Prints alignment checks and summary analytics.
- Displays continuous, compressed sleep, state distribution, and hourly CoV
  plots interactively.

### Pairwise CoV Comparison

Run from `Multimodal Analysis/src`.

```bash
cd "Multimodal Analysis/src"
python -m cli.run_pair_cov_comparison --manifest "path/to/manifest.csv"
```

Optional output directory:

```bash
python -m cli.run_pair_cov_comparison --manifest "path/to/manifest.csv" --out-dir "reports"
```

The manifest CSV must contain:

- `pair_id`
- `subject_label`
- `h5_path`
- `sleep_path`
- `target_id`

The workflow writes:

- `reports/subject_summary.csv`
- `reports/pair_comparison.csv`

## Input Notes

- H5 movement files must contain `Sensors/<sensor-id>/Accelerometer` and
  `Sensors/<sensor-id>/Time`.
- H5 timestamps are interpreted as microsecond Unix timestamps.
- Movement and multimodal metrics are generally computed in 30-second epochs.
- Sleep profile text files should contain timestamped semicolon-delimited sleep
  states. Multimodal sleep parsing also looks for a `Start Time` metadata line;
  if no date is found there, it attempts to infer a `YYYYMMDD` date from the
  sleep file path.
- EDF fallback channel defaults are `C4:M1` for EEG, `E1:M2` for EOG, and
  `EMG1` for EMG. Override them if your EDF uses different channel names.

## Requirements

Core dependencies are listed in `requirements.txt` and include numerical,
plotting, H5, EDF, and sleep-staging libraries:

- numpy<2.4
- pandas
- matplotlib
- seaborn
- h5py
- scipy
- mne
- yasa
- scikit-learn
- edfio
- PySide6
- pyinstaller

## License

This project is licensed under the MIT License. See `LICENSE` for details.
