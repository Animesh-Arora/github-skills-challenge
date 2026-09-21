# AIOps Anomaly Detection Pipeline

A lightweight Python-based AIOps pipeline that demonstrates **service monitoring, anomaly detection, event-driven processing, automated testing, code coverage, and Continuous Integration using GitHub Actions**.

This repository was developed as part of a GitHub Actions testing exercise and extended with a simple AIOps simulation.

---

## 1. AIOps Scenario

### Service Being Monitored

The **payment-service** is a simulated application service that processes payment requests. It produces operational telemetry at one-minute intervals including response times, CPU usage, memory usage, and application logs.

### Operational Problem Being Addressed

The operations team needs to detect when the payment-service exhibits unusual behaviour — such as response-time spikes, resource exhaustion, or application errors — and automatically surface these issues so they can be triaged. Manually reviewing logs and dashboards does not scale; an automated pipeline is needed.

### Purpose of AIOps in This Assessment

AIOps (Artificial Intelligence for IT Operations) automates the detection, correlation, and surfacing of operational issues. In this assessment the AIOps pipeline:

1. Ingests synthetic service telemetry (metrics + logs).
2. Applies threshold-based anomaly detection to identify abnormal observations.
3. Generates structured anomaly events.
4. Passes those events through a simulated event-streaming system (Producer → Topic → Consumer).
5. Outputs a final report of detected operational issues.

This demonstrates the core AIOps workflow: **Operational Data → Anomaly Detection → Event Generation → Producer → Topic → Consumer → AIOps Output**.

---

## 2. Operational Data Description

The operational data is stored in [`data/service_data.json`](data/service_data.json). It contains **10 telemetry records** captured from the `payment-service` at one-minute intervals on 20 September 2026 (10:00 – 10:09).

### Fields

| Field | Type | Category | Description |
|---|---|---|---|
| `timestamp` | ISO 8601 string | Metadata | When the observation was recorded (1-minute intervals) |
| `service` | string | Metadata | Name of the service (`payment-service`) |
| `response_time_ms` | integer | **Metric** | HTTP response time in milliseconds |
| `cpu_percent` | integer | **Metric** | CPU utilisation as a percentage |
| `memory_percent` | integer | **Metric** | Memory utilisation as a percentage |
| `log_level` | string | **Log** | Severity level (`INFO` or `ERROR`) |
| `message` | string | **Log** | Human-readable log message |

### Timestamps

Timestamps follow ISO 8601 format (`YYYY-MM-DDTHH:MM:SS`) and are spaced exactly one minute apart. They allow the telemetry to be ordered chronologically and enable correlation of metric spikes with log events at the same point in time.

---

## 3. Log and Metric Observations

### Normal Behaviour (Records 1–5 and 8–10)

| Timestamp | Response Time (ms) | CPU % | Memory % | Log Level | Message |
|---|---|---|---|---|---|
| 10:00:00 | 120 | 42 | 51 | INFO | Payment request processed successfully |
| 10:01:00 | 135 | 45 | 53 | INFO | Payment request processed successfully |
| 10:02:00 | 128 | 44 | 52 | INFO | Payment request processed successfully |
| 10:03:00 | 142 | 48 | 55 | INFO | Payment request processed successfully |
| 10:04:00 | 130 | 46 | 54 | INFO | Payment request processed successfully |
| 10:07:00 | 150 | 49 | 56 | INFO | Payment request processed successfully |
| 10:08:00 | 138 | 47 | 55 | INFO | Payment request processed successfully |
| 10:09:00 | 145 | 50 | 57 | INFO | Payment request processed successfully |

**Observations:**
- Response times are low (120–150 ms), well below the 500 ms threshold.
- CPU usage is moderate (42–50%), well below 80%.
- Memory usage is moderate (51–57%), well below 80%.
- All log levels are `INFO` with successful processing messages.
- These records represent the healthy steady-state of the service.

### Unusual Behaviour (Records 6 and 7)

