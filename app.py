from flask import Flask, render_template, request, jsonify
import pandas as pd
from utils import load_data, get_top_districts, prepare_heatmap_data, generate_graph_data
from datetime import datetime
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load and preprocess data
try:
    crime_df = load_data()
    logger.info(f"Data loaded successfully with {len(crime_df)} records")
except Exception as e:
    logger.error(f"Error loading data: {e}")
    raise

@app.route("/")
def index():
    try:
        # Top 5 dangerous districts
        top_districts = get_top_districts(crime_df)
        
        # Graph data
        graphs = generate_graph_data(crime_df)
        
        return render_template(
            "index.html",
            top_districts=top_districts,
            graphs=graphs,
            page_title="SF Crime Analysis Dashboard",
            current_year=datetime.now().year
        )
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template("error.html", error_message=str(e)), 500

@app.route("/heatmap_data")
def heatmap_data():
    try:
        heatmap_points = prepare_heatmap_data(crime_df)
        return jsonify(heatmap_points)
    except Exception as e:
        logger.error(f"Heatmap data error: {e}")
        return jsonify({"error": "Failed to load heatmap data"}), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error_message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_message="Internal server error"), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)