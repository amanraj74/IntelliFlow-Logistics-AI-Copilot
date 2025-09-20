import pathway as pw
import os
import json
from datetime import datetime
import time


class LogisticsPipeline:
    """Real-time data processing pipeline for logistics data using Pathway."""
    
    def __init__(self, 
                 drivers_path: str = "data/streams/drivers",
                 incidents_path: str = "data/streams/incidents",
                 vehicles_path: str = "data/streams/vehicles",
                 invoices_path: str = "data/streams/invoices",
                 output_path: str = "data/output"):
        """Initialize the pipeline with data paths.
        
        Args:
            drivers_path: Path to drivers data directory
            incidents_path: Path to incidents data directory
            vehicles_path: Path to vehicles data directory
            invoices_path: Path to invoices data directory
            output_path: Path to output directory
        """
        self.drivers_path = drivers_path
        self.incidents_path = incidents_path
        self.vehicles_path = vehicles_path
        self.invoices_path = invoices_path
        self.output_path = output_path
        
        # Ensure output directories exist
        os.makedirs(os.path.join(output_path, "alerts"), exist_ok=True)
        os.makedirs(os.path.join(output_path, "driver_analytics"), exist_ok=True)
        os.makedirs(os.path.join(output_path, "processed_incidents"), exist_ok=True)
    
    def run(self):
        """Run the real-time data processing pipeline."""
        # Read data streams
        drivers = pw.io.csv.read(self.drivers_path, mode="streaming", infer_schema=True)
        incidents = pw.io.csv.read(self.incidents_path, mode="streaming", infer_schema=True)
        
        # Try to read vehicles data if available
        try:
            vehicles = pw.io.csv.read(self.vehicles_path, mode="streaming", infer_schema=True)
        except Exception:
            # Create empty table if no vehicles data
            vehicles = pw.Table.empty(schema=pw.schema_from_types(
                id=str, type=str, status=str
            ))
        
        # Try to read invoices data if available
        try:
            invoices = pw.io.csv.read(self.invoices_path, mode="streaming", infer_schema=True)
        except Exception:
            # Create empty table if no invoices data
            invoices = pw.Table.empty(schema=pw.schema_from_types(
                id=str, amount=float, due_date=str, status=str
            ))
        
        # Process driver data
        processed_drivers = self._process_drivers(drivers)
        
        # Process incident data
        processed_incidents = self._process_incidents(incidents)
        
        # Join drivers and incidents for risk analysis
        driver_risk = self._analyze_driver_risk(processed_drivers, processed_incidents)
        
        # Generate safety alerts
        safety_alerts = self._generate_safety_alerts(driver_risk, processed_incidents)
        
        # Generate compliance alerts if invoice data available
        if 'id' in invoices.schema:
            compliance_alerts = self._generate_compliance_alerts(invoices)
            
            # Combine all alerts
            all_alerts = pw.Table.concat_reindex(safety_alerts, compliance_alerts)
        else:
            all_alerts = safety_alerts
        
        # Write outputs
        pw.io.jsonlines.write(all_alerts, os.path.join(self.output_path, "alerts", "alerts_stream.jsonl"))
        pw.io.jsonlines.write(driver_risk, os.path.join(self.output_path, "driver_analytics", "driver_risk.jsonl"))
        pw.io.jsonlines.write(processed_incidents, os.path.join(self.output_path, "processed_incidents", "incidents.jsonl"))
        
        # Run the pipeline
        pw.run()
    
    def _process_drivers(self, drivers):
        """Process driver data."""
        @pw.udf
        def normalize_risk_score(score):
            """Ensure risk score is between 0 and 1."""
            try:
                score = float(score)
                return max(0.0, min(1.0, score))
            except (ValueError, TypeError):
                return 0.5
        
        return drivers.select(
            id=pw.this.id,
            name=pw.this.name,
            license_number=pw.this.license_number,
            risk_score=normalize_risk_score(pw.this.risk_score),
            timestamp=pw.this.timestamp if 'timestamp' in drivers.schema else pw.make_const(datetime.now().isoformat())
        )
    
    def _process_incidents(self, incidents):
        """Process incident data."""
        @pw.udf
        def severity_to_score(sev: str) -> float:
            """Convert severity string to numeric score."""
            return {"low": 0.1, "medium": 0.5, "high": 0.9}.get(str(sev).lower(), 0.3)
        
        @pw.udf
        def extract_incident_type(description: str) -> str:
            """Extract incident type from description."""
            keywords = {
                "speed": "speeding",
                "brake": "harsh_braking",
                "late": "late_delivery",
                "delay": "late_delivery",
                "aggress": "aggressive_driving",
                "deviat": "route_deviation",
                "violat": "violation",
                "accident": "accident",
                "crash": "accident"
            }
            
            description = description.lower()
            for key, incident_type in keywords.items():
                if key in description:
                    return incident_type
            
            return "other"
        
        return incidents.select(
            id=pw.this.id,
            driver_id=pw.this.driver_id,
            date=pw.this.date,
            severity=pw.this.severity,
            description=pw.this.description,
            location=pw.this.location,
            risk_score=severity_to_score(pw.this.severity),
            incident_type=extract_incident_type(pw.this.description),
            timestamp=pw.this.timestamp if 'timestamp' in incidents.schema else pw.make_const(datetime.now().isoformat())
        )
    
    def _analyze_driver_risk(self, drivers, incidents):
        """Analyze driver risk based on incidents."""
        # Count incidents by driver
        incident_counts = incidents.groupby(incidents.driver_id).reduce(
            incident_count=pw.reducers.count(),
            high_severity_count=pw.reducers.count(pw.this.severity == "high"),
            avg_risk_score=pw.reducers.avg(pw.this.risk_score)
        )
        
        # Join with drivers
        driver_risk = drivers.join(incident_counts, pw.left.id == pw.right.driver_id)
        
        @pw.udf
        def calculate_combined_risk(base_risk, incident_count, high_severity_count, avg_incident_risk):
            """Calculate combined risk score based on base risk and incidents."""
            # Default values for nulls
            incident_count = incident_count or 0
            high_severity_count = high_severity_count or 0
            avg_incident_risk = avg_incident_risk or 0.0
            base_risk = base_risk or 0.5
            
            # Incident factor increases with more incidents and high severity
            incident_factor = min(1.0, (incident_count * 0.1) + (high_severity_count * 0.3))
            
            # Combined risk is weighted average of base risk and incident risk
            combined_risk = (base_risk * 0.4) + (avg_incident_risk * 0.3) + (incident_factor * 0.3)
            
            # Ensure within bounds
            return max(0.0, min(1.0, combined_risk))
        
        return driver_risk.select(
            id=pw.this.id,
            name=pw.this.name,
            license_number=pw.this.license_number,
            base_risk_score=pw.this.risk_score,
            incident_count=pw.this.incident_count,
            high_severity_count=pw.this.high_severity_count,
            combined_risk_score=calculate_combined_risk(
                pw.this.risk_score, 
                pw.this.incident_count, 
                pw.this.high_severity_count, 
                pw.this.avg_risk_score
            ),
            timestamp=pw.this.timestamp
        )
    
    def _generate_safety_alerts(self, driver_risk, incidents):
        """Generate safety alerts based on driver risk and incidents."""
        # High-risk driver alerts
        high_risk_alerts = driver_risk.filter(pw.this.combined_risk_score >= 0.7).select(
            id=pw.apply(lambda x: f"A{int(time.time())}{x}", pw.this.id),
            type=pw.make_const("safety"),
            message=pw.apply(
                lambda name, score: f"Driver {name} risk score increased to {score:.2f}", 
                pw.this.name, pw.this.combined_risk_score
            ),
            priority=pw.make_const("high"),
            related_entity_id=pw.this.id,
            related_entity_type=pw.make_const("driver"),
            timestamp=pw.this.timestamp
        )
        
        # Recent high-severity incident alerts
        incident_alerts = incidents.filter(pw.this.severity == "high").select(
            id=pw.apply(lambda x: f"A{int(time.time())}{x}", pw.this.id),
            type=pw.make_const("safety"),
            message=pw.apply(
                lambda desc, loc: f"High severity incident: {desc} at {loc}", 
                pw.this.description, pw.this.location
            ),
            priority=pw.make_const("high"),
            related_entity_id=pw.this.driver_id,
            related_entity_type=pw.make_const("driver"),
            timestamp=pw.this.timestamp
        )
        
        # Combine alerts
        return pw.Table.concat_reindex(high_risk_alerts, incident_alerts)
    
    def _generate_compliance_alerts(self, invoices):
        """Generate compliance alerts based on invoice data."""
        @pw.udf
        def is_overdue(due_date, status):
            """Check if an invoice is overdue."""
            if status.lower() == "paid":
                return False
                
            try:
                due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                return due < datetime.now()
            except (ValueError, TypeError):
                return False
        
        # Overdue invoice alerts
        overdue_alerts = invoices.filter(is_overdue(pw.this.due_date, pw.this.status)).select(
            id=pw.apply(lambda x: f"A{int(time.time())}{x}", pw.this.id),
            type=pw.make_const("compliance"),
            message=pw.apply(
                lambda id, amount: f"Invoice {id} is overdue (Amount: ${amount:.2f})", 
                pw.this.id, pw.this.amount
            ),
            priority=pw.make_const("medium"),
            related_entity_id=pw.this.id,
            related_entity_type=pw.make_const("invoice"),
            timestamp=pw.make_const(datetime.now().isoformat())
        )
        
        return overdue_alerts


def run_pipeline():
    """Run the logistics pipeline."""
    pipeline = LogisticsPipeline()
    pipeline.run()


if __name__ == "__main__":
    run_pipeline()