| Timestamp | Response Time (ms) | CPU % | Memory % | Log Level | Message |
|---|---|---|---|---|---|
| 10:05:00 | **610** | 75 | 70 | **ERROR** | Payment service timeout |
| 10:06:00 | **640** | **94** | **91** | **ERROR** | Database connection timeout |

**Observations:**
- **Record 6 (10:05:00):** Response time spikes to 610 ms (exceeds the 500 ms threshold). CPU and memory are elevated but still within thresholds. The log level changes to `ERROR` with a "Payment service timeout" message.
- **Record 7 (10:06:00):** Response time remains high at 640 ms. CPU surges to 94% (exceeds 80%) and memory to 91% (exceeds 80%). The error message indicates a "Database connection timeout", suggesting a downstream dependency failure.
- The two anomalous records occur consecutively, suggesting a cascading failure: an initial service timeout escalates into full resource exhaustion and database connectivity loss.
- The service recovers by 10:07:00 (record 8), returning to normal metrics and `INFO` logging.

---

## 4. Anomaly Detection Findings

### Detection Mechanism

The `AnomalyDetector` class in [`src/anomaly_detector.py`](src/anomaly_detector.py) uses configurable thresholds:

| Metric | Threshold | Condition |
|---|---|---|
| Response Time | 500 ms | Flagged if `response_time_ms > 500` |
| CPU Usage | 80% | Flagged if `cpu_percent > 80` |
| Memory Usage | 80% | Flagged if `memory_percent > 80` |
| Log Level | `ERROR` | Flagged if `log_level == "ERROR"` |

When any combination of thresholds is exceeded, an anomaly event is generated with the list of reasons.

### Detected Anomalies

**Anomaly 1 — 2026-09-20T10:05:00 (payment-service)**

| Check | Value | Threshold | Triggered? |
|---|---|---|---|
| Response Time | 610 ms | > 500 ms | ✅ Yes |
| CPU | 75% | > 80% | ❌ No |
| Memory | 70% | > 80% | ❌ No |
| Log Level | ERROR | == ERROR | ✅ Yes |

Reasons: `High response time`, `Error log detected`

**Anomaly 2 — 2026-09-20T10:06:00 (payment-service)**

| Check | Value | Threshold | Triggered? |
|---|---|---|---|
| Response Time | 640 ms | > 500 ms | ✅ Yes |
| CPU | 94% | > 80% | ✅ Yes |
| Memory | 91% | > 80% | ✅ Yes |
| Log Level | ERROR | == ERROR | ✅ Yes |

Reasons: `High response time`, `High CPU utilization`, `High memory utilization`, `Error log detected`

### Analysis

- **No expected anomaly was missed.** Both records with unusual behaviour (10:05 and 10:06) were correctly flagged.
- **No normal event was incorrectly flagged.** All eight normal records returned `None` from the detector.
- The detector correctly identified the escalation pattern: the first anomaly has 2 reasons, the second has 4, reflecting the worsening condition.

### Limitation and Possible Improvement

**Limitation:** The threshold-based approach uses static, hardcoded limits. It cannot adapt to services with different baseline characteristics (e.g., a service whose normal response time is 450 ms would nearly always trigger). It also cannot detect gradual degradation trends — a slow upward drift in response times that stays below 500 ms would go unnoticed.

**Possible Improvement:** Implement **statistical anomaly detection** (e.g., z-score or moving-average-based detection) that learns each service's baseline dynamically. This would catch gradual degradation and reduce false positives for services with naturally higher baselines.

---

## 5. Event-Processing Flow

The pipeline simulates an event-streaming architecture with four core components:

```text
Operational Data (service_data.json)
        |
        v
+--------------------+
| Anomaly Detector   |  Analyses each telemetry record against thresholds.
+--------------------+  Returns an anomaly event dict or None.
        |
        | anomaly event (dict with type, service, timestamp, reasons, source)
        v
+--------------------+
| Event Producer     |  Validates the event (rejects None/empty) and
+--------------------+  publishes it to the topic.
        |
        v
+--------------------+
| Event Topic        |  In-memory list simulating a message broker topic.
+--------------------+  Stores published events in order.
        |
        v
+--------------------+
| Event Consumer     |  Reads all messages from the topic.
+--------------------+  Returns them for downstream processing.
        |
        v
+--------------------+
| AIOps Output       |  Prints the final detection report.
+--------------------+
```

