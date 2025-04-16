import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_data():
    try:
        # Load only necessary columns
        columns = [
            'Incident Datetime',
            'Incident Day of Week',
            'Incident Category',
            'Police District',
            'Latitude',
            'Longitude'
        ]
        
        df = pd.read_parquet(
            "data/SFPD_Incidents_2021_to_Present_Reduced.parquet",
            columns=columns
        )
        
        # Standardize column names
        column_mapping = {
            'Incident Datetime': 'Datetime',
            'Incident Day of Week': 'Day',
            'Incident Category': 'Category',
            'Police District': 'District'
        }
        df = df.rename(columns=column_mapping)
        
        # Convert and extract datetime fields
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df['Hour'] = df['Datetime'].dt.hour.astype('int8')
        df['Month'] = df['Datetime'].dt.month.astype('int8')
        df['Day'] = df['Day'].str.capitalize()
        
        # Filter valid coordinates
        df = df[
            df['Latitude'].between(-90, 90) & 
            df['Longitude'].between(-180, 180)
        ].copy()
        
        # Optimize data types
        df['Day'] = df['Day'].astype('category')
        df['Category'] = df['Category'].astype('category')
        df['District'] = df['District'].astype('category')
        df['Latitude'] = df['Latitude'].astype('float32')
        df['Longitude'] = df['Longitude'].astype('float32')
        
        return df
    
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise

def get_top_districts(df, top_n=5):
    return df["District"].value_counts().head(top_n).to_dict()

def prepare_heatmap_data(df, sample_size=10000):
    try:
        if df.empty:
            logger.warning("Empty DataFrame received for heatmap")
            return []
            
        # Get recent data (3 months or fallback to 6 months)
        current_date = pd.Timestamp.now()
        date_threshold = current_date - relativedelta(months=3)
        recent_df = df[df['Datetime'] >= date_threshold].copy()
        
        if len(recent_df) < 1000:  # Fallback to 6 months if not enough data
            date_threshold = current_date - relativedelta(months=6)
            recent_df = df[df['Datetime'] >= date_threshold].copy()
            logger.info(f"Using 6 months data (count: {len(recent_df)})")
        
        if len(recent_df) < 500:  # Final fallback to 1 year
            date_threshold = current_date - relativedelta(months=12)
            recent_df = df[df['Datetime'] >= date_threshold].copy()
            logger.info(f"Using 12 months data (count: {len(recent_df)})")
        
        # If still too large, sample it
        if len(recent_df) > 50000:
            recent_df = recent_df.sample(n=50000, random_state=42)
            logger.info(f"Sampled 50,000 records from {len(recent_df)} total")
        
        # Round coordinates to reduce points
        recent_df = recent_df.assign(
            lat_round=recent_df['Latitude'].round(3),
            lng_round=recent_df['Longitude'].round(3)
        )
        
        # Aggregate data
        heatmap_df = recent_df.groupby(
            ['lat_round', 'lng_round', 'District', 'Category'],
            observed=True
        ).agg({
            'Latitude': 'mean',
            'Longitude': 'mean',
            'Datetime': 'count'
        }).rename(columns={'Datetime': 'count'}).reset_index()
        
        # Calculate percentiles
        if len(heatmap_df) > 0:
            counts = heatmap_df['count'].values
            p70 = np.percentile(counts, 70)
            p90 = np.percentile(counts, 90)
        else:
            p70, p90 = 1, 2
            
        # Prepare final data
        heatmap_data = []
        for _, row in heatmap_df.iterrows():
            if row['count'] >= p90:
                color = "#ff4444"  # Red
                radius = 8
            elif row['count'] >= p70:
                color = "#ffbb33"  # Yellow
                radius = 6
            else:
                color = "#00C851"  # Green
                radius = 4
                
            heatmap_data.append({
                "lat": float(row["Latitude"]),
                "lng": float(row["Longitude"]),
                "color": color,
                "radius": radius,
                "district": str(row["District"]),
                "category": str(row["Category"]),
                "count": int(row["count"])
            })
        
        return heatmap_data[:sample_size]
        
    except Exception as e:
        logger.error(f"Heatmap processing error: {e}")
        return []

def generate_graph_data(df):
    try:
        # Calculate averages
        hourly_avg = df.groupby("Hour", observed=True).size() / df['Datetime'].dt.date.nunique()
        daily_avg = df.groupby("Day", observed=True).size() / (df['Datetime'].dt.isocalendar().week.nunique())
        monthly_avg = df.groupby("Month", observed=True).size() / df['Datetime'].dt.year.nunique()

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



def get_top_districts(df, top_n=5):
    return df["District"].value_counts().head(top_n).to_dict()



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