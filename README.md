# *San Francisco Crime Analysis Dashboard*

## 📌 Overview

The San Francisco Crime Analysis Dashboard is a comprehensive web application that visualizes and analyzes crime patterns in San Francisco from 2021 to present. The dashboard provides interactive maps, statistical charts, and predictive insights to help understand crime trends across different districts and time periods.

## 🚀 Features

- **Interactive Crime Heatmap**: Visualize crime hotspots across San Francisco
- **Temporal Analysis**: View crime patterns by hour, day, and month
- **District Comparison**: Identify high-risk districts and neighborhoods
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Data Processing**: Dynamic filtering of recent crime data

## 🛠️ Technical Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Leaflet.js, Chart.js)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Leaflet (maps), Chart.js (graphs)
- **Data Storage**: Parquet file format

## 📂 Project Structure

```
sf-crime-dashboard/
├── app.py                # Flask application entry point
├── utils.py              # Data processing and utility functions
├── requirements.txt      # Python dependencies
├── data/
│   └── SFPD_Incidents_2021_to_Present_Reduced.parquet  # Crime dataset
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Main dashboard page
    ├── error.html        # Error page template
    └── partials/         # Template partials
        ├── header.html   # Header section
        └── footer.html   # Footer section
```

## ⚙️ Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sf-crime-dashboard.git
   cd sf-crime-dashboard
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Place your crime data file in the `data/` directory:
   ```
   data/SFPD_Incidents_2021_to_Present_Reduced.parquet
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the dashboard at:
   ```
   http://localhost:5000
   ```

## 📊 Data Processing

The application processes crime data with the following workflow:

1. **Data Loading**: Reads from Parquet file for efficient storage
2. **Data Cleaning**:
   - Standardizes column names
   - Filters invalid geographic coordinates
   - Handles missing values
3. **Feature Engineering**:
   - Extracts hour, day, and month from timestamps
   - Calculates crime frequencies
4. **Aggregation**:
   - Groups data by time periods and locations
   - Computes statistical summaries

## 🧪 Testing

To manually test the application:

1. Verify the home page loads correctly
2. Check that the map displays crime data points
3. Confirm all charts render properly
4. Test the heatmap data endpoint:
   ```bash
   curl http://localhost:5000/heatmap_data
   ```

## 🚨 Error Handling

The application includes comprehensive error handling:

- Invalid data formats
- Missing data files
- API request failures
- Geographic coordinate validation

Errors are logged and displayed to users with appropriate messages.

## 📈 Performance Considerations

1. **Data Optimization**:
   - Uses Parquet format for efficient storage
   - Implements memory-efficient data types
   - Samples large datasets when necessary

2. **Frontend Optimization**:
   - Implements marker clustering for map points
   - Uses canvas-based chart rendering
   - Implements lazy loading where possible

## ✅ Acknowledgments

- San Francisco Police Department for providing the crime data
- OpenStreetMap for base map tiles
- The open-source community for the libraries used in this project