### Component Roles

| Component | File | Role |
|---|---|---|
| **Producer** | `src/event_producer.py` | Accepts anomaly events and publishes them to a topic. Acts as the entry point into the event-streaming system. |
| **Topic** | `src/event_topic.py` | An in-memory message queue that decouples producer from consumer. Stores events until they are consumed. |
| **Consumer** | `src/event_consumer.py` | Reads events from the topic. Represents the downstream system that acts on detected anomalies. |
| **Event/Message** | Python dict | A structured anomaly record containing `type`, `service`, `timestamp`, `reasons`, and `source` fields. |

---

## 6. Final Workflow Execution Result

```text
==================================================
AIOps Pipeline Result
==================================================
Records processed: 10
Anomalies detected: 2
Events consumed: 2

Detected Events:

Service: payment-service
Timestamp: 2026-09-20T10:05:00
Type: ANOMALY
Reasons: High response time, Error log detected

Service: payment-service
Timestamp: 2026-09-20T10:06:00
Type: ANOMALY
Reasons: High response time, High CPU utilization, High memory utilization, Error log detected
```

**Verification:**

1. ✅ **Operational data processed** — all 10 records read from `data/service_data.json`.
2. ✅ **Anomalous behaviour detected** — 2 out of 10 records flagged.
3. ✅ **Anomaly events generated** — structured event dicts created with reasons.
4. ✅ **Events published** — producer sent 2 events to the `anomaly-events` topic.
5. ✅ **Events consumed** — consumer retrieved 2 events from the topic.
6. ✅ **Events processed successfully** — all event fields (service, timestamp, type, reasons) printed.
7. ✅ **Final output represents the detected operational issues** — response-time spikes, resource exhaustion, and error logs are clearly surfaced.

---

## 7. Issues Identified and Corrected

### Issue 1: Incorrect Fibonacci Assertion in Tests

- **Component:** `tests/calculations_test.py`
- **Cause:** The test for `get_nth_fibonacci(10)` asserted an incorrect expected value. The 10th Fibonacci number is 55, but the test expected a different value.
- **Correction:** Updated the assertion to `assert result == 55`.
- **Verification:** Test passes after correction.

### Issue 2: Missing Negative-Input Tests for Calculations

- **Component:** `tests/calculations_test.py`
- **Cause:** The `area_of_circle` and `get_nth_fibonacci` functions include `ValueError` guards for negative input, but there were no tests validating this behaviour. This left a coverage gap and meant the defensive logic was untested.
- **Correction:** Added `test_get_nth_fibonacci_negative` and `test_area_of_circle_negative_radius` tests.
- **Verification:** Both tests pass; coverage for `calculations.py` reaches 100%.

### Issue 3: Missing AIOps Pipeline Tests

- **Component:** `tests/test_aiops_pipeline.py`
- **Cause:** The test file lacked comprehensive tests for the anomaly detection and event-streaming pipeline components, resulting in low coverage.
- **Correction:** Added tests for:
  - Normal record detection (`test_normal_record_is_not_anomaly`)
  - Anomalous record detection (`test_anomalous_record_is_detected`)
  - Producer publishing (`test_producer_publishes_event`)
  - Consumer receiving (`test_consumer_receives_event`)
  - Full end-to-end pipeline integration (`test_run_pipeline_integration`)
  - Producer rejecting empty events (`test_producer_rejects_empty_event`)
  - Topic clearing (`test_topic_clear`)
  - High CPU detection (`test_high_cpu_detected`)
  - High memory detection (`test_high_memory_detected`)
- **Verification:** All 16 tests pass with 100% code coverage across all source files.

### Issue 4: Coverage Configuration

- **Component:** `.coveragerc`
- **Cause:** The coverage configuration needed updating to properly cover the `src` directory and exclude test files.
- **Correction:** Updated `.coveragerc` with correct source paths and omit patterns.
- **Verification:** `pytest --cov=src --cov-report=term-missing` reports 100% coverage.

