from typing import List, Optional
from pydantic import BaseModel
import pathway as pw
from datetime import datetime

class Driver(BaseModel):
    id: str
    name: str
    license_number: str
    risk_score: float = 0.0

class Incident(BaseModel):
    id: str
    driver_id: str
    date: str
    severity: str
    description: str
    location: Optional[str] = None

def process_driver_stream(stream_dir: str = "data/streams/drivers") -> pw.Table:
    """Process driver data stream using Pathway."""
    return (
        pw.io.fs.read(
            stream_dir,
            format="csv",
            mode="streaming",
            schema={"id": str, "name": str, "license_number": str, "risk_score": float}
        )
        .select(
            pw.this.id,
            pw.this.name,
            pw.this.license_number,
            risk_score=pw.cast(float, pw.this.risk_score)
        )
    )

def process_incidents_stream(stream_dir: str = "data/streams/incidents") -> pw.Table:
    """Process incident data stream using Pathway."""
    return (
        pw.io.fs.read(
            stream_dir,
            format="csv",
            mode="streaming",
            schema={
                "id": str,
                "driver_id": str,
                "date": str,
                "severity": str,
                "description": str,
                "location": str
            }
        )
        .select(
            pw.this.id,
            pw.this.driver_id,
            pw.this.severity,
            pw.this.description,
            date=pw.this.date,
            location=pw.this.location
        )
    )

def calculate_risk_scores(drivers: pw.Table, incidents: pw.Table) -> pw.Table:
    """Calculate real-time risk scores for drivers based on incidents."""
    incident_counts = (
        incidents
        .groupby(pw.this.driver_id)
        .reduce(
            driver_id=pw.this.driver_id,
            incident_count=pw.reducers.count(),
            severity_score=pw.reducers.sum(
                pw.case(
                    {
                        "high": 1.0,
                        "medium": 0.5,
                        "low": 0.2
                    },
                    pw.this.severity
                )
            )
        )
    )

    return (
        drivers
        .join(incident_counts, pw.left.id == pw.right.driver_id)
        .select(
            pw.this.id,
            pw.this.name,
            pw.this.license_number,
            risk_score=(
                pw.coalesce(pw.this.severity_score, 0) * 0.7 +
                pw.coalesce(pw.this.incident_count, 0) * 0.3
            )
        )
    )

def generate_alerts(risk_scores: pw.Table, threshold: float = 0.7) -> pw.Table:
    """Generate real-time alerts for high-risk drivers."""
    return (
        risk_scores
        .filter(pw.this.risk_score >= threshold)
        .select(
            id=pw.uuid4(),
            driver_id=pw.this.id,
            message=pw.concat(
                "High risk alert for driver ",
                pw.this.name,
                " (Risk score: ",
                pw.cast(str, pw.this.risk_score),
                ")"
            ),
            timestamp=pw.cast(str, datetime.now()),
            severity="high"
        )
    )