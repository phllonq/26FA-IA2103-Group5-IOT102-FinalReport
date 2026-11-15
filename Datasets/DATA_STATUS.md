# Data Status and Submission Note

This package is a traceable organization of the source data supplied for this project.

## Completed from supplied evidence
- Original gateway export preserved unchanged in `raw_source/`.
- Three BMP280 streams separated into RQ1 CSV files.
- Descriptive RQ1 statistics calculated from non-missing measurements.
- Metadata, field dictionary, and import log generated.

## Not completed because source evidence was not supplied
- Flight-mode labels (ground / hover / forward).
- Altitude and forward speed.
- Verified experimental session identifiers.
- Synchronized sensor-to-reference error analysis (MAE/RMSE).
- RSSI/state/interval logs for adaptive transmission.
- Fixed-rate comparison run.
- Packet-level TX/RX/ACK logs.
- Standard AoI calculation.

RQ2 CSV files are intentionally schema-only. They must not be presented as measured results. Synthetic or invented experimental values have not been inserted.
