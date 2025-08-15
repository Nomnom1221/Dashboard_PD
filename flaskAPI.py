from flask import Flask, jsonify
import pandas as pd
import requests
from io import StringIO 

app = Flask(__name__)

# Function to fetch CSV data from GitHub
def fetch_csv_from_github(url):
    response = requests.get(url)
    # Assuming CSV is the response content
    return response.content

@app.route('/get_data')
def get_data():
    github_csv_url = "https://raw.githubusercontent.com/Nomnom1221/Sample/master/reneeDataset.csv"
    
    # Fetch CSV data
    csv_data = fetch_csv_from_github(github_csv_url)
    
    # Convert CSV data to DataFrame
    df = pd.read_csv(github_csv_url)
    
    # Convert DataFrame to JSON and return
    return jsonify(df.to_dict())
@app.route('/hello')
def hello_world():
    return "Paris data APi"

if __name__ == '__main__':
    app.run(debug=False)
