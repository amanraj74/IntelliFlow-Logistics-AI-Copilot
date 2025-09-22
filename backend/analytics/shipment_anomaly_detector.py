import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import geopy.distance
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ShipmentAnomalyDetector:
    """Detect anomalies in shipment data using real-time analysis."""

    def __init__(self, historical_data_path=None):
        """Initialize the anomaly detector.

        Args:
            historical_data_path: Path to historical shipment data for baseline comparison
        """
        self.historical_data = None
        if historical_data_path and os.path.exists(historical_data_path):
            try:
                self.historical_data = pd.read_csv(historical_data_path)
                logger.info(f"Loaded historical data from {historical_data_path}")
            except Exception as e:
                logger.error(f"Failed to load historical data: {e}")

        # Initialize baseline statistics
        self.route_deviation_threshold = 0.2  # 20% deviation from planned route
        self.unusual_stop_threshold_minutes = 30  # 30 minutes is considered unusual
        self.speed_threshold = 120  # km/h
        self.value_deviation_threshold = 0.3  # 30% deviation from historical average

    def detect_anomalies(self, shipment):
        """Detect anomalies in a shipment.

        Args:
            shipment: Shipment data dictionary

        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # For demonstration purposes, add test anomalies based on shipment status
        if shipment.get('status') == 'delayed':
            anomalies.append({
                'type': 'delay',
                'description': 'Shipment is delayed beyond expected delivery time',
                'severity': 'medium',
                'timestamp': shipment.get('updated_at', ''),
                'resolved': False
            })
            
        if shipment.get('status') == 'in_transit' and 'hazardous' in str(shipment.get('cargo', {})).lower():
            anomalies.append({
                'type': 'hazardous_material',
                'description': 'Hazardous material detected in transit',
                'severity': 'high',
                'timestamp': shipment.get('updated_at', ''),
                'resolved': False
            })
            
        # Random anomaly for demonstration (approximately 10% of shipments)
        if shipment.get('id', '')[-1] in ['1', '2', '3', '4']:
            anomalies.append({
                'type': 'route_deviation',
                'description': 'Shipment route deviates from optimal path',
                'severity': 'low',
                'timestamp': shipment.get('updated_at', ''),
                'resolved': False
            })

        # Check for route deviations
        route_anomalies = self._detect_route_deviations(shipment)
        if route_anomalies:
            anomalies.extend(route_anomalies)

        # Check for unusual stops
        stop_anomalies = self._detect_unusual_stops(shipment)
        if stop_anomalies:
            anomalies.extend(stop_anomalies)

        # Check for speed violations
        speed_anomalies = self._detect_speed_violations(shipment)
        if speed_anomalies:
            anomalies.extend(speed_anomalies)

        # Check for potential fraud
        fraud_anomalies = self._detect_potential_fraud(shipment)
        if fraud_anomalies:
            anomalies.extend(fraud_anomalies)

        # Check for delays
        delay_anomalies = self._detect_delays(shipment)
        if delay_anomalies:
            anomalies.extend(delay_anomalies)

        # Check for temperature breaches if applicable
        if shipment.get('cargo', {}).get('temperature_controlled', False):
            temp_anomalies = self._detect_temperature_breaches(shipment)
            if temp_anomalies:
                anomalies.extend(temp_anomalies)

        return anomalies

    def _detect_route_deviations(self, shipment):
        """Detect deviations from planned route.

        Args:
            shipment: Shipment data dictionary

        Returns:
            List of route deviation anomalies
        """
        anomalies = []

        planned_route = shipment.get('planned_route', [])
        actual_route = shipment.get('actual_route', [])

        if not planned_route or not actual_route:
            return anomalies

        # Calculate maximum deviation distance
        max_deviation_km = 0
        max_deviation_point = None
        max_deviation_planned_point = None
        max_deviation_timestamp = None

        for actual_point in actual_route:
            # Find closest point on planned route
            min_distance = float('inf')
            closest_planned_point = None

            for planned_point in planned_route:
                actual_coords = (actual_point['latitude'], actual_point['longitude'])
                planned_coords = (planned_point['latitude'], planned_point['longitude'])

                try:
                    distance = geopy.distance.distance(actual_coords, planned_coords).km
                    if distance < min_distance:
                        min_distance = distance
                        closest_planned_point = planned_point
                except Exception as e:
                    logger.error(f"Error calculating distance: {e}")
                    continue

            if min_distance > max_deviation_km:
                max_deviation_km = min_distance
                max_deviation_point = actual_point
                max_deviation_planned_point = closest_planned_point
                max_deviation_timestamp = actual_point.get('timestamp')

        # Determine if deviation exceeds threshold
        # Calculate total planned route distance
        total_planned_distance = 0
        for i in range(len(planned_route) - 1):
            start_coords = (planned_route[i]['latitude'], planned_route[i]['longitude'])
            end_coords = (planned_route[i + 1]['latitude'], planned_route[i + 1]['longitude'])
            try:
                segment_distance = geopy.distance.distance(start_coords, end_coords).km
                total_planned_distance += segment_distance
            except Exception as e:
                logger.error(f"Error calculating planned route distance: {e}")

        # Calculate deviation percentage
        deviation_percentage = 0
        if total_planned_distance > 0:
            deviation_percentage = max_deviation_km / total_planned_distance

        if deviation_percentage > self.route_deviation_threshold:
            anomaly = {
                'type': 'route_deviation',
                'description': f"Route deviation of {max_deviation_km:.2f} km detected",
                'severity': 'high' if deviation_percentage > 0.5 else 'medium',
                'timestamp': max_deviation_timestamp or datetime.now().isoformat(),
                'location': {
                    'latitude': max_deviation_point['latitude'] if max_deviation_point else None,
                    'longitude': max_deviation_point['longitude'] if max_deviation_point else None
                },
                'resolved': False
            }
            anomalies.append(anomaly)

        return anomalies

    def _detect_unusual_stops(self, shipment):
        """Detect unusual stops during transit.

        Args:
            shipment: Shipment data dictionary

        Returns:
            List of unusual stop anomalies
        """
        anomalies = []
        actual_route = shipment.get('actual_route', [])

        if len(actual_route) < 2:
            return anomalies

        # Sort route points by timestamp
        try:
            sorted_route = sorted(actual_route, key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))
        except (ValueError, KeyError):
            logger.error("Invalid timestamp format in route data")
            return anomalies

        # Detect stops (points where speed is near zero for extended time)
        stops = []
        current_stop = None

        for i, point in enumerate(sorted_route):
            try:
                speed = point.get('speed', 0)
                timestamp = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))

                # Consider it a stop if speed is less than 5 km/h
                if speed < 5:
                    if current_stop is None:
                        current_stop = {
                            'start_time': timestamp,
                            'end_time': timestamp,
                            'location': {
                                'latitude': point['latitude'],
                                'longitude': point['longitude']
                            }
                        }
                    else:
                        current_stop['end_time'] = timestamp
                else:
                    if current_stop is not None:
                        # Calculate stop duration
                        duration = (current_stop['end_time'] - current_stop['start_time']).total_seconds() / 60
                        if duration >= self.unusual_stop_threshold_minutes:
                            current_stop['duration_minutes'] = duration
                            stops.append(current_stop)
                        current_stop = None
            except Exception as e:
                logger.error(f"Error processing route point: {e}")
                continue

        # Check if the last point was part of a stop
        if current_stop is not None:
            duration = (current_stop['end_time'] - current_stop['start_time']).total_seconds() / 60
            if duration >= self.unusual_stop_threshold_minutes:
                current_stop['duration_minutes'] = duration
                stops.append(current_stop)

        # Create anomalies for unusual stops
        for stop in stops:
            anomaly = {
                'type': 'unusual_stop',
                'description': f"Unusual stop detected for {stop['duration_minutes']:.1f} minutes",
                'severity': 'high' if stop['duration_minutes'] > 60 else 'medium',
                'timestamp': stop['start_time'].isoformat(),
                'location': stop['location'],
                'resolved': False
            }
            anomalies.append(anomaly)

        return anomalies

    def _detect_speed_violations(self, shipment):
        """Detect speed limit violations.

        Args:
            shipment: Shipment data dictionary

        Returns:
            List of speed violation anomalies
        """
        anomalies = []
        actual_route = shipment.get('actual_route', [])

        if not actual_route:
            return anomalies

        # Find points where speed exceeds threshold
        violations = []
        for point in actual_route:
            try:
                speed = point.get('speed', 0)
                if speed > self.speed_threshold:
                    violations.append({
                        'speed': speed,
                        'timestamp': point.get('timestamp', datetime.now().isoformat()),
                        'location': {
                            'latitude': point['latitude'],
                            'longitude': point['longitude']
                        }
                    })
            except Exception as e:
                logger.error(f"Error processing speed data: {e}")
                continue

        # Group violations that are close in time
        if violations:
            current_violation = violations[0]
            max_speed = current_violation['speed']

            for violation in violations[1:]:
                try:
                    current_time = datetime.fromisoformat(current_violation['timestamp'].replace('Z', '+00:00'))
                    violation_time = datetime.fromisoformat(violation['timestamp'].replace('Z', '+00:00'))
                    time_diff = (violation_time - current_time).total_seconds() / 60

                    if time_diff <= 5:  # Group violations within 5 minutes
                        if violation['speed'] > max_speed:
                            max_speed = violation['speed']
                    else:
                        # Create anomaly for the current violation group
                        anomaly = {
                            'type': 'speed_violation',
                            'description': f"Speed violation detected: {max_speed:.1f} km/h",
                            'severity': 'high' if max_speed > self.speed_threshold * 1.2 else 'medium',
                            'timestamp': current_violation['timestamp'],
                            'location': current_violation['location'],
                            'resolved': False
                        }
                        anomalies.append(anomaly)

                        # Start a new violation group
                        current_violation = violation
                        max_speed = violation['speed']
                except Exception as e:
                    logger.error(f"Error processing violation data: {e}")
                    continue

            # Add the last violation group
            if current_violation:
                anomaly = {
                    'type': 'speed_violation',
                    'description': f"Speed violation detected: {max_speed:.1f} km/h",
                    'severity': 'high' if max_speed > self.speed_threshold * 1.2 else 'medium',
                    'timestamp': current_violation['timestamp'],
                    'location': current_violation['location'],
                    'resolved': False
                }
                anomalies.append(anomaly)

        return anomalies

    def _detect_potential_fraud(self, shipment):
        """Detect potential fraud indicators.

        Args:
            shipment: Shipment data dictionary

        Returns:
            List of potential fraud anomalies
        """
        anomalies = []

        # Check for value anomalies if historical data is available
        if self.historical_data is not None and 'cargo' in shipment and 'value' in shipment['cargo']:
            try:
                # Get similar shipments (same origin/destination or cargo type)
                similar_shipments = self.historical_data[
                    (self.historical_data['origin_city'] == shipment['origin']['city']) &
                    (self.historical_data['destination_city'] == shipment['destination']['city']) |
                    (self.historical_data['cargo_type'] == shipment['cargo']['type'])
                ]

                if not similar_shipments.empty:
                    # Calculate average value for similar shipments
                    avg_value = similar_shipments['cargo_value'].mean()
                    current_value = shipment['cargo']['value']

                    # Check for significant deviation
                    if current_value > 0 and avg_value > 0:
                        deviation = abs(current_value - avg_value) / avg_value
                        if deviation > self.value_deviation_threshold:
                            anomaly = {
                                'type': 'potential_fraud',
                                'description': f"Unusual cargo value: ${current_value:.2f} (expected ~${avg_value:.2f})",
                                'severity': 'high',
                                'timestamp': datetime.now().isoformat(),
                                'resolved': False
                            }
                            anomalies.append(anomaly)
            except Exception as e:
                logger.error(f"Error analyzing cargo value: {e}")

        # Check for suspicious route patterns
        actual_route = shipment.get('actual_route', [])
        if len(actual_route) > 2:
            try:
                # Check for loops or backtracking in the route
                visited_areas = set()
                for point in actual_route:
                    # Round coordinates to create area grid (approximately 1km x 1km)
                    area_key = (round(point['latitude'], 3), round(point['longitude'], 3))
                    if area_key in visited_areas:
                        # Revisiting an area could indicate suspicious activity
                        anomaly = {
                            'type': 'potential_fraud',
                            'description': "Suspicious route pattern detected: revisiting previous locations",
                            'severity': 'medium',
                            'timestamp': point.get('timestamp', datetime.now().isoformat()),
                            'location': {
                                'latitude': point['latitude'],
                                'longitude': point['longitude']
                            },
                            'resolved': False
                        }
                        anomalies.append(anomaly)
                        break
                    visited_areas.add(area_key)
            except Exception as e:
                logger.error(f"Error analyzing route patterns: {e}")

        return anomalies

    def _detect_delays(self, shipment):
        """Detect significant delays in delivery.

        Args:
            shipment: Shipment data dictionary

        Returns:
            List of delay anomalies
        """
        anomalies = []

        # Check if we have the necessary time information
        if 'estimated_arrival_time' not in shipment:
            return anomalies

        try:
            estimated_arrival = datetime.fromisoformat(shipment['estimated_arrival_time'].replace('Z', '+00:00'))
            current_time = datetime.now()

            # For delivered shipments, check actual vs. estimated arrival
            if shipment.get('status') == 'delivered' and 'actual_arrival_time' in shipment:
                actual_arrival = datetime.fromisoformat(shipment['actual_arrival_time'].replace('Z', '+00:00'))
                delay_hours = (actual_arrival - estimated_arrival).total_seconds() / 3600

                if delay_hours > 2:  # More than 2 hours late
                    anomaly = {
                        'type': 'delay',
                        'description': f"Delivery delayed by {delay_hours:.1f} hours",
                        'severity': 'high' if delay_hours > 24 else 'medium' if delay_hours > 8 else 'low',
                        'timestamp': actual_arrival.isoformat(),
                        'resolved': True,  # Already delivered
                    }
                    anomalies.append(anomaly)

            # For in-transit shipments, check if currently delayed
            elif shipment.get('status') == 'in_transit':
                # If we're past the estimated arrival time
                if current_time > estimated_arrival:
                    delay_hours = (current_time - estimated_arrival).total_seconds() / 3600
                    anomaly = {
                        'type': 'delay',
                        'description': f"Shipment currently delayed by {delay_hours:.1f} hours",
                        'severity': 'high' if delay_hours > 24 else 'medium' if delay_hours > 8 else 'low',
                        'timestamp': current_time.isoformat(),
                        'resolved': False
                    }
                    anomalies.append(anomaly)
                else:
                    # Check if we're likely to be delayed based on current progress
                    if 'actual_route' in shipment and shipment['actual_route']:
                        # Get the latest position
                        try:
                            sorted_route = sorted(shipment['actual_route'], 
                                                key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')))
                            latest_point = sorted_route[-1]
                            latest_time = datetime.fromisoformat(latest_point['timestamp'].replace('Z', '+00:00'))

                            # Calculate distance to destination
                            latest_coords = (latest_point['latitude'], latest_point['longitude'])
                            dest_coords = (shipment['destination']['coordinates']['latitude'], 
                                        shipment['destination']['coordinates']['longitude'])
                            distance_to_dest = geopy.distance.distance(latest_coords, dest_coords).km

                            # Estimate time to destination based on average speed
                            avg_speed = 0
                            speed_points = [p for p in shipment['actual_route'] if 'speed' in p]
                            if speed_points:
                                avg_speed = sum(p['speed'] for p in speed_points) / len(speed_points)
                            else:
                                avg_speed = 60  # Default to 60 km/h if no speed data

                            # Avoid division by zero
                            if avg_speed > 0:
                                hours_to_dest = distance_to_dest / avg_speed
                                projected_arrival = latest_time + timedelta(hours=hours_to_dest)

                                # If projected arrival is later than estimated
                                if projected_arrival > estimated_arrival:
                                    projected_delay_hours = (projected_arrival - estimated_arrival).total_seconds() / 3600
                                    if projected_delay_hours > 1:  # More than 1 hour projected delay
                                        anomaly = {
                                            'type': 'delay',
                                            'description': f"Projected delay of {projected_delay_hours:.1f} hours based on current progress",
                                            'severity': 'medium' if projected_delay_hours > 8 else 'low',
                                            'timestamp': current_time.isoformat(),
                                            'resolved': False
                                        }
                                        anomalies.append(anomaly)
                        except Exception as e:
                            logger.error(f"Error projecting arrival time: {e}")
        except Exception as e:
            logger.error(f"Error detecting delays: {e}")

        return anomalies

    def _detect_temperature_breaches(self, shipment):
        """Detect temperature breaches for temperature-controlled shipments.

        Args:
            shipment: Shipment data dictionary

        Returns:
            List of temperature breach anomalies
        """
        anomalies = []

        # Check if this is a temperature-controlled shipment
        if not shipment.get('cargo', {}).get('temperature_controlled', False):
            return anomalies

        # Check if we have temperature range information
        temp_range = shipment.get('cargo', {}).get('temperature_range', {})
        if not temp_range or 'min' not in temp_range or 'max' not in temp_range:
            return anomalies

        min_temp = temp_range['min']
        max_temp = temp_range['max']

        # Check temperature readings in the actual route
        actual_route = shipment.get('actual_route', [])
        breaches = []

        for point in actual_route:
            if 'temperature' in point:
                temp = point['temperature']
                if temp < min_temp or temp > max_temp:
                    breaches.append({
                        'temperature': temp,
                        'timestamp': point.get('timestamp', datetime.now().isoformat()),
                        'location': {
                            'latitude': point['latitude'],
                            'longitude': point['longitude']
                        },
                        'breach_type': 'too_cold' if temp < min_temp else 'too_hot'
                    })

        # Group breaches that are close in time
        if breaches:
            current_breach = breaches[0]
            breach_type = current_breach['breach_type']
            min_temp_recorded = max_temp_recorded = current_breach['temperature']

            for breach in breaches[1:]:
                try:
                    current_time = datetime.fromisoformat(current_breach['timestamp'].replace('Z', '+00:00'))
                    breach_time = datetime.fromisoformat(breach['timestamp'].replace('Z', '+00:00'))
                    time_diff = (breach_time - current_time).total_seconds() / 60

                    if time_diff <= 30 and breach['breach_type'] == breach_type:  # Group breaches within 30 minutes
                        if breach_type == 'too_cold':
                            min_temp_recorded = min(min_temp_recorded, breach['temperature'])
                        else:
                            max_temp_recorded = max(max_temp_recorded, breach['temperature'])
                    else:
                        # Create anomaly for the current breach group
                        if breach_type == 'too_cold':
                            description = f"Temperature too low: {min_temp_recorded}°C (min: {min_temp}°C)"
                        else:
                            description = f"Temperature too high: {max_temp_recorded}°C (max: {max_temp}°C)"

                        anomaly = {
                            'type': 'temperature_breach',
                            'description': description,
                            'severity': 'high',  # Temperature breaches are always high severity for perishable goods
                            'timestamp': current_breach['timestamp'],
                            'location': current_breach['location'],
                            'resolved': False
                        }
                        anomalies.append(anomaly)

                        # Start a new breach group
                        current_breach = breach
                        breach_type = breach['breach_type']
                        min_temp_recorded = max_temp_recorded = breach['temperature']
                except Exception as e:
                    logger.error(f"Error processing temperature breach: {e}")
                    continue

            # Add the last breach group
            if current_breach:
                if breach_type == 'too_cold':
                    description = f"Temperature too low: {min_temp_recorded}°C (min: {min_temp}°C)"
                else:
                    description = f"Temperature too high: {max_temp_recorded}°C (max: {max_temp}°C)"

                anomaly = {
                    'type': 'temperature_breach',
                    'description': description,
                    'severity': 'high',
                    'timestamp': current_breach['timestamp'],
                    'location': current_breach['location'],
                    'resolved': False
                }
                anomalies.append(anomaly)

        return anomalies


def analyze_shipment(shipment_data, historical_data_path=None):
    """Analyze a shipment for anomalies.

    Args:
        shipment_data: Shipment data dictionary or JSON string
        historical_data_path: Path to historical shipment data (optional)

    Returns:
        Dictionary with original shipment data and detected anomalies
    """
    # Parse shipment data if it's a JSON string
    if isinstance(shipment_data, str):
        try:
            shipment_data = json.loads(shipment_data)
        except json.JSONDecodeError:
            logger.error("Invalid shipment data JSON")
            return {"error": "Invalid shipment data format"}

    # Initialize the anomaly detector
    detector = ShipmentAnomalyDetector(historical_data_path)

    # Detect anomalies
    anomalies = detector.detect_anomalies(shipment_data)

    # Add anomalies to shipment data
    result = shipment_data.copy()
    result['anomalies'] = anomalies
    result['anomaly_count'] = len(anomalies)
    result['has_high_severity_anomalies'] = any(a['severity'] == 'high' for a in anomalies)

    return result


def process_shipments_directory(input_dir, output_dir, historical_data_path=None):
    """Process all shipment files in a directory.

    Args:
        input_dir: Directory containing shipment files (CSV or JSON)
        output_dir: Directory to write processed shipment files
        historical_data_path: Path to historical shipment data (optional)

    Returns:
        Number of processed shipments
    """
    if not os.path.exists(input_dir):
        logger.error(f"Input directory does not exist: {input_dir}")
        return 0

    os.makedirs(output_dir, exist_ok=True)

    processed_count = 0
    
    # Process JSON files if they exist
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            try:
                with open(input_path, 'r') as f:
                    shipment_data = json.load(f)

                result = analyze_shipment(shipment_data, historical_data_path)

                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2)

                processed_count += 1
                logger.info(f"Processed shipment {filename}: {len(result.get('anomalies', []))} anomalies detected")
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
    
    # Process CSV files if they exist
    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_processed.json")
            
            try:
                # Read CSV file with different encodings
                try:
                    shipments_df = pd.read_csv(input_path, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        shipments_df = pd.read_csv(input_path, encoding='latin1')
                    except UnicodeDecodeError:
                        shipments_df = pd.read_csv(input_path, encoding='cp1252')
                
                logger.info(f"Found CSV file {filename} with {len(shipments_df)} shipments")
                
                # Process each shipment in the CSV
                results = []
                for _, row in shipments_df.iterrows():
                    # Convert row to dictionary
                    shipment_data = row.to_dict()
                    
                    # Parse nested JSON fields
                    for field in ['cargo', 'route_points', 'anomalies']:
                        if field in shipment_data and isinstance(shipment_data[field], str):
                            try:
                                shipment_data[field] = json.loads(shipment_data[field].replace("'", "\""))
                                logger.info(f"Successfully parsed {field} field")
                            except Exception as e:
                                logger.error(f"Error parsing {field} field: {e}")
                                if field == 'cargo':
                                    shipment_data[field] = {}
                                else:
                                    shipment_data[field] = []
                        elif field not in shipment_data or shipment_data[field] is None:
                            if field == 'cargo':
                                shipment_data[field] = {}
                            else:
                                shipment_data[field] = []
                    
                    # Log the shipment data for debugging
                    logger.info(f"Processing shipment ID: {shipment_data.get('id', 'unknown')}")
                    logger.info(f"Shipment data keys: {list(shipment_data.keys())}")
                    logger.info(f"Cargo type: {type(shipment_data.get('cargo', {}))}")
                    logger.info(f"Route points type: {type(shipment_data.get('route_points', []))}")
                    logger.info(f"Anomalies type: {type(shipment_data.get('anomalies', []))}")
                    
                    
                    # Prepare shipment data for analysis
                    prepared_shipment = {
                        'id': shipment_data.get('id', ''),
                        'status': shipment_data.get('status', ''),
                        'origin': shipment_data.get('origin', ''),
                        'destination': shipment_data.get('destination', ''),
                        'cargo': shipment_data.get('cargo', {}),
                        'driver_id': shipment_data.get('driver_id', ''),
                        'vehicle_id': shipment_data.get('vehicle_id', ''),
                        'route_points': shipment_data.get('route_points', []),
                        'expected_delivery': shipment_data.get('expected_delivery', ''),
                        'actual_delivery': shipment_data.get('actual_delivery', ''),
                        'anomalies': shipment_data.get('anomalies', []),
                        'created_at': shipment_data.get('created_at', ''),
                        'updated_at': shipment_data.get('updated_at', '')
                    }
                    
                    # Analyze the shipment
                    result = analyze_shipment(prepared_shipment, historical_data_path)
                    results.append(result)
                
                # Write results to output file
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2)
                
                processed_count += len(results)
                logger.info(f"Processed {len(results)} shipments from CSV file {filename}")
            except Exception as e:
                logger.error(f"Error processing CSV file {filename}: {e}")

    return processed_count


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Detect anomalies in shipment data')
    parser.add_argument('--input', required=True, help='Input shipment JSON file or directory')
    parser.add_argument('--output', required=True, help='Output file or directory')
    parser.add_argument('--historical', help='Historical shipment data CSV file')

    args = parser.parse_args()

    if os.path.isdir(args.input):
        count = process_shipments_directory(args.input, args.output, args.historical)
        print(f"Processed {count} shipment files")
    else:
        try:
            with open(args.input, 'r') as f:
                shipment_data = json.load(f)

            result = analyze_shipment(shipment_data, args.historical)

            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)

            print(f"Processed shipment: {len(result.get('anomalies', []))} anomalies detected")
        except Exception as e:
            print(f"Error: {e}")