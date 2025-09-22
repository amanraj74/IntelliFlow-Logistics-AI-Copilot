#!/usr/bin/env python3
"""
Migration script to update IntelliFlow project with Pathway integration
This script helps you integrate all the new Pathway components into your existing project
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

class PathwayMigration:
    """Migrate existing IntelliFlow project to use Pathway"""
    
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_original"
    
    def print_step(self, step, description):
        print(f"\n{'='*50}")
        print(f"STEP {step}: {description}")
        print(f"{'='*50}")
    
    def backup_original_files(self):
        """Backup original files before modification"""
        self.print_step(1, "Backing up original files")
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # Files to backup
        files_to_backup = [
            "backend/api/routers/ai_query.py",
            "requirements.txt",
            "docker-compose.yml",
            "Dockerfile"
        ]
        
        for file_path in files_to_backup:
            source = self.project_root / file_path
            if source.exists():
                dest = self.backup_dir / file_path
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
                print(f"✅ Backed up: {file_path}")
        
        print(f"✅ Backup completed in: {self.backup_dir}")
    
    def create_directory_structure(self):
        """Create new directory structure"""
        self.print_step(2, "Creating directory structure")
        
        directories = [
            "backend/pathway",
            "backend/rag", 
            "data/streams/drivers",
            "data/streams/shipments",
            "data/streams/incidents",
            "data/processed",
            "cache/pathway_storage",
            "scripts"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {directory}")
    
    def update_api_main(self):
        """Update the main API file to use new router"""
        self.print_step(3, "Updating API main file")
        
        main_py_path = self.project_root / "backend/api/main.py"
        
        if main_py_path.exists():
            with open(main_py_path, 'r') as f:
                content = f.read()
            
            # Update import
            if "ai_query" in content and "ai_query_pathway" not in content:
                content = content.replace(
                    "from backend.api.routers import drivers, incidents, alerts, ai_query",
                    "from backend.api.routers import drivers, incidents, alerts\nfrom backend.api.routers import ai_query_pathway as ai_query"
                )
                
                with open(main_py_path, 'w') as f:
                    f.write(content)
                
                print("✅ Updated backend/api/main.py import")
            else:
                print("⚠️ API main file already updated or not found")
        else:
            print("⚠️ backend/api/main.py not found")
    
    def create_env_files(self):
        """Create environment configuration files"""
        self.print_step(4, "Creating environment files")
        
        # .env file
        env_content = """# IntelliFlow Logistics AI Configuration
ENVIRONMENT=development
API_PORT=9000
PATHWAY_CACHE=./cache/pathway_storage
PATHWAY_PERSISTENT_STORAGE=./data/pathway_storage
PYTHONPATH=.
DEBUG=True
"""
        
        env_path = self.project_root / ".env"
        if not env_path.exists():
            with open(env_path, 'w') as f:
                f.write(env_content)
            print("✅ Created .env file")
        else:
            print("⚠️ .env file already exists")
        
        # Streamlit secrets
        streamlit_dir = self.project_root / ".streamlit"
        streamlit_dir.mkdir(exist_ok=True)
        
        secrets_content = 'API_BASE = "http://localhost:9000"\n'
        secrets_path = streamlit_dir / "secrets.toml"
        
        with open(secrets_path, 'w') as f:
            f.write(secrets_content)
        print("✅ Created .streamlit/secrets.toml")
    
    def create_startup_scripts(self):
        """Create startup scripts"""
        self.print_step(5, "Creating startup scripts")
        
        # Backend startup script
        backend_script = """#!/bin/bash
echo "🚀 Starting IntelliFlow Backend with Pathway..."

# Check if virtual environment exists
if [ -d "pathway_env" ]; then
    source pathway_env/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

export PYTHONPATH=.
export PATHWAY_CACHE=./cache/pathway_storage

# Start Pathway pipeline in background
echo "Starting Pathway streaming pipeline..."
python -m backend.pathway.streaming_pipeline &
PIPELINE_PID=$!

# Wait a moment for pipeline to initialize
sleep 3

# Start FastAPI server
echo "Starting FastAPI server..."
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 9000 --reload &
API_PID=$!

echo "Backend started!"
echo "Pipeline PID: $PIPELINE_PID"
echo "API PID: $API_PID"
echo "API available at: http://localhost:9000"
echo "Press Ctrl+C to stop"

# Wait for interrupt
trap 'echo "Stopping services..."; kill $PIPELINE_PID $API_PID 2>/dev/null; exit' INT
wait
"""
        
        # Frontend startup script
        frontend_script = """#!/bin/bash
echo "🎨 Starting IntelliFlow Frontend..."

# Check if virtual environment exists
if [ -d "pathway_env" ]; then
    source pathway_env/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

export PYTHONPATH=.
streamlit run frontend/dashboard.py --server.port=8501 --server.address=0.0.0.0
"""
        
        # Demo data script
        demo_script = """#!/bin/bash
echo "📊 Generating demo data..."

# Check if virtual environment exists
if [ -d "pathway_env" ]; then
    source pathway_env/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate  
elif [ -d "env" ]; then
    source env/bin/activate
fi

export PYTHONPATH=.

# Check if demo script exists
if [ -f "scripts/generate_demo_data.py" ]; then
    python scripts/generate_demo_data.py --mode scenario
    echo "Demo data generated! Check data/streams/ folder"
else
    echo "Demo data generator not found. Creating basic demo data..."
    
    # Create basic demo data
    mkdir -p data/streams/drivers data/streams/incidents
    
    echo "id,name,license_number,risk_score,experience_years,created_at,status
