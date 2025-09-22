import pandas as pd
from typing import Dict, List, Union, Any

def process_driver_data(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert driver data to pandas DataFrame for analysis."""
    return pd.DataFrame(data)

def process_incidents(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Convert incident data to pandas DataFrame for analysis."""
    return pd.DataFrame(data)

def calculate_risk_metrics(drivers_df: pd.DataFrame, incidents_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate risk metrics for drivers based on incidents."""
    # Merge driver and incident data
    metrics = drivers_df.copy()
    
    if not incidents_df.empty:
        incident_counts = incidents_df['driver_id'].value_counts()
        metrics['incident_count'] = metrics['id'].map(incident_counts).fillna(0)
        
        # Calculate risk score (example algorithm)
        metrics['risk_score'] = metrics.apply(
            lambda x: min(1.0, 0.1 * x['incident_count'] + float(x.get('risk_score', 0))),
            axis=1
        )
    
    return metrics

def format_alerts(alerts: List[Dict[str, Any]]) -> pd.DataFrame:
    """Format alerts data for display."""
    df = pd.DataFrame(alerts)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df.get('timestamp', pd.Timestamp.now()))
        df = df.sort_values('timestamp', ascending=False)
    return df

def analyze_trends(incidents_df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze incident trends over time."""
    if incidents_df.empty:
        return {"trend": "neutral", "stats": {}}
    
    incidents_df['date'] = pd.to_datetime(incidents_df['date'])
    daily_counts = incidents_df.resample('D', on='date').size()
    
    trend_stats = {
        "total_incidents": len(incidents_df),
        "daily_average": daily_counts.mean(),
        "trend": "increasing" if daily_counts.is_monotonic_increasing else "decreasing"
    }
    
    return trend_stats
