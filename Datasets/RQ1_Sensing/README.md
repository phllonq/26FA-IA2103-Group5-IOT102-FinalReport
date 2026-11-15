# RQ1 – Sensing Dataset

## Purpose
This directory contains the three BMP280 measurement streams extracted from the supplied gateway CSV export.

## Sensor mapping
- `RQ1_S1_baseline.csv`: BMP280 #1, unshielded (`t1`, `p1`).
- `RQ1_S2_shielded.csv`: BMP280 #2, Pagoda Shield (`t2`, `p2`).
- `RQ1_S3_ground_reference.csv`: BMP280 #3, ground reference (`t3`, `p3`).

Temperature is expressed in °C and pressure in hPa. Humidity is omitted because the supplied export contains no humidity readings.

## Source and extraction
All rows are derived from `raw_source/uav_readings_original.csv`. A row is included in a sensor-specific file when at least one of that sensor's temperature or pressure fields is present. Original record ID, timestamp, epoch timestamp, status, sequence number, and power-source field are retained where available.

The `session_id` column is blank because the source export does not contain a reliable session identifier. Do not infer session boundaries from sequence resets alone.

## Analysis
`RQ1_summary.csv` reports descriptive statistics (sample count, mean, sample standard deviation, minimum, maximum). MAE and RMSE are intentionally blank because synchronized reference pairing and comparable environmental conditions have not been established. The three sensors may be located at different positions and altitudes.

Flight mode, altitude, and UAV speed are not present in the source file and are therefore not represented as measured fields.