D001,Aman Singh,DL12-3456,0.25,5,$(date -Iseconds),active
D002,Priya Verma,DL34-7890,0.75,3,$(date -Iseconds),active
D003,Rajesh Kumar,DL56-1234,0.95,2,$(date -Iseconds),active" > data/streams/drivers/demo_drivers.csv
    
    echo '{"id": "INC001", "driver_id": "D003", "description": "Speed violation detected", "severity": "high", "date": "'$(date -Iseconds)'", "location": "Highway NH-1", "resolved": false}
{"id": "INC002", "driver_id": "D002", "description": "Late delivery", "severity": "medium", "date": "'$(date -Iseconds)'", "location": "Delhi", "resolved": false}' > data/streams/incidents/demo_incidents.jsonl
    
    echo "Basic demo data created!"
fi
"""
        
        # Write scripts
        scripts = {
            "start-backend.sh": backend_script,
            "start-frontend.sh": frontend_script,
            "generate-demo.sh": demo_script
        }
        
        for script_name, script_content in scripts.items():
            script_path = self.project_root / script_name
            with open(script_path, 'w') as f:
                f.write(script_content)
            # Make executable
            os.chmod(script_path, 0o755)
            print(f"✅ Created: {script_name}")
    
    def update_requirements(self):
        """Update requirements.txt with Pathway dependencies"""
        self.print_step(6, "Updating requirements")
        
        pathway_requirements = """
# Pathway framework (Linux/WSL only)
pathway>=0.7.0

# Optional ML dependencies
sentence-transformers>=2.2.2
scikit-learn>=1.5.2

# Additional dependencies for real-time features
websockets>=11.0
"""
        
        # Check if we're in WSL/Linux
        if os.name == 'posix':
            # Linux/WSL - add Pathway
            req_path = self.project_root / "requirements-pathway.txt"
            original_req = self.project_root / "requirements.txt"
            
            # Copy original requirements
            if original_req.exists():
                shutil.copy2(original_req, req_path)
            
            # Append Pathway requirements
            with open(req_path, 'a') as f:
                f.write(pathway_requirements)
            
            print("✅ Created requirements-pathway.txt for Linux/WSL")
        else:
            print("⚠️ Windows detected - Pathway requirements not added to main file")
            print("   Use WSL for Pathway features")
    
    def create_readme_update(self):
        """Create updated README section"""
        self.print_step(7, "Creating README update")
        
        readme_addition = """

## 🚀 Pathway Integration (NEW)

### Real-time Streaming with Pathway

This project now includes Pathway integration for real-time data processing:

#### Quick Start with Pathway (WSL/Linux)
```bash
# 1. Setup (one-time)
chmod +x setup-pathway.sh
./setup-pathway.sh

# 2. Generate demo data
./generate-demo.sh

# 3. Start backend (Pathway + API)
./start-backend.sh

# 4. Start frontend
./start-frontend.sh

# 5. Open dashboard
open http://localhost:8501
```

#### Docker with Pathway
```bash
docker-compose -f docker-compose-pathway.yml up --build
```

#### Real-time Demo
1. Start all services
2. Add CSV/JSON files to `data/streams/` folders
3. Watch dashboard update automatically
4. Query AI copilot for real-time insights

### Architecture
```
Data Files → Pathway Streaming → Vector Store → AI Copilot
     ↓              ↓               ↓            ↓
Live Updates   Real-time ETL   Dynamic Index  Live Responses
```

**Requirements Met:**
- ✅ Pathway-powered streaming ETL
- ✅ Dynamic indexing (no rebuilds)
- ✅ Live retrieval/generation interface
- ✅ Real-time updates (T+0 to T+1)

"""
        
        readme_path = self.project_root / "README-PATHWAY.md"
        with open(readme_path, 'w') as f:
            f.write(readme_addition)
        
        print("✅ Created README-PATHWAY.md")
    
    def run_migration(self):
        """Run complete migration"""
        print("🚛 IntelliFlow Pathway Migration")
        print("================================")
        print("This will update your project with Pathway integration")
        
        # Confirm before proceeding
        response = input("\nContinue with migration? (y/N): ").lower().strip()
        if response != 'y':
            print("Migration cancelled")
            return False
        
        try:
            self.backup_original_files()
            self.create_directory_structure()
            self.update_api_main()
            self.create_env_files()
            self.create_startup_scripts()
            self.update_requirements()
            self.create_readme_update()
            
            print(f"\n{'='*50}")
            print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
            print(f"{'='*50}")
            
            print("\n🎯 Next Steps:")
            print("1. Run in WSL/Linux: ./setup-pathway.sh")
            print("2. Generate demo data: ./generate-demo.sh")
            print("3. Start backend: ./start-backend.sh")
            print("4. Start frontend: ./start-frontend.sh")
            print("5. Open: http://localhost:8501")
            
            print("\n📁 New Files Created:")
            print("- start-backend.sh, start-frontend.sh, generate-demo.sh")
            print("- .env, .streamlit/secrets.toml")
            print("- requirements-pathway.txt")
            print("- README-PATHWAY.md")
            
            print(f"\n💾 Backups saved in: {self.backup_dir}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            return False

def main():
    migration = PathwayMigration()
    success = migration.run_migration()
    
    if success:
        print("\n🎉 Your project is ready for Pathway integration!")
    else:
        print("\n⚠️ Migration failed. Check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())