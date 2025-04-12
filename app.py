from flask import Flask, jsonify, request, render_template, send_file
import requests
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# In-memory storage for location data
location_data = []

# Example configuration for target endpoints
TARGET_ENDPOINTS = {
    'users': 'https://jsonplaceholder.typicode.com/users',
    'posts': 'https://jsonplaceholder.typicode.com/posts',
    'comments': 'https://jsonplaceholder.typicode.com/comments'
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    global location_data
    data = request.json
    
    # Clear previous data
    location_data = []
    
    # Add timestamp to the data
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Store the new data
    location_data.append(data)
    
    return jsonify({'message': 'Data submitted successfully'})

@app.route('/data')
def view_data():
    return render_template('data.html', data=location_data)

@app.route('/export-csv')
def export_csv():
    if not location_data:
        return jsonify({'error': 'No data available to export'}), 404
    
    # Prepare data for CSV export
    export_data = []
    for item in location_data:
        # Safely get systemInfo fields with default values
        system_info = item.get('systemInfo', {})
        
        row = {
            'Business Types': ', '.join(item.get('currentBusinessTypes', [])),
            'App State': item.get('appState', ''),
            'System Info - IDFA': system_info.get('idfa', ''),
            'System Info - Region Code': system_info.get('regionCode', ''),
            'System Info - Timestamp': system_info.get('timestamp', ''),
            'System Info - Country Code': system_info.get('countryCode', ''),
            'System Info - Device ID': system_info.get('deviceId', ''),
            'System Info - Country ID': system_info.get('countryId', ''),
            'System Info - Platform': system_info.get('platform', ''),
            'System Info - Session ID': system_info.get('instashopSessionId', ''),
            'System Info - Language': system_info.get('lang', ''),
            'System Info - LVC': system_info.get('LVC', ''),
            'System Info - App Version': system_info.get('appVersion', ''),
            'System Info - Environment': system_info.get('environment', ''),
            'System Info - App Build': system_info.get('appBuild', ''),
            'System Info - Timezone': system_info.get('timezone', ''),
            'Longitude': item.get('longitude', ''),
            'Areas': ', '.join(item.get('areas', [])),
            'Client ID': item.get('clientId', ''),
            'Latitude': item.get('latitude', ''),
            'OS': item.get('os', ''),
            'No Impulse': item.get('noImpulse', ''),
            'Basket IDs': ', '.join(item.get('basketIds', []))
        }
        export_data.append(row)
    
    # Convert to DataFrame
    df = pd.DataFrame(export_data)
    
    # Save to CSV
    csv_filename = f'location_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(csv_filename, index=False)
    
    return send_file(
        csv_filename,
        mimetype='text/csv',
        as_attachment=True,
        download_name=csv_filename
    )

@app.route('/proxy/<endpoint>', methods=['GET'])
def proxy_endpoint(endpoint):
    """
    Generic proxy endpoint that forwards requests to the specified target endpoint
    """
    if endpoint not in TARGET_ENDPOINTS:
        return jsonify({'error': 'Endpoint not found'}), 404
    
    target_url = TARGET_ENDPOINTS[endpoint]
    
    try:
        response = requests.get(target_url, params=request.args)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy/<endpoint>/<int:id>', methods=['GET'])
def proxy_endpoint_with_id(endpoint, id):
    """
    Proxy endpoint that handles requests with specific IDs
    """
    if endpoint not in TARGET_ENDPOINTS:
        return jsonify({'error': 'Endpoint not found'}), 404
    
    target_url = f"{TARGET_ENDPOINTS[endpoint]}/{id}"
    
    try:
        response = requests.get(target_url, params=request.args)
        return jsonify(response.json()), response.status_code
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 