@echo off
echo Fixing Windows-specific issues...

REM Delete problematic secrets file
if exist ".streamlit\secrets.toml" del /f ".streamlit\secrets.toml"

REM Create .streamlit directory if it doesn't exist
if not exist ".streamlit" mkdir .streamlit

REM Create new secrets file with proper encoding
echo API_BASE = "http://localhost:8000" > .streamlit\secrets.toml

REM Create directories if they don't exist
if not exist "data\streams\drivers" mkdir data\streams\drivers
if not exist "data\streams\incidents" mkdir data\streams\incidents
if not exist "cache\pathway_storage" mkdir cache\pathway_storage

REM Create sample data files
echo id,name,license_number,risk_score > data\streams\drivers\drivers.csv
echo D001,Aman Singh,PB12-3456,0.12 >> data\streams\drivers\drivers.csv
echo D002,Priya Verma,PB09-7890,0.45 >> data\streams\drivers\drivers.csv
echo D003,Rajesh Kumar,HR05-1234,0.78 >> data\streams\drivers\drivers.csv

echo id,driver_id,date,severity,description,location > data\streams\incidents\incidents.csv
echo I1001,D001,2024-09-15,medium,Harsh braking detected,Highway NH-1 >> data\streams\incidents\incidents.csv
echo I1002,D002,2024-09-16,low,Late delivery due to traffic,Delhi NCR >> data\streams\incidents\incidents.csv
echo I1003,D003,2024-09-17,high,Speed limit violation,Mumbai >> data\streams\incidents\incidents.csv

echo Fixed! Now try running the services.
pause