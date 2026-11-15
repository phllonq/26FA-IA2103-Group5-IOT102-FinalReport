# Experimental Datasets

This directory organizes the telemetry export supplied for the IOT102 UAV monitoring project.

## Dataset contents

- `RQ1_Sensing/`: sensor streams extracted from the supplied `uav_readings.csv`.
- `RQ2_Communication/`: schemas for communication experiments. The supplied readings export does not contain packet TX/RX/ACK event logs or an identifiable fixed-rate comparison run.
- `Metadata/`: configuration, field definitions, and collection/import notes.

## Evidence and limitations

The source export contains 910 records from 2026-11-12 through 2026-11-15:
- 554 records marked `online`.
- 356 records marked `offline`.
- BMP280 #1 (`t1`, `p1`): 459 records with measurements.
- BMP280 #2 (`t2`, `p2`): 145 records with measurements.
- BMP280 #3 (`t3`, `p3`): 476 records with measurements.
- Humidity (`h1`, `h2`, `h3`), battery (`bat`, `vbat`) have no recorded values.

The original source export is preserved at `raw_source/uav_readings_original.csv`.

**Important:** No values have been fabricated. Blank `session_id` fields mean the source export did not provide session identifiers. RQ1 summary contains descriptive statistics only. MAE/RMSE, flight-mode comparisons, and RQ2 performance metrics are not claimed where the required evidence is absent.
