# AIOps Anomaly Detection Pipeline

A lightweight Python-based AIOps pipeline that demonstrates **service monitoring, anomaly detection, event-driven processing, automated testing, code coverage, and Continuous Integration using GitHub Actions**.

This repository was developed as part of a GitHub Actions testing exercise and extended with a simple AIOps simulation.

## Overview

Modern applications generate large amounts of telemetry such as response times, CPU usage, memory usage, and logs.

This project simulates a basic AIOps workflow that:

1. Reads service telemetry from a JSON file.
2. Detects abnormal service behaviour.
3. Generates anomaly events.
4. Publishes events to an in-memory event topic.
5. Allows a consumer to receive the generated events.
6. Uses automated tests to verify the system.
7. Uses GitHub Actions for Continuous Integration and code coverage.

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

## Anomaly Detection

The `AnomalyDetector` analyses service telemetry using configurable thresholds.

The default thresholds include:

```text
Response Time : 500 ms
CPU Usage     : 80%
Memory Usage  : 80%
```

When a telemetry record exceeds one or more thresholds, an anomaly event is generated containing information about the affected service and the reason for the anomaly.

Example:

```json
{
  "type": "ANOMALY",
  "service": "payment-service",
  "reasons": [
    "High response time"
  ]
}
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

## Components

### Anomaly Detector

`src/anomaly_detector.py`

Analyses telemetry records and generates anomaly events when configured thresholds are exceeded.

### Event Topic

`src/event_topic.py`

Provides a simple in-memory simulation of an event-streaming topic.

### Event Producer

`src/event_producer.py`

Publishes detected anomaly events to an event topic.

### Event Consumer

`src/event_consumer.py`

Consumes events available in the event topic.

### AIOps Pipeline

`src/aiops_pipeline.py`

Connects the different components together and processes telemetry stored in:

```text
data/service_data.json
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Animesh-Arora/github-skills-challenge.git
cd github-skills-challenge
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
pip install pytest coverage pytest-cov
```

## Running the AIOps Pipeline

Run:

```bash
python src/aiops_pipeline.py
```

The program processes the telemetry dataset and displays information such as:

```text
Records processed
Anomalies detected
Events consumed
```

It also prints details of the detected anomaly events.

## Running Tests

Run all tests using:

```bash
pytest --verbose
```

Tests cover functionality including:

* Circle area calculations
* Fibonacci calculations
* Anomaly detection
* Event publishing
* Event consumption

## Code Coverage

Coverage can be generated using:

```bash
pytest --cov=src --verbose
```

A detailed terminal coverage report can also be generated using:

```bash
pytest --cov=src --cov-report=term-missing
```

The CI pipeline is configured to enforce a minimum code coverage requirement.

## Continuous Integration

GitHub Actions is used to automatically execute tests when changes are proposed through pull requests.

The project contains workflows for:

### Python Testing

The Python package workflow:

* Checks out the repository
* Configures Python
* Installs dependencies
* Runs linting
* Executes the Pytest test suite

### Coverage Testing

The coverage workflow:

* Runs tests using `pytest`
* Measures coverage of the `src` directory
* Generates a coverage report
* Posts coverage information on the pull request
* Enforces the configured minimum coverage threshold

This helps prevent untested or broken code from being merged into the main branch.

## Technologies Used

* Python
* Pytest
* Coverage.py
* pytest-cov
* GitHub Actions
* GitHub Codespaces
* JSON

## Concepts Demonstrated

This project demonstrates several software engineering and DevOps concepts:

* Continuous Integration
* Automated Unit Testing
* Code Coverage
* GitHub Actions
* Pull Request Validation
* Event-Driven Architecture
* Producer-Consumer Pattern
* Basic AIOps
* Telemetry Monitoring
* Anomaly Detection
* Branch Protection

## Future Improvements

The current implementation is intentionally lightweight and uses an in-memory event-streaming simulation.

It can be extended with:

* Apache Kafka or another real message broker
* Machine-learning-based anomaly detection
* Real-time telemetry ingestion
* Persistent event storage
* Alerting and notifications
* Monitoring dashboards
* Containerisation using Docker
* Deployment to a cloud environment

## License

This project is licensed under the MIT License.

## Author

**Animesh Arora**

GitHub: [Animesh-Arora](https://github.com/Animesh-Arora)
