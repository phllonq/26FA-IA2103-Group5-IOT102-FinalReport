# RQ2 – Communication Dataset

## Purpose
This directory defines the data schema for evaluating adaptive communication against fixed-rate transmission.

## Evidence currently available
The supplied `uav_readings.csv` contains gateway telemetry fields such as timestamp, status, sequence number, sensor readings, and power-source label. It does **not** contain explicit RF transmission (`TX`), reception (`RX`), acknowledgment (`ACK`), timeout, RSSI, transmission interval, or packet-generation timestamp events.

Consequently, the CSV files in this directory are schema-only files, not completed experimental datasets:
- `D1_adaptive.csv`: adaptive-mode observation schema.
- `D2_fixed_rate.csv`: fixed-rate comparison schema.
- `D3_packet_log.csv`: packet event schema.
- `RQ2_summary.csv`: metric summary schema.

No synthetic records or claimed RQ2 results have been inserted.

## Metric requirements
- PDR requires transmitted packet counts and unique received packet counts for the same session.
- Packet reduction requires comparable fixed-rate and adaptive runs.
- Latency requires corresponding transmit and receive timestamps with a known clock relationship.
- Standard AoI requires packet generation timestamps and reception timestamps.
- ACK success rate requires ACK transmission/reception evidence and a defined denominator.

Under the standard definition, PDR is between 0% and 100%. Duplicate receptions must not be counted as unique delivered packets.
