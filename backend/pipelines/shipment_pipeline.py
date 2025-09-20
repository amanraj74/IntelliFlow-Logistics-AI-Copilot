import os
import json
import time
import logging
from datetime import datetime
import pandas as pd
import pathway as pw
from pathway.stdlib.ml.index import KNNIndex
from pathway.stdlib.utils.col import unpack_col

# Import our anomaly detector
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analytics.shipment_anomaly_detector import analyze_shipment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ShipmentPipeline:
    """Real-time shipment data processing pipeline using Pathway."""

    def __init__(self, input_dir, output_dir, historical_data_path=None):
        """Initialize the shipment pipeline.

        Args:
            input_dir: Directory to monitor for new shipment data files
            output_dir: Directory to write processed shipment data
            historical_data_path: Path to historical shipment data (optional)
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.historical_data_path = historical_data_path
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize Pathway pipeline
        self.pw_context = None
        self.shipment_table = None
        self.anomaly_table = None
        self.alert_table = None

    def build_pipeline(self):
        """Build the Pathway data processing pipeline."""
        # Create a Pathway context
        self.pw_context = pw.io.python.run_all()

        # Define the input connector to monitor the directory for new files
        self.shipment_table = pw.io.fs.read(
            self.input_dir,
            format="json",
            mode="streaming",  # Use streaming mode to continuously monitor for new files
            with_metadata=True,
        )

        # Process shipments to detect anomalies
        self.anomaly_table = self.shipment_table.select(
            pw.this.data,
            pw.this._pw_path_name,
            pw.this._pw_row_id,
            processed=pw.apply_async(
                self._process_shipment,
                pw.this.data,
                self.historical_data_path
            )
        )

        # Extract anomalies for alerting
        self.alert_table = self.anomaly_table.select(
            shipment_id=pw.apply(lambda x: x.get("id") if isinstance(x, dict) else None, pw.this.processed),
            anomalies=pw.apply(lambda x: x.get("anomalies", []) if isinstance(x, dict) else [], pw.this.processed),
            has_high_severity=pw.apply(lambda x: x.get("has_high_severity_anomalies", False) if isinstance(x, dict) else False, pw.this.processed),
            timestamp=pw.apply(lambda: datetime.now().isoformat()),
            file_path=pw.this._pw_path_name,
        ).filter(pw.apply(lambda anomalies: len(anomalies) > 0, pw.this.anomalies))

        # Write processed shipments to output directory
        pw.io.fs.write(
            self.anomaly_table.select(
                data=pw.this.processed,
                path=pw.apply(self._get_output_path, pw.this._pw_path_name)
            ),
            self.output_dir,
            format="json",
            filename_pattern="{path}",
        )

        # Write alerts to a separate file for real-time monitoring
        pw.io.fs.write(
            self.alert_table,
            os.path.join(self.output_dir, "alerts"),
            format="json",
            filename_pattern="alert_{timestamp}.json",
        )

        # Optional: Create a vector index for similarity search
        if self._should_create_vector_index():
            self._create_vector_index()

        return self

    def _process_shipment(self, shipment_data, historical_data_path):
        """Process a shipment to detect anomalies.

        Args:
            shipment_data: Shipment data dictionary
            historical_data_path: Path to historical shipment data

        Returns:
            Processed shipment data with detected anomalies
        """
        try:
            # Use our anomaly detector to analyze the shipment
            result = analyze_shipment(shipment_data, historical_data_path)
            return result
        except Exception as e:
            logger.error(f"Error processing shipment: {e}")
            # Return original data with error flag
            if isinstance(shipment_data, dict):
                shipment_data["processing_error"] = str(e)
            return shipment_data

    def _get_output_path(self, input_path):
        """Generate output path based on input path.

        Args:
            input_path: Input file path

        Returns:
            Output file path
        """
        # Extract filename from path and use it for output
        filename = os.path.basename(input_path)
        return filename

    def _should_create_vector_index(self):
        """Determine if vector index should be created.

        Returns:
            Boolean indicating whether to create vector index
        """
        # For demo purposes, always create index
        # In production, this could be configurable
        return True

    def _create_vector_index(self):
        """Create a vector index for similarity search on shipments."""
        try:
            # Extract features for indexing
            shipment_features = self.anomaly_table.select(
                id=pw.apply(lambda x: x.get("id") if isinstance(x, dict) else "unknown", pw.this.processed),
                origin=pw.apply(lambda x: self._extract_location_features(x.get("origin", {})) if isinstance(x, dict) else [0, 0], pw.this.processed),
                destination=pw.apply(lambda x: self._extract_location_features(x.get("destination", {})) if isinstance(x, dict) else [0, 0], pw.this.processed),
                cargo_type=pw.apply(lambda x: x.get("cargo", {}).get("type", "unknown") if isinstance(x, dict) else "unknown", pw.this.processed),
                cargo_value=pw.apply(lambda x: float(x.get("cargo", {}).get("value", 0)) if isinstance(x, dict) else 0, pw.this.processed),
                anomaly_count=pw.apply(lambda x: len(x.get("anomalies", [])) if isinstance(x, dict) else 0, pw.this.processed),
                has_high_severity=pw.apply(lambda x: x.get("has_high_severity_anomalies", False) if isinstance(x, dict) else False, pw.this.processed),
            )

            # Unpack location features
            with_features = unpack_col(shipment_features, "origin", ["origin_lat", "origin_lon"])
            with_features = unpack_col(with_features, "destination", ["dest_lat", "dest_lon"])

            # Create embeddings (simplified for demo)
            embeddings = with_features.select(
                pw.this.id,
                vector=pw.apply(
                    lambda lat1, lon1, lat2, lon2, value, anomaly_count, has_high: [
                        float(lat1), float(lon1), float(lat2), float(lon2), 
                        float(value) / 10000.0,  # Normalize value
                        float(anomaly_count),
                        1.0 if has_high else 0.0
                    ],
                    pw.this.origin_lat, pw.this.origin_lon,
                    pw.this.dest_lat, pw.this.dest_lon,
                    pw.this.cargo_value, pw.this.anomaly_count,
                    pw.this.has_high_severity
                )
            )

            # Create KNN index
            index = KNNIndex(embeddings.vector)
            
            # Store index reference for querying
            self.vector_index = index
            
            logger.info("Created vector index for shipment similarity search")
        except Exception as e:
            logger.error(f"Error creating vector index: {e}")

    def _extract_location_features(self, location):
        """Extract location features for vector indexing.

        Args:
            location: Location dictionary

        Returns:
            List of location features [latitude, longitude]
        """
        if not location or not isinstance(location, dict):
            return [0.0, 0.0]
            
        # Try to get coordinates
        coords = location.get("coordinates", {})
        if coords and isinstance(coords, dict):
            lat = coords.get("latitude", 0.0)
            lon = coords.get("longitude", 0.0)
            return [float(lat), float(lon)]
            
        # Fallback to direct lat/lon if available
        lat = location.get("latitude", 0.0)
        lon = location.get("longitude", 0.0)
        return [float(lat), float(lon)]

    def run(self):
        """Run the pipeline."""
        logger.info(f"Starting shipment pipeline: monitoring {self.input_dir} for new data")
        logger.info(f"Processed shipments will be written to {self.output_dir}")
        
        # Build and run the pipeline
        self.build_pipeline()
        
        try:
            # Keep the pipeline running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
        finally:
            if self.pw_context:
                self.pw_context.stop()


def run_shipment_pipeline(input_dir, output_dir, historical_data_path=None):
    """Run the shipment pipeline.

    Args:
        input_dir: Directory to monitor for new shipment data files
        output_dir: Directory to write processed shipment data
        historical_data_path: Path to historical shipment data (optional)

    Returns:
        None
    """
    pipeline = ShipmentPipeline(input_dir, output_dir, historical_data_path)
    pipeline.run()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run shipment anomaly detection pipeline')
    parser.add_argument('--input', required=True, help='Input directory to monitor for shipment data')
    parser.add_argument('--output', required=True, help='Output directory for processed shipments')
    parser.add_argument('--historical', help='Historical shipment data CSV file')

    args = parser.parse_args()

    run_shipment_pipeline(args.input, args.output, args.historical)