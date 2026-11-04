"""Structured JSON logging helper for PlayRef."""

import json
import logging
import sys
import time
from contextlib import contextmanager
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formats log records as JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if attached
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id
        if hasattr(record, "stage"):
            log_obj["stage"] = record.stage
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if hasattr(record, "extra_data") and isinstance(record.extra_data, dict):
            log_obj.update(record.extra_data)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def get_logger(name: str = "playref") -> logging.Logger:
    """Get or configure structured JSON logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


logger = get_logger("playref")


@contextmanager
def log_stage(stage_name: str, request_id: Optional[str] = None, **kwargs):
    """Context manager to measure and log duration of pipeline stages."""
    start = time.perf_counter()
    logger.info(
        f"Starting stage: {stage_name}",
        extra={"stage": stage_name, "request_id": request_id, "extra_data": kwargs},
    )
    try:
        yield
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            f"Finished stage: {stage_name} in {duration_ms}ms",
            extra={
                "stage": stage_name,
                "duration_ms": duration_ms,
                "request_id": request_id,
                "extra_data": kwargs,
            },
        )
    except Exception as e:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.error(
            f"Failed stage: {stage_name} after {duration_ms}ms with error: {e}",
            exc_info=True,
            extra={
                "stage": stage_name,
                "duration_ms": duration_ms,
                "request_id": request_id,
                "extra_data": kwargs,
            },
        )
        raise

