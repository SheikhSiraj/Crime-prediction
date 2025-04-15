import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    try:
        df = pd.read_csv("data/SFPD_Incidents_2021_to_Present_Reduced.csv")
        
        # Standardize column names
        column_mapping = {
            'Incident Day of Week': 'Day',
            'Incident Datetime': 'Datetime',
            'Incident Date': 'Date',
            'Incident Category': 'Category',
            'Police District': 'District',
            'Analysis Neighborhood': 'Neighborhood',
            'Latitude': 'Latitude',
            'Longitude': 'Longitude'
        }
        
        # Rename columns to standard names
        df = df.rename(columns={k:v for k,v in column_mapping.items() if k in df.columns})
        
        # Convert datetime string to datetime object
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        
        # Extract Hour and Month from Datetime
        df['Hour'] = df['Datetime'].dt.hour
        df['Month'] = df['Datetime'].dt.month
        
        # Standardize day names
        df['Day'] = df['Day'].str.capitalize()
        
        # Check if we have required columns
        required_columns = ["Day", "Hour", "Month", "Latitude", "Longitude", "District", "Category"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns after processing: {missing_cols}")
            
        # Ensure we have the required columns
        df = df.dropna(subset=required_columns)
        
        # Convert to proper types
        df['Hour'] = df['Hour'].astype(int)
        df['Month'] = df['Month'].astype(int)
        
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def get_top_districts(df, top_n=5):
    return df["District"].value_counts().head(top_n).to_dict()

def prepare_heatmap_data(df, sample_size=5000):
    try:
        # Keep only recent 3 months data
        recent_date = df['Datetime'].max() - pd.DateOffset(months=3)
        df = df[df['Datetime'] >= recent_date]

        # Calculate absolute counts instead of ratios
        district_counts = df["District"].value_counts()
        max_count = district_counts.max()
        
        heatmap_data = []
        for _, row in df.iterrows():
            count = district_counts.get(row["District"], 0)
            
            # Dynamic color and size based on absolute counts
            if count > max_count * 0.2:
                color = "#ff4444"  # Red
                radius = 10
            elif count > max_count * 0.1:
                color = "#ffbb33"  # Yellow
                radius = 7
            else:
                color = "#00C851"  # Green
                radius = 5

            heatmap_data.append({
                "lat": row["Latitude"],
                "lng": row["Longitude"],
                "color": color,
                "radius": radius,
                "district": row["District"],
                "category": row["Category"],
                "datetime": str(row["Datetime"]),
                "count": count
            })
            
        return heatmap_data
    except Exception as e:
        logger.error(f"Heatmap error: {e}")
        raise



def generate_graph_data(df):
    try:
        # Calculate averages instead of totals
        
        # Hourly average (across all days)
        hourly_avg = df.groupby("Hour").size() / df['Datetime'].dt.date.nunique()
        
        # Daily average (across all weeks)
        daily_avg = df.groupby("Day").size() / (df['Datetime'].dt.isocalendar().week.nunique())
        
        # Monthly average (across all years)
        monthly_avg = df.groupby("Month").size() / df['Datetime'].dt.year.nunique()

        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                      "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        return {
            "hourly": {
                "labels": [f"{h}:00" for h in range(24)],
                "data": [round(hourly_avg.get(h, 0), 1) for h in range(24)]
            },
            "daily": {
                "labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "data": [round(daily_avg.get(day, 0), 1) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
            },
            "monthly": {
                "labels": month_names,
                "data": [round(monthly_avg.get(m, 0), 1) for m in range(1,13)]
            }
        }
    except Exception as e:
        logger.error(f"Error generating graph data: {e}")
        raise
    try:
        # Calculate averages instead of totals
        
        # Hourly average (across all days)
        hourly_avg = df.groupby("Hour").size() / df['Datetime'].dt.date.nunique()
        
        # Daily average (across all weeks)
        daily_avg = df.groupby("Day").size() / (df['Datetime'].dt.isocalendar().week.nunique())
        
        # Monthly average (across all years)
        monthly_avg = df.groupby("Month").size() / df['Datetime'].dt.year.nunique()

        return {
            "hourly": {
                "labels": [f"{h}:00" for h in range(24)],
                "data": [round(hourly_avg.get(h, 0), 1) for h in range(24)]
            },
            "daily": {
                "labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                "data": [round(daily_avg.get(day, 0), 1) for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]]
            },
            "monthly": {
                "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                "data": [round(monthly_avg.get(m, 0), 1) for m in range(1,13)]
            }
        }
    except Exception as e:
        logger.error(f"Error generating graph data: {e}")
        raise
    try:
        # Hourly data
        hourly_counts = df.groupby("Hour").size()
        hourly_counts = hourly_counts.reindex(range(24), fill_value=0)
        
        # Daily data
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        daily_counts = df["Day"].value_counts().reindex(day_order, fill_value=0)
        
        # Monthly data
        monthly_counts = df.groupby("Month").size()
        monthly_counts = monthly_counts.reindex(range(1, 13), fill_value=0)
        
        return {
            "hourly": {
                "labels": [f"{h}:00" for h in hourly_counts.index],
                "data": hourly_counts.values.tolist()
            },
            "daily": {
                "labels": daily_counts.index.tolist(),
                "data": daily_counts.values.tolist()
            },
            "monthly": {
                "labels": [datetime(2021, m, 1).strftime('%b') for m in monthly_counts.index],
                "data": monthly_counts.values.tolist()
            }
        }
    except Exception as e:
        logger.error(f"Error generating graph data: {e}")
        raise



def prepare_heatmap_data(df, sample_size=5000):
    try:
        # Filter recent 3 months data
        recent_date = df['Datetime'].max() - pd.DateOffset(months=3)
        recent_df = df[df['Datetime'] >= recent_date].copy()
        
        # Group by location and count incidents
        heatmap_df = recent_df.groupby(['Latitude', 'Longitude', 'District', 'Category'])\
                             .size()\
                             .reset_index(name='count')
        
        # Calculate percentiles for better color distribution
        percentiles = heatmap_df['count'].quantile([0.7, 0.9]).values
        
        heatmap_data = []
        for _, row in heatmap_df.iterrows():
            # Determine color and radius based on percentiles
            if row['count'] >= percentiles[1]:  # Top 10%
                color = "#ff4444"  # Red
                radius = 10
            elif row['count'] >= percentiles[0]:  # Top 30%
                color = "#ffbb33"  # Yellow
                radius = 7
            else:
                color = "#00C851"  # Green
                radius = 5
                
            heatmap_data.append({
                "lat": row["Latitude"],
                "lng": row["Longitude"],
                "color": color,
                "radius": radius,
                "district": row["District"],
                "category": row["Category"],
                "count": int(row["count"])
            })
            
        return heatmap_data[:sample_size]  # Return sampled data
    except Exception as e:
        logger.error(f"Heatmap error: {e}")
        return []  # Return empty list on error