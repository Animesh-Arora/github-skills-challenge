import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from anomaly_detector import AnomalyDetector
from aiops_pipeline import run_pipeline
from event_consumer import EventConsumer
from event_producer import EventProducer
from event_topic import EventTopic


def test_normal_record_is_not_anomaly():
    detector = AnomalyDetector()

    record = {
        "timestamp": "2026-09-20T10:00:00",
        "service": "payment-service",
        "response_time_ms": 120,
        "cpu_percent": 42,
        "memory_percent": 51,
        "log_level": "INFO",
        "message": "Payment request processed successfully"
    }

    assert detector.detect(record) is None


def test_anomalous_record_is_detected():
    detector = AnomalyDetector()

    record = {
        "timestamp": "2026-09-20T10:05:00",
        "service": "payment-service",
        "response_time_ms": 610,
        "cpu_percent": 75,
        "memory_percent": 70,
        "log_level": "ERROR",
        "message": "Payment service timeout"
    }

    event = detector.detect(record)

    assert event is not None
    assert event["type"] == "ANOMALY"


def test_producer_publishes_event():
    topic = EventTopic("anomaly-events")
    producer = EventProducer(topic)

    event = {
        "type": "ANOMALY",
        "service": "payment-service"
    }

    assert producer.publish(event)
    assert len(topic.get_messages()) == 1


def test_consumer_receives_event():
    topic = EventTopic("anomaly-events")
    producer = EventProducer(topic)
    consumer = EventConsumer(topic)

    event = {
        "type": "ANOMALY",
        "service": "payment-service"
    }

    producer.publish(event)

    messages = consumer.consume()

    assert len(messages) == 1


def test_run_pipeline_integration():
    """Test the full pipeline end-to-end."""
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'service_data.json')
    result = run_pipeline(data_path)

    assert result["records_processed"] == 10
    assert len(result["anomalies_detected"]) >= 1
    assert len(result["events_consumed"]) == len(result["anomalies_detected"])


def test_producer_rejects_empty_event():
    """Test that producer returns False for empty/None event."""
    topic = EventTopic("anomaly-events")
    producer = EventProducer(topic)

    assert producer.publish(None) is False
    assert producer.publish({}) is False
    assert len(topic.get_messages()) == 0


def test_topic_clear():
    """Test that topic clear removes all messages."""
    topic = EventTopic("anomaly-events")
    topic.publish({"type": "ANOMALY"})

    assert len(topic.get_messages()) == 1
    topic.clear()
    assert len(topic.get_messages()) == 0


def test_high_cpu_detected():
    """Test that high CPU triggers anomaly."""
    detector = AnomalyDetector()
    record = {
        "timestamp": "2026-09-20T10:00:00",
        "service": "api-service",
        "response_time_ms": 100,
        "cpu_percent": 95,
        "memory_percent": 50,
        "log_level": "INFO",
        "message": "OK"
    }
    event = detector.detect(record)

    assert event is not None
    assert "High CPU utilization" in event["reasons"]


def test_high_memory_detected():
    """Test that high memory triggers anomaly."""
    detector = AnomalyDetector()
    record = {
        "timestamp": "2026-09-20T10:00:00",
        "service": "api-service",
        "response_time_ms": 100,
        "cpu_percent": 50,
        "memory_percent": 95,
        "log_level": "INFO",
        "message": "OK"
    }
    event = detector.detect(record)

    assert event is not None
    assert "High memory utilization" in event["reasons"]