---

## 8. Test and Validation Results

```text
============================= test session starts =============================
collected 16 items

tests/calculations_test.py::test_area_of_circle_positive_radius     PASSED [  6%]
tests/calculations_test.py::test_area_of_circle_zero_radius         PASSED [ 12%]
tests/calculations_test.py::test_get_nth_fibonacci_zero              PASSED [ 18%]
tests/calculations_test.py::test_get_nth_fibonacci_one               PASSED [ 25%]
tests/calculations_test.py::test_get_nth_fibonacci_ten               PASSED [ 31%]
tests/calculations_test.py::test_get_nth_fibonacci_negative          PASSED [ 37%]
tests/calculations_test.py::test_area_of_circle_negative_radius     PASSED [ 43%]
tests/test_aiops_pipeline.py::test_normal_record_is_not_anomaly     PASSED [ 50%]
tests/test_aiops_pipeline.py::test_anomalous_record_is_detected     PASSED [ 56%]
tests/test_aiops_pipeline.py::test_producer_publishes_event         PASSED [ 62%]
tests/test_aiops_pipeline.py::test_consumer_receives_event          PASSED [ 68%]
tests/test_aiops_pipeline.py::test_run_pipeline_integration         PASSED [ 75%]
tests/test_aiops_pipeline.py::test_producer_rejects_empty_event     PASSED [ 81%]
tests/test_aiops_pipeline.py::test_topic_clear                      PASSED [ 87%]
tests/test_aiops_pipeline.py::test_high_cpu_detected                PASSED [ 93%]
tests/test_aiops_pipeline.py::test_high_memory_detected             PASSED [100%]

============================= 16 passed in 0.08s ==============================
```

### Code Coverage

```text
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
src/aiops_pipeline.py        22      0   100%
src/anomaly_detector.py      18      0   100%
src/calculations.py          16      0   100%
src/event_consumer.py         6      0   100%
src/event_producer.py         9      0   100%
src/event_topic.py           10      0   100%
-------------------------------------------------------
TOTAL                        81      0   100%
```

---

## 9. Steps to Reproduce

### Prerequisites

- Python 3.10+
- Git

### Setup

```bash
git clone https://github.com/Animesh-Arora/github-skills-challenge.git
cd github-skills-challenge

python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
pip install pytest coverage pytest-cov
```

### Run the AIOps Pipeline

```bash
python src/aiops_pipeline.py
```

Expected output: 10 records processed, 2 anomalies detected, 2 events consumed with detailed event information.

### Run Tests

```bash
pytest --verbose
```

Expected: 16 tests pass.

### Run Coverage Report

```bash
pytest --cov=src --cov-report=term-missing --verbose
```

Expected: 100% coverage across all source files.

---

## Architecture

```text
Service Telemetry
       |
       v
+------------------+
| Anomaly Detector |
+------------------+
       |
       | anomaly detected
       v
+------------------+
|  Event Producer  |
+------------------+
       |
       v
+------------------+
|   Event Topic    |
+------------------+
       |
       v
+------------------+
|  Event Consumer  |
+------------------+
```

## Project Structure

```text
github-skills-challenge/
│
├── data/
│   └── service_data.json
│
├── src/
│   ├── aiops_pipeline.py
│   ├── anomaly_detector.py
│   ├── calculations.py
│   ├── event_consumer.py
│   ├── event_producer.py
│   └── event_topic.py
│
├── tests/
│   ├── calculations_test.py
│   └── test_aiops_pipeline.py
│
├── .github/
│   └── workflows/
│       ├── python-package.yml
│       └── python-coverage.yml
│
├── .coveragerc
├── requirements.txt
└── README.md
```

## Technologies Used

* Python
* Pytest
* Coverage.py
* pytest-cov
* GitHub Actions
* JSON

## License

This project is licensed under the MIT License.

## Author

**Animesh Arora**

GitHub: [Animesh-Arora](https://github.com/Animesh-Arora)
