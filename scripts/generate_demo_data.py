#!/usr/bin/env python3
"""
Demo data generator for Pathway streaming pipeline
This script generates sample data files to demonstrate real-time updates
"""

import os
import json
import csv
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoDataGenerator:
    """Generate realistic demo data for logistics system"""
    
    def __init__(self, output_dir: str = "./data/streams"):
        self.output_dir = output_dir
        self.ensure_directories()
        
        # Sample data pools
        self.driver_names = [
            "Aman Singh", "Priya Sharma", "Rajesh Kumar", "Anita Patel", 
            "Vikram Gupta", "Sunita Verma", "Arjun Mehta", "Kavita Jain",
            "Rohit Agarwal", "Neha Reddy", "Suresh Yadav", "Pooja Mishra"
        ]
        
        self.cities = [
            "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", 
            "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
        ]
        
        self.cargo_types = [
            "Electronics", "Pharmaceuticals", "Automotive Parts", "Textiles",
            "Food Items", "Machinery", "Chemicals", "Consumer Goods"
        ]
        
        self.incident_types = [
            "Harsh braking detected", "Speed limit violation", "Route deviation",
            "Late delivery", "Vehicle breakdown", "Traffic violation",
            "Fuel efficiency concern", "Customer complaint"
        ]
    
    def ensure_directories(self):
        """Create necessary directories"""
        dirs = [
            f"{self.output_dir}/drivers",
            f"{self.output_dir}/shipments", 
            f"{self.output_dir}/incidents"
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
    
    def generate_drivers(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate driver data"""
        drivers = []
        for i in range(count):
            driver = {
                "id": f"D{i+1:03d}",
                "name": self.driver_names[i % len(self.driver_names)],
                "license_number": f"DL{random.randint(10,99)}{random.randint(1000,9999)}",
                "risk_score": round(random.uniform(0.1, 0.8), 2),
                "experience_years": random.randint(2, 15),
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            drivers.append(driver)
        return drivers
    
    def generate_shipments(self, driver_count: int = 5, shipment_count: int = 8) -> List[Dict[str, Any]]:
        """Generate shipment data"""
        shipments = []
        statuses = ["in_transit", "delivered", "delayed", "cancelled"]
        
        for i in range(shipment_count):
            origin = random.choice(self.cities)
            destination = random.choice([c for c in self.cities if c != origin])
            
            shipment = {
                "id": f"SHP{i+1:04d}",
                "driver_id": f"D{random.randint(1, driver_count):03d}",
                "status": random.choice(statuses),
                "origin": origin,
                "destination": destination,
                "cargo_type": random.choice(self.cargo_types),
                "cargo_weight": random.randint(500, 5000),
                "cargo_value": random.randint(10000, 500000),
                "created_at": (datetime.now() - timedelta(days=random.randint(0, 5))).isoformat(),
                "expected_delivery": (datetime.now() + timedelta(days=random.randint(1, 3))).isoformat(),
                "priority": random.choice(["low", "medium", "high"])
            }
            shipments.append(shipment)
        return shipments
    
    def generate_incidents(self, driver_count: int = 5, incident_count: int = 6) -> List[Dict[str, Any]]:
        """Generate incident data"""
        incidents = []
        severities = ["low", "medium", "high"]
        
        for i in range(incident_count):
            incident = {
                "id": f"INC{i+1:04d}",
                "driver_id": f"D{random.randint(1, driver_count):03d}",
                "description": random.choice(self.incident_types),
                "severity": random.choice(severities),
                "date": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
                "location": random.choice(self.cities),
                "resolved": random.choice([True, False]),
                "resolution_notes": "Investigation completed" if random.choice([True, False]) else ""
            }
            incidents.append(incident)
        return incidents
    
    def save_drivers_csv(self, drivers: List[Dict[str, Any]], filename: str = None):
        """Save drivers data as CSV"""
        if not filename:
            filename = f"drivers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = f"{self.output_dir}/drivers/{filename}"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if drivers:
                fieldnames = drivers[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(drivers)
        
        logger.info(f"Saved {len(drivers)} drivers to {filepath}")
        return filepath
    
    def save_jsonlines(self, data: List[Dict[str, Any]], filepath: str):
        """Save data as JSON Lines format"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item) + '\n')
        
        logger.info(f"Saved {len(data)} items to {filepath}")
        return filepath
    
    def generate_initial_data(self):
        """Generate initial data set"""
        logger.info("Generating initial demo data...")
        
        # Generate data
        drivers = self.generate_drivers(5)
        shipments = self.generate_shipments(5, 8)
        incidents = self.generate_incidents(5, 6)
        
        # Save data
        self.save_drivers_csv(drivers, "initial_drivers.csv")
        self.save_jsonlines(
            shipments, 
            f"{self.output_dir}/shipments/initial_shipments.jsonl"
        )
        self.save_jsonlines(
            incidents,
            f"{self.output_dir}/incidents/initial_incidents.jsonl"
        )
        
        logger.info("Initial data generation completed!")
        return {
            "drivers": len(drivers),
            "shipments": len(shipments), 
            "incidents": len(incidents)
        }
    
    def simulate_real_time_updates(self, duration_minutes: int = 10):
        """Simulate real-time data updates"""
        logger.info(f"Starting real-time simulation for {duration_minutes} minutes...")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        update_count = 0
        
        while datetime.now() < end_time:
            # Generate random updates
            update_type = random.choice(["driver", "shipment", "incident"])
            
            if update_type == "driver":
                # Add new driver or update existing
                new_driver = self.generate_drivers(1)[0]
                new_driver["id"] = f"D{random.randint(100, 999):03d}"
                self.save_drivers_csv([new_driver], f"driver_update_{update_count}.csv")
                
            elif update_type == "shipment":
                # Add new shipment
                new_shipment = self.generate_shipments(5, 1)[0]
                new_shipment["id"] = f"SHP{random.randint(1000, 9999):04d}"
                self.save_jsonlines(
                    [new_shipment], 
                    f"{self.output_dir}/shipments/shipment_update_{update_count}.jsonl"
                )
                
            elif update_type == "incident":
                # Add new incident
                new_incident = self.generate_incidents(5, 1)[0]
                new_incident["id"] = f"INC{random.randint(1000, 9999):04d}"
                new_incident["date"] = datetime.now().isoformat()
                self.save_jsonlines(
                    [new_incident],
                    f"{self.output_dir}/incidents/incident_update_{update_count}.jsonl"
                )
            
            update_count += 1
            logger.info(f"Generated update #{update_count}: {update_type}")
            
            # Wait before next update (5-15 seconds)
            time.sleep(random.randint(5, 15))
        
        logger.info(f"Real-time simulation completed. Generated {update_count} updates.")
    
    def generate_demo_scenario(self):
        """Generate a complete demo scenario"""
        logger.info("=== Starting Demo Scenario Generation ===")
        
        # Step 1: Generate initial data
        initial_stats = self.generate_initial_data()
        logger.info(f"Initial data: {initial_stats}")
        
        # Step 2: Wait a bit then generate updates
        logger.info("Waiting 10 seconds before starting updates...")
        time.sleep(10)
        
        # Step 3: Generate some immediate updates to show real-time capability
        logger.info("Generating immediate updates...")
        
        # High-risk driver alert
        high_risk_driver = {
            "id": "D999",
            "name": "Alert Driver",
            "license_number": "DL99ALERT",
            "risk_score": 0.95,
            "experience_years": 1,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        self.save_drivers_csv([high_risk_driver], "high_risk_alert.csv")
        
        # Critical incident
        critical_incident = {
            "id": "INC9999",
            "driver_id": "D999", 
            "description": "Speed violation and harsh braking detected",
            "severity": "high",
            "date": datetime.now().isoformat(),
            "location": "Highway NH-1",
            "resolved": False,
            "resolution_notes": ""
        }
        self.save_jsonlines(
            [critical_incident],
            f"{self.output_dir}/incidents/critical_incident.jsonl"
        )
        
        # Delayed shipment
        delayed_shipment = {
            "id": "SHP9999",
            "driver_id": "D999",
            "status": "delayed", 
            "origin": "Delhi",
            "destination": "Mumbai",
            "cargo_type": "High Value Electronics",
            "cargo_weight": 2000,
            "cargo_value": 750000,
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
            "expected_delivery": (datetime.now() + timedelta(hours=6)).isoformat(),
            "priority": "high"
        }
        self.save_jsonlines(
            [delayed_shipment],
            f"{self.output_dir}/shipments/delayed_shipment.jsonl"
        )
        
        logger.info("=== Demo Scenario Generation Completed ===")
        logger.info("Files generated in data/streams/ - Pathway pipeline should detect them!")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate demo data for Pathway logistics system')
    parser.add_argument('--mode', choices=['initial', 'realtime', 'scenario'], 
                       default='scenario', help='Data generation mode')
    parser.add_argument('--duration', type=int, default=10, 
                       help='Duration in minutes for realtime mode')
    
    args = parser.parse_args()
    
    generator = DemoDataGenerator()
    
    if args.mode == 'initial':
        generator.generate_initial_data()
    elif args.mode == 'realtime':
        generator.simulate_real_time_updates(args.duration)
    elif args.mode == 'scenario':
        generator.generate_demo_scenario()

if __name__ == "__main__":
    main()