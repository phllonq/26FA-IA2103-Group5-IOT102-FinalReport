# Dataset Dictionary

## 1. Common fields

| Field | Type | Unit | Meaning |
|---|---|---|---|
| `id` | Integer | - | Original gateway database/export record identifier |
| `timestamp` | String | ISO 8601 | Original timestamp from source field `ts` |
| `ts_epoch` | Numeric | Unix seconds | Original epoch timestamp |
| `session_id` | String | - | Experimental session identifier; blank when not supplied by source |
| `status` | String | - | Original gateway status (`online` / `offline`) |
| `seq` | Numeric/integer-like | - | Original sequence value; resets may occur |
| `pwr` | String | - | Original power-source label |

## 2. RQ1 sensor fields

| Field | Type | Unit | Meaning |
|---|---|---|---|
| `temperature_c` | Numeric | °C | Temperature from the sensor identified by the file |
| `pressure_hpa` | Numeric | hPa | Pressure from the sensor identified by the file |

### Sensor-to-file mapping

| File | Original source fields | Sensor |
|---|---|---|
| `RQ1_S1_baseline.csv` | `t1`, `p1` | BMP280 #1, unshielded |
| `RQ1_S2_shielded.csv` | `t2`, `p2` | BMP280 #2, Pagoda Shield |
| `RQ1_S3_ground_reference.csv` | `t3`, `p3` | BMP280 #3, ground reference |

## 3. RQ1 summary fields

| Field | Meaning |
|---|---|
| `sensor_id` | Sensor identifier |
| `measurement` | `temperature_c` or `pressure_hpa` |
| `sample_count` | Number of non-missing observations |
| `mean_value` | Arithmetic mean |
| `std_dev_sample` | Sample standard deviation (ddof=1) |
| `min_value` | Minimum observed value |
| `max_value` | Maximum observed value |
| `mae` | Mean absolute error; blank when not validly calculated |
| `rmse` | Root mean square error; blank when not validly calculated |
| `comparison_status` | Status of comparison calculation |
| `notes` | Interpretation and limitations |

## 4. RQ2 schema fields

| Field | Meaning |
|---|---|
| `event` | Packet event such as TX, RX, ACK, TIMEOUT, DUPLICATE |
| `direction` | Packet direction, e.g. UAV_TO_GROUND or GROUND_TO_UAV |
| `rssi_dbm` | Received signal strength in dBm |
| `state` | Adaptive state, if recorded by firmware |
| `tx_interval_s` | Configured transmission interval in seconds |
| `tx_count` | Number of transmitted packets |
| `rx_unique_count` | Number of unique received packets |
| `duplicate_count` | Number of duplicate receptions |
| `lost_count` | Number of transmitted packets not received |
| `packet_size_bytes` | Packet size in bytes |
| `latency_ms` | Measured latency in milliseconds |
| `generation_timestamp` | Time when telemetry data was generated |
| `average_aoi_ms` | Average Age of Information in milliseconds |

The RQ2 CSV files are schema-only until real packet-event logs and comparison runs are supplied.

## 5. Missing values and interpretation

- Empty CSV fields represent missing or unavailable values.
- Zero must not be used as a substitute for missing data.
- Sequence numbers must be interpreted within a validated session.
- Rows marked offline may still contain stored sensor readings; retain the original `status` field.
- Do not calculate PDR from sequence numbers alone when transmission counts, session boundaries, and duplicate handling are unknown.
- Standard PDR = unique successfully received packets / transmitted packets × 100.
- Standard AoI requires generation timestamps and reception timestamps.
