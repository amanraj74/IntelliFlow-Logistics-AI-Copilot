import os
import csv
import json
import random
import datetime
import time
import argparse
from pathlib import Path


class DataGenerator:
    """Generate sample data for the logistics system."""

    def __init__(self, output_dir="data/streams"):
        """Initialize the data generator.

        Args:
            output_dir: Directory to write generated data files
        """
        self.output_dir = output_dir
        self.driver_ids = []
        self.vehicle_ids = []
        self.incident_ids = []
        self.invoice_ids = []
        self.shipment_ids = []
        
        # Ensure output directories exist
        for subdir in ["drivers", "vehicles", "incidents", "invoices", "shipments"]:
            os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)

    def generate_drivers(self, count=20):
        """Generate sample driver data.

        Args:
            count: Number of drivers to generate
        """
        drivers = []
        self.driver_ids = []

        first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
                      "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
        last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
                     "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson"]

        for i in range(1, count + 1):
            driver_id = f"D{i:03d}"
            self.driver_ids.append(driver_id)
            
            # Generate a risk score with some drivers having high risk
            risk_score = random.uniform(0.1, 0.9)
            if i <= int(count * 0.15):  # Make 15% of drivers high risk
                risk_score = random.uniform(0.7, 0.95)
            
            driver = {
                "id": driver_id,
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "license_number": f"LIC{random.randint(100000, 999999)}",
                "risk_score": round(risk_score, 2),
                "vehicle_id": f"V{random.randint(1, count):03d}" if i > 3 else "",  # Some drivers have no vehicle
                "status": random.choice(["active", "active", "active", "inactive", "on_leave"]),
                "last_updated": self._generate_timestamp(days_back=random.randint(1, 30))
            }
            drivers.append(driver)

        # Write to CSV
        self._write_csv(os.path.join(self.output_dir, "drivers", "drivers.csv"), drivers)
        return drivers

    def generate_vehicles(self, count=20):
        """Generate sample vehicle data.

        Args:
            count: Number of vehicles to generate
        """
        vehicles = []
        self.vehicle_ids = []

        makes = ["Volvo", "Freightliner", "Kenworth", "Peterbilt", "Mack", "International", "Ford", "Chevrolet", "Toyota", "Mercedes"]
        models = ["FH16", "Cascadia", "T680", "579", "Anthem", "ProStar", "F-650", "Silverado", "Tundra", "Actros"]

        for i in range(1, count + 1):
            vehicle_id = f"V{i:03d}"
            self.vehicle_ids.append(vehicle_id)
            
            # Generate maintenance history
            maintenance_history = []
            for _ in range(random.randint(0, 5)):
                maintenance_history.append({
                    "date": self._generate_timestamp(days_back=random.randint(30, 365)),
                    "type": random.choice(["routine", "repair", "inspection", "other"]),
                    "description": random.choice(["Oil change", "Brake inspection", "Tire rotation", "Engine repair", "Annual inspection"]),
                    "cost": round(random.uniform(50, 2000), 2)
                })
            
            vehicle = {
                "id": vehicle_id,
                "type": random.choice(["truck", "van", "semi", "trailer"]),
                "make": random.choice(makes),
                "model": random.choice(models),
                "year": random.randint(2015, 2023),
                "license_plate": f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.randint(100, 999)}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}",
                "vin": f"{random.randint(10000000, 99999999)}",
                "status": random.choice(["active", "active", "active", "maintenance", "repair"]),
                "current_driver_id": random.choice(self.driver_ids) if self.driver_ids and i % 3 != 0 else "",  # Some vehicles have no driver
                "fuel_type": random.choice(["diesel", "gasoline", "electric", "hybrid"]),
                "last_inspection_date": self._generate_timestamp(days_back=random.randint(1, 180)),
                "next_inspection_due": self._generate_timestamp(days_ahead=random.randint(1, 180)),
                "last_updated": self._generate_timestamp(days_back=random.randint(1, 30))
            }
            vehicles.append(vehicle)

        # Write to CSV
        self._write_csv(os.path.join(self.output_dir, "vehicles", "vehicles.csv"), vehicles)
        return vehicles

    def generate_incidents(self, count=50):
        """Generate sample incident data.

        Args:
            count: Number of incidents to generate
        """
        incidents = []
        self.incident_ids = []

        incident_types = [
            {"type": "speeding", "desc": "Driver exceeded speed limit by {speed} mph", "severity": ["low", "medium", "high"]},
            {"type": "harsh_braking", "desc": "Harsh braking incident recorded", "severity": ["low", "medium"]},
            {"type": "accident", "desc": "Vehicle involved in {type} collision", "severity": ["medium", "high"]},
            {"type": "late_delivery", "desc": "Delivery delayed by {hours} hours", "severity": ["low", "medium"]},
            {"type": "route_deviation", "desc": "Driver deviated from planned route by {miles} miles", "severity": ["low", "medium", "high"]},
            {"type": "violation", "desc": "Driver violated {rule} regulation", "severity": ["medium", "high"]}
        ]

        locations = [
            "Interstate 95, Miami, FL",
            "Highway 101, San Francisco, CA",
            "Interstate 80, Chicago, IL",
            "Route 66, Albuquerque, NM",
            "Interstate 10, Houston, TX",
            "Interstate 5, Seattle, WA",
            "Highway 401, Toronto, ON",
            "Interstate 90, Boston, MA",
            "Interstate 75, Atlanta, GA",
            "Interstate 15, Las Vegas, NV"
        ]

        for i in range(1, count + 1):
            incident_id = f"I{i:04d}"
            self.incident_ids.append(incident_id)
            
            # Select a random incident type
            incident_type = random.choice(incident_types)
            severity = random.choice(incident_type["severity"])
            
            # Format the description based on the incident type
            description = incident_type["desc"]
            if "{speed}" in description:
                description = description.format(speed=random.randint(10, 30))
            elif "{type}" in description:
                description = description.format(type=random.choice(["rear-end", "side", "minor", "major"]))
            elif "{hours}" in description:
                description = description.format(hours=random.randint(1, 12))
            elif "{miles}" in description:
                description = description.format(miles=random.randint(5, 50))
            elif "{rule}" in description:
                description = description.format(rule=random.choice(["hours of service", "weight limit", "safety", "cargo securing"]))
            
            # Generate a date within the last 90 days
            date = self._generate_timestamp(days_back=random.randint(1, 90))
            
            incident = {
                "id": incident_id,
                "driver_id": random.choice(self.driver_ids) if self.driver_ids else f"D{random.randint(1, 20):03d}",
                "date": date,
                "severity": severity,
                "description": description,
                "location": random.choice(locations),
                "reported_by": random.choice(["driver", "system", "manager", "customer"]),
                "status": random.choice(["reported", "investigating", "resolved", "closed"]),
                "resolution": "" if random.random() < 0.3 else "Driver received additional training",
                "timestamp": date
            }
            incidents.append(incident)

        # Write to CSV
        self._write_csv(os.path.join(self.output_dir, "incidents", "incidents.csv"), incidents)
        return incidents

    def generate_invoices(self, count=30):
        """Generate sample invoice data.

        Args:
            count: Number of invoices to generate
        """
        invoices = []
        self.invoice_ids = []

        payment_terms = ["Net 30", "Net 60", "Net 15", "Due on Receipt"]
        payment_methods = ["Credit Card", "Bank Transfer", "Check", "Cash"]

        for i in range(1, count + 1):
            invoice_id = f"INV{i:05d}"
            self.invoice_ids.append(invoice_id)
            
            # Generate random amount
            amount = round(random.uniform(500, 10000), 2)
            
            # Generate dates
            issue_date = self._generate_timestamp(days_back=random.randint(10, 90))
            
            # Parse the issue date to add days for due date
            issue_dt = datetime.datetime.fromisoformat(issue_date.replace('Z', '+00:00'))
            
            # Determine payment terms and due date
            term = random.choice(payment_terms)
            if term == "Net 30":
                days_to_add = 30
            elif term == "Net 60":
                days_to_add = 60
            elif term == "Net 15":
                days_to_add = 15
            else:  # Due on Receipt
                days_to_add = 0
                
            due_dt = issue_dt + datetime.timedelta(days=days_to_add)
            due_date = due_dt.isoformat()
            
            # Determine if invoice is paid
            is_paid = random.random() < 0.7  # 70% of invoices are paid
            
            # If paid, generate payment date
            payment_date = ""
            if is_paid:
                # Payment date between issue date and now
                payment_days = random.randint(0, min(30, (datetime.datetime.now() - issue_dt).days))
                payment_dt = issue_dt + datetime.timedelta(days=payment_days)
                payment_date = payment_dt.isoformat()
            
            # Determine status
            if is_paid:
                status = "paid"
            elif due_dt < datetime.datetime.now():
                status = "overdue"
            else:
                status = "issued"
            
            # Generate line items
            line_items = []
            num_items = random.randint(1, 5)
            for j in range(num_items):
                quantity = random.randint(1, 10)
                unit_price = round(random.uniform(50, 1000), 2)
                line_items.append({
                    "description": random.choice(["Freight delivery", "Express shipping", "Warehousing", "Packaging", "Handling fee"]),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "amount": round(quantity * unit_price, 2)
                })
            
            # Calculate total from line items
            total_amount = sum(item["amount"] for item in line_items)
            
            invoice = {
                "id": invoice_id,
                "order_id": f"ORD{random.randint(10000, 99999)}",
                "customer_id": f"CUST{random.randint(100, 999)}",
                "amount": round(total_amount, 2),
                "currency": "USD",
                "issue_date": issue_date,
                "due_date": due_date,
                "payment_terms": term,
                "early_payment_discount": round(random.uniform(0, 5), 2) if random.random() < 0.3 else 0,
                "late_payment_fee": round(random.uniform(1, 10), 2) if random.random() < 0.5 else 0,
                "status": status,
                "payment_date": payment_date,
                "payment_method": random.choice(payment_methods) if is_paid else "",
                "line_items": line_items,
                "notes": "",
                "compliance_flags": [] if random.random() < 0.8 else [random.choice(["missing_po", "incorrect_amount", "late_submission"])],
                "last_updated": self._generate_timestamp(days_back=random.randint(0, 10))
            }
            invoices.append(invoice)

        # Write to CSV
        self._write_csv(os.path.join(self.output_dir, "invoices", "invoices.csv"), invoices)
        return invoices

    def generate_streaming_data(self, interval=5, count=10):
        """Generate streaming data by appending to CSV files at intervals.

        Args:
            interval: Seconds between data generation
            count: Number of iterations to generate data
        """
        print(f"Starting streaming data generation. Will generate {count} updates at {interval} second intervals.")
        
        for i in range(count):
            print(f"Generating data batch {i+1}/{count}...")
            
            # Generate a new incident
            self._generate_streaming_incident()
            
            # Update a random driver's risk score
            self._update_random_driver_risk()
            
            # Generate a new invoice every 3rd iteration
            if i % 3 == 0:
                self._generate_streaming_invoice()
            
            # Generate a new shipment or update existing shipment every 2nd iteration
            if i % 2 == 0:
                self._generate_streaming_shipment()
            else:
                self._update_random_shipment_status()
                
            print(f"Waiting {interval} seconds before next update...")
            time.sleep(interval)
            
        print("Streaming data generation complete.")

    def _generate_streaming_incident(self):
        """Generate a new incident and append to incidents.csv"""
        # Read existing incidents to avoid ID conflicts
        existing_incidents = self._read_csv(os.path.join(self.output_dir, "incidents", "incidents.csv"))
        
        # Find the highest ID number
        max_id = 0
        for incident in existing_incidents:
            if incident["id"].startswith("I"):
                try:
                    id_num = int(incident["id"][1:])
                    max_id = max(max_id, id_num)
                except ValueError:
                    pass
        
        # Create a new incident with the next ID
        new_id = f"I{max_id + 1:04d}"
        
        # Select a random driver
        drivers = self._read_csv(os.path.join(self.output_dir, "drivers", "drivers.csv"))
        if not drivers:
            return
        
        driver = random.choice(drivers)
        driver_id = driver["id"]
        
        # Generate a high severity incident with 30% probability
        is_high_severity = random.random() < 0.3
        severity = "high" if is_high_severity else random.choice(["low", "medium"])
        
        # Generate description based on severity
        if is_high_severity:
            description = random.choice([
                f"Driver involved in accident on highway",
                f"Significant route deviation detected",
                f"Driver exceeded speed limit by {random.randint(20, 40)} mph",
                f"Vehicle breakdown requiring immediate assistance",
                f"Hours of service violation detected"
            ])
        else:
            description = random.choice([
                f"Minor delay in delivery schedule",
                f"Driver exceeded speed limit by {random.randint(5, 15)} mph",
                f"Brief unscheduled stop detected",
                f"Minor route deviation",
                f"Late departure from warehouse"
            ])
        
        # Generate location
        locations = [
            "Interstate 95, Miami, FL",
            "Highway 101, San Francisco, CA",
            "Interstate 80, Chicago, IL",
            "Route 66, Albuquerque, NM",
            "Interstate 10, Houston, TX"
        ]
        location = random.choice(locations)
        
        # Create the new incident
        new_incident = {
            "id": new_id,
            "driver_id": driver_id,
            "date": datetime.datetime.now().isoformat(),
            "severity": severity,
            "description": description,
            "location": location,
            "reported_by": random.choice(["system", "manager"]),
            "status": "reported",
            "resolution": "",
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Append to CSV
        self._append_csv(os.path.join(self.output_dir, "incidents", "incidents.csv"), [new_incident])
        print(f"Generated new incident: {new_id} - {severity} severity for driver {driver_id}")

    def _update_random_driver_risk(self):
        """Update a random driver's risk score"""
        # Read existing drivers
        drivers = self._read_csv(os.path.join(self.output_dir, "drivers", "drivers.csv"))
        if not drivers:
            return
        
        # Select a random driver to update
        driver_index = random.randint(0, len(drivers) - 1)
        driver = drivers[driver_index]
        
        # Get current risk score
        try:
            current_risk = float(driver["risk_score"])
        except (ValueError, KeyError):
            current_risk = 0.5
        
        # Generate new risk score with some volatility
        change = random.uniform(-0.15, 0.15)
        new_risk = max(0.1, min(0.95, current_risk + change))
        
        # Update the driver's risk score
        drivers[driver_index]["risk_score"] = round(new_risk, 2)
        drivers[driver_index]["last_updated"] = datetime.datetime.now().isoformat()
        
        # Write back to CSV
        self._write_csv(os.path.join(self.output_dir, "drivers", "drivers.csv"), drivers)
        print(f"Updated driver {driver['id']} risk score: {current_risk:.2f} -> {new_risk:.2f}")

    def generate_shipments(self, count=40):
        """Generate sample shipment data.

        Args:
            count: Number of shipments to generate
        """
        shipments = []
        self.shipment_ids = []

        # Define possible values for shipment properties
        statuses = ["scheduled", "in_transit", "delivered", "delayed", "cancelled"]
        cargo_types = ["general", "perishable", "hazardous", "fragile", "oversized"]
        cities = [
            "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ",
            "Philadelphia, PA", "San Antonio, TX", "San Diego, CA", "Dallas, TX", "San Jose, CA",
            "Austin, TX", "Jacksonville, FL", "Fort Worth, TX", "Columbus, OH", "Charlotte, NC",
            "San Francisco, CA", "Indianapolis, IN", "Seattle, WA", "Denver, CO", "Boston, MA"
        ]
        
        # Generate anomaly types
        anomaly_types = [
            "route_deviation", "unusual_stop", "speed_violation", "potential_fraud", 
            "delay", "temperature_breach", "cargo_tampering", "unscheduled_maintenance"
        ]

        for i in range(1, count + 1):
            shipment_id = f"SH{i:04d}"
            self.shipment_ids.append(shipment_id)
            
            # Determine if this shipment has anomalies (30% chance)
            has_anomalies = random.random() < 0.3
            
            # Generate random origin and destination
            origin = random.choice(cities)
            # Make sure destination is different from origin
            destination = random.choice([city for city in cities if city != origin])
            
            # Generate timestamps
            created_at = self._generate_timestamp(days_back=random.randint(5, 30))
            estimated_delivery = self._generate_timestamp(days_ahead=random.randint(1, 10))
            
            # Parse created_at to datetime for calculations
            created_dt = datetime.datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            # Generate status and actual delivery date based on status
            status = random.choice(statuses)
            actual_delivery = ""
            
            if status == "delivered":
                # Delivered between created_at and now
                delivery_days = random.randint(1, max(1, (datetime.datetime.now() - created_dt).days))
                delivery_dt = created_dt + datetime.timedelta(days=delivery_days)
                actual_delivery = delivery_dt.isoformat()
            elif status == "in_transit":
                # No actual delivery date yet
                pass
            elif status == "delayed":
                # Estimated delivery pushed back
                estimated_delivery = self._generate_timestamp(days_ahead=random.randint(11, 20))
            
            # Generate cargo information
            cargo = {
                "type": random.choice(cargo_types),
                "weight": round(random.uniform(100, 5000), 2),
                "volume": round(random.uniform(1, 100), 2),
                "value": round(random.uniform(500, 50000), 2),
                "temperature_controlled": random.random() < 0.3,
                "hazardous": random.random() < 0.15
            }
            
            # Generate anomalies if applicable
            anomalies = []
            if has_anomalies:
                num_anomalies = random.randint(1, 3)
                for _ in range(num_anomalies):
                    anomaly_type = random.choice(anomaly_types)
                    anomaly = {
                        "type": anomaly_type,
                        "detected_at": self._generate_timestamp(days_back=random.randint(0, 5)),
                        "severity": random.choice(["low", "medium", "high"]),
                        "description": self._generate_anomaly_description(anomaly_type),
                        "location": f"{random.uniform(25, 48):.6f},{random.uniform(-125, -70):.6f}" if anomaly_type != "temperature_breach" else "",
                        "resolved": random.random() < 0.4
                    }
                    anomalies.append(anomaly)
            
            # Create the shipment object
            shipment = {
                "id": shipment_id,
                "status": status,
                "origin": origin,
                "destination": destination,
                "cargo": cargo,
                "driver_id": random.choice(self.driver_ids) if self.driver_ids else f"D{random.randint(1, 20):03d}",
                "vehicle_id": random.choice(self.vehicle_ids) if self.vehicle_ids else f"V{random.randint(1, 20):03d}",
                "route": self._generate_route_points(origin, destination),
                "estimated_delivery": estimated_delivery,
                "actual_delivery": actual_delivery,
                "anomalies": anomalies,
                "created_at": created_at,
                "last_updated": self._generate_timestamp(days_back=random.randint(0, 3))
            }
            
            shipments.append(shipment)

        # Write to CSV
        self._write_csv(os.path.join(self.output_dir, "shipments", "shipments.csv"), shipments)
        return shipments

    def _generate_anomaly_description(self, anomaly_type):
        """Generate a description for a shipment anomaly.

        Args:
            anomaly_type: Type of anomaly

        Returns:
            Description string
        """
        if anomaly_type == "route_deviation":
            return f"Vehicle deviated from planned route by {random.randint(5, 50)} miles"
        elif anomaly_type == "unusual_stop":
            return f"Unscheduled stop detected for {random.randint(15, 120)} minutes"
        elif anomaly_type == "speed_violation":
            return f"Vehicle exceeded speed limit by {random.randint(10, 30)} mph"
        elif anomaly_type == "potential_fraud":
            return random.choice([
                "Suspicious pattern of stops detected",
                "Unusual route changes detected",
                "Possible cargo tampering detected",
                "Unauthorized access to cargo area"
            ])
        elif anomaly_type == "delay":
            return f"Shipment delayed by {random.randint(1, 24)} hours"
        elif anomaly_type == "temperature_breach":
            return f"Cargo temperature exceeded acceptable range by {random.randint(3, 15)}°C"
        elif anomaly_type == "cargo_tampering":
            return "Possible unauthorized access to cargo detected"
        elif anomaly_type == "unscheduled_maintenance":
            return f"Vehicle required unscheduled maintenance causing {random.randint(1, 8)} hour delay"
        else:
            return "Unknown anomaly detected"

    def _generate_route_points(self, origin, destination):
        """Generate a series of route points between origin and destination.

        Args:
            origin: Origin city
            destination: Destination city

        Returns:
            List of route points
        """
        # This is a simplified version - in a real system, you'd use a mapping API
        # to generate actual route coordinates
        
        # Extract approximate lat/long from city names (very rough approximation)
        city_coords = {
            "New York, NY": (40.7128, -74.0060),
            "Los Angeles, CA": (34.0522, -118.2437),
            "Chicago, IL": (41.8781, -87.6298),
            "Houston, TX": (29.7604, -95.3698),
            "Phoenix, AZ": (33.4484, -112.0740),
            "Philadelphia, PA": (39.9526, -75.1652),
            "San Antonio, TX": (29.4241, -98.4936),
            "San Diego, CA": (32.7157, -117.1611),
            "Dallas, TX": (32.7767, -96.7970),
            "San Jose, CA": (37.3382, -121.8863),
            "Austin, TX": (30.2672, -97.7431),
            "Jacksonville, FL": (30.3322, -81.6557),
            "Fort Worth, TX": (32.7555, -97.3308),
            "Columbus, OH": (39.9612, -82.9988),
            "Charlotte, NC": (35.2271, -80.8431),
            "San Francisco, CA": (37.7749, -122.4194),
            "Indianapolis, IN": (39.7684, -86.1581),
            "Seattle, WA": (47.6062, -122.3321),
            "Denver, CO": (39.7392, -104.9903),
            "Boston, MA": (42.3601, -71.0589)
        }
        
        # Default coordinates if city not found
        origin_coords = city_coords.get(origin, (40.0, -95.0))
        dest_coords = city_coords.get(destination, (42.0, -75.0))
        
        # Generate 3-7 points along the route
        num_points = random.randint(3, 7)
        route_points = []
        
        # Add origin
        route_points.append({
            "lat": origin_coords[0],
            "lng": origin_coords[1],
            "timestamp": self._generate_timestamp(days_back=random.randint(1, 5))
        })
        
        # Generate intermediate points
        for i in range(1, num_points - 1):
            # Interpolate between origin and destination
            ratio = i / (num_points - 1)
            lat = origin_coords[0] + (dest_coords[0] - origin_coords[0]) * ratio
            lng = origin_coords[1] + (dest_coords[1] - origin_coords[1]) * ratio
            
            # Add some randomness to make it look like a real route
            lat += random.uniform(-0.5, 0.5)
            lng += random.uniform(-0.5, 0.5)
            
            route_points.append({
                "lat": round(lat, 6),
                "lng": round(lng, 6),
                "timestamp": self._generate_timestamp(days_back=random.randint(0, 4))
            })
        
        # Add destination (only if shipment has reached it)
        route_points.append({
            "lat": dest_coords[0],
            "lng": dest_coords[1],
            "timestamp": self._generate_timestamp(days_back=random.randint(0, 2))
        })
        
        return route_points

    def _generate_streaming_shipment(self):
        """Generate a new shipment and append to shipments.csv"""
        # Check if shipments.csv exists, if not, generate initial shipments
        shipment_path = os.path.join(self.output_dir, "shipments", "shipments.csv")
        if not os.path.exists(shipment_path):
            self.generate_shipments(10)
            return
            
        # Read existing shipments to avoid ID conflicts
        existing_shipments = self._read_csv(shipment_path)
        
        # Find the highest ID number
        max_id = 0
        for shipment in existing_shipments:
            if shipment["id"].startswith("SH"):
                try:
                    id_num = int(shipment["id"][2:])
                    max_id = max(max_id, id_num)
                except ValueError:
                    pass
        
        # Create a new shipment with the next ID
        new_id = f"SH{max_id + 1:04d}"
        
        # Define possible values for shipment properties
        statuses = ["scheduled", "in_transit"]
        cargo_types = ["general", "perishable", "hazardous", "fragile", "oversized"]
        cities = [
            "New York, NY", "Los Angeles, CA", "Chicago, IL", "Houston, TX", "Phoenix, AZ",
            "Philadelphia, PA", "San Antonio, TX", "San Diego, CA", "Dallas, TX", "San Jose, CA"
        ]
        
        # Generate random origin and destination
        origin = random.choice(cities)
        destination = random.choice([city for city in cities if city != origin])
        
        # Generate timestamps
        created_at = datetime.datetime.now().isoformat()
        estimated_delivery = self._generate_timestamp(days_ahead=random.randint(1, 10))
        
        # Generate cargo information
        cargo = {
            "type": random.choice(cargo_types),
            "weight": round(random.uniform(100, 5000), 2),
            "volume": round(random.uniform(1, 100), 2),
            "value": round(random.uniform(500, 50000), 2),
            "temperature_controlled": random.random() < 0.3,
            "hazardous": random.random() < 0.15
        }
        
        # Create the new shipment
        new_shipment = {
            "id": new_id,
            "status": random.choice(statuses),
            "origin": origin,
            "destination": destination,
            "cargo": json.dumps(cargo),  # Convert to JSON string for CSV
            "driver_id": random.choice(self.driver_ids) if self.driver_ids else f"D{random.randint(1, 20):03d}",
            "vehicle_id": random.choice(self.vehicle_ids) if self.vehicle_ids else f"V{random.randint(1, 20):03d}",
            "route": json.dumps(self._generate_route_points(origin, destination)),  # Convert to JSON string for CSV
            "estimated_delivery": estimated_delivery,
            "actual_delivery": "",
            "anomalies": json.dumps([]),  # Empty anomalies initially
            "created_at": created_at,
            "last_updated": created_at
        }
        
        # Append to CSV
        self._append_csv(shipment_path, [new_shipment])
        print(f"Generated new shipment: {new_id} - From {origin} to {destination}")

    def _update_random_shipment_status(self):
        """Update a random shipment's status and potentially add anomalies"""
        # Read existing shipments
        shipment_path = os.path.join(self.output_dir, "shipments", "shipments.csv")
        if not os.path.exists(shipment_path):
            self.generate_shipments(10)
            return
            
        shipments = self._read_csv(shipment_path)
        if not shipments:
            return
        
        # Filter for shipments that are not delivered or cancelled
        active_shipments = [s for s in shipments if s["status"] not in ["delivered", "cancelled"]]
        if not active_shipments:
            return
        
        # Select a random shipment to update
        shipment_index = random.randint(0, len(active_shipments) - 1)
        shipment = active_shipments[shipment_index]
        
        # Find the index in the original list
        original_index = shipments.index(shipment)
        
        # Get current status
        current_status = shipment["status"]
        
        # Determine new status based on current status
        if current_status == "scheduled":
            new_status = "in_transit"
        elif current_status == "in_transit":
            new_status = random.choice(["in_transit", "in_transit", "delayed", "delivered"])
        elif current_status == "delayed":
            new_status = random.choice(["delayed", "in_transit", "delivered"])
        else:
            new_status = current_status
        
        # Update the shipment's status
        shipments[original_index]["status"] = new_status
        shipments[original_index]["last_updated"] = datetime.datetime.now().isoformat()
        
        # If delivered, set actual delivery date
        if new_status == "delivered" and not shipments[original_index]["actual_delivery"]:
            shipments[original_index]["actual_delivery"] = datetime.datetime.now().isoformat()
        
        # Chance to add an anomaly (20% chance if not already delivered)
        if new_status != "delivered" and random.random() < 0.2:
            # Parse existing anomalies
            try:
                anomalies = json.loads(shipments[original_index]["anomalies"])
            except (json.JSONDecodeError, TypeError):
                anomalies = []
            
            # Generate a new anomaly
            anomaly_types = [
                "route_deviation", "unusual_stop", "speed_violation", "potential_fraud", 
                "delay", "temperature_breach", "cargo_tampering", "unscheduled_maintenance"
            ]
            anomaly_type = random.choice(anomaly_types)
            
            new_anomaly = {
                "type": anomaly_type,
                "detected_at": datetime.datetime.now().isoformat(),
                "severity": random.choice(["low", "medium", "high"]),
                "description": self._generate_anomaly_description(anomaly_type),
                "location": f"{random.uniform(25, 48):.6f},{random.uniform(-125, -70):.6f}" if anomaly_type != "temperature_breach" else "",
                "resolved": False
            }
            
            anomalies.append(new_anomaly)
            shipments[original_index]["anomalies"] = json.dumps(anomalies)
            
            # If it's a severe anomaly, update status to delayed
            if new_anomaly["severity"] == "high" and new_status != "delivered":
                shipments[original_index]["status"] = "delayed"
                new_status = "delayed"
        
        # Write back to CSV
        self._write_csv(shipment_path, shipments)
        print(f"Updated shipment {shipment['id']} status: {current_status} -> {new_status}")

    def _generate_streaming_invoice(self):
        """Generate a new invoice and append to invoices.csv"""
        # Check if invoices.csv exists, if not, generate initial invoices
        invoice_path = os.path.join(self.output_dir, "invoices", "invoices.csv")
        if not os.path.exists(invoice_path):
            self.generate_invoices(5)
            return
        
        # Read existing invoices to avoid ID conflicts
        existing_invoices = self._read_csv(invoice_path)
        
        # Find the highest ID number
        max_id = 0
        for invoice in existing_invoices:
            if invoice["id"].startswith("INV"):
                try:
                    id_num = int(invoice["id"][3:])
                    max_id = max(max_id, id_num)
                except ValueError:
                    pass
        
        # Create a new invoice with the next ID
        new_id = f"INV{max_id + 1:05d}"
        
        # Generate random amount
        amount = round(random.uniform(500, 10000), 2)
        
        # Generate dates
        issue_date = datetime.datetime.now().isoformat()
        
        # Determine payment terms and due date
        term = random.choice(["Net 30", "Net 60", "Net 15", "Due on Receipt"])
        if term == "Net 30":
            days_to_add = 30
        elif term == "Net 60":
            days_to_add = 60
        elif term == "Net 15":
            days_to_add = 15
        else:  # Due on Receipt
            days_to_add = 0
            
        due_date = (datetime.datetime.now() + datetime.timedelta(days=days_to_add)).isoformat()
        
        # Generate line items
        line_items = []
        num_items = random.randint(1, 5)
        for j in range(num_items):
            quantity = random.randint(1, 10)
            unit_price = round(random.uniform(50, 1000), 2)
            line_items.append({
                "description": random.choice(["Freight delivery", "Express shipping", "Warehousing", "Packaging", "Handling fee"]),
                "quantity": quantity,
                "unit_price": unit_price,
                "amount": round(quantity * unit_price, 2)
            })
        
        # Calculate total from line items
        total_amount = sum(item["amount"] for item in line_items)
        
        # Create the new invoice
        new_invoice = {
            "id": new_id,
            "order_id": f"ORD{random.randint(10000, 99999)}",
            "customer_id": f"CUST{random.randint(100, 999)}",
            "amount": round(total_amount, 2),
            "currency": "USD",
            "issue_date": issue_date,
            "due_date": due_date,
            "payment_terms": term,
            "early_payment_discount": round(random.uniform(0, 5), 2) if random.random() < 0.3 else 0,
            "late_payment_fee": round(random.uniform(1, 10), 2) if random.random() < 0.5 else 0,
            "status": "issued",
            "payment_date": "",
            "payment_method": "",
            "line_items": json.dumps(line_items),  # Convert to JSON string for CSV
            "notes": "",
            "compliance_flags": json.dumps([]) if random.random() < 0.8 else json.dumps([random.choice(["missing_po", "incorrect_amount", "late_submission"])]),
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        # Append to CSV
        self._append_csv(invoice_path, [new_invoice])
        print(f"Generated new invoice: {new_id} - Amount: ${total_amount:.2f}, Due: {due_date}")

    def _generate_timestamp(self, days_back=0, days_ahead=0):
        """Generate a timestamp in ISO format.

        Args:
            days_back: Number of days in the past
            days_ahead: Number of days in the future

        Returns:
            ISO formatted timestamp string
        """
        if days_back > 0:
            dt = datetime.datetime.now() - datetime.timedelta(days=days_back)
        elif days_ahead > 0:
            dt = datetime.datetime.now() + datetime.timedelta(days=days_ahead)
        else:
            dt = datetime.datetime.now()
            
        return dt.isoformat()

    def _write_csv(self, filepath, data):
        """Write data to a CSV file.

        Args:
            filepath: Path to the CSV file
            data: List of dictionaries to write
        """
        if not data:
            return
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Get fieldnames from the first item
        fieldnames = list(data[0].keys())
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def _append_csv(self, filepath, data):
        """Append data to a CSV file.

        Args:
            filepath: Path to the CSV file
            data: List of dictionaries to append
        """
        if not data:
            return
            
        # Check if file exists
        file_exists = os.path.isfile(filepath)
        
        # If file doesn't exist, write with header
        if not file_exists:
            return self._write_csv(filepath, data)
        
        # Get fieldnames from the first item
        fieldnames = list(data[0].keys())
        
        # Read existing file to get fieldnames
        if file_exists:
            with open(filepath, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                existing_fieldnames = next(reader, None)
                
            # If fieldnames don't match, rewrite the file
            if existing_fieldnames and set(fieldnames) != set(existing_fieldnames):
                existing_data = self._read_csv(filepath)
                combined_data = existing_data + data
                return self._write_csv(filepath, combined_data)
        
        # Append to file
        with open(filepath, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerows(data)

    def _read_csv(self, filepath):
        """Read data from a CSV file.

        Args:
            filepath: Path to the CSV file

        Returns:
            List of dictionaries with the CSV data
        """
        if not os.path.isfile(filepath):
            return []
            
        data = []
        with open(filepath, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
                
        return data


def main():
    """Main function to run the data generator."""
    parser = argparse.ArgumentParser(description='Generate sample data for the logistics system')
    parser.add_argument('--output-dir', default='data/streams', help='Directory to write generated data files')
    parser.add_argument('--drivers', type=int, default=20, help='Number of drivers to generate')
    parser.add_argument('--vehicles', type=int, default=20, help='Number of vehicles to generate')
    parser.add_argument('--incidents', type=int, default=50, help='Number of incidents to generate')
    parser.add_argument('--invoices', type=int, default=30, help='Number of invoices to generate')
    parser.add_argument('--shipments', type=int, default=40, help='Number of shipments to generate')
    parser.add_argument('--stream', action='store_true', help='Generate streaming data')
    parser.add_argument('--interval', type=int, default=5, help='Seconds between streaming data generation')
    parser.add_argument('--count', type=int, default=10, help='Number of streaming data iterations')
    
    args = parser.parse_args()
    
    generator = DataGenerator(output_dir=args.output_dir)
    
    print("Generating initial data...")
    generator.generate_drivers(args.drivers)
    generator.generate_vehicles(args.vehicles)
    generator.generate_incidents(args.incidents)
    generator.generate_invoices(args.invoices)
    generator.generate_shipments(args.shipments)
    
    if args.stream:
        generator.generate_streaming_data(args.interval, args.count)


if __name__ == "__main__":
    main()