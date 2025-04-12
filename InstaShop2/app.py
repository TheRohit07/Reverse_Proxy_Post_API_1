from flask import Flask, render_template, request, jsonify, send_file
import json
import csv
import io
import requests
from datetime import datetime

app = Flask(__name__)

# Store data in memory
data_store = []

# Target endpoint for reverse proxy
TARGET_ENDPOINT = 'https://api.instashop.com/users'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def view_data():
    return render_template('data.html', data=data_store)

@app.route('/submit', methods=['POST'])
def submit():
    try:
        # Clear existing data before adding new data
        data_store.clear()
        
        data = request.json
        data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        data_store.append(data)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/export-csv')
def export_csv():
    if not data_store:
        return "No data available to export", 404

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    headers = [
        'Timestamp', 'Client ID', 'Category ID', 'Skip', 'Size',
        'App State', 'Business Types', 'Areas', 'Client ID',
        'OS', 'No Impulse', 'Basket IDs',
        'System Info - Region Code', 'System Info - Country Code',
        'System Info - Platform', 'System Info - Timestamp',
        'System Info - Device ID', 'System Info - Country ID',
        'System Info - Session ID', 'System Info - Language',
        'System Info - Timezone', 'System Info - LVC',
        'System Info - App Version', 'System Info - Environment',
        'System Info - App Build', 'System Info - IDFA'
    ]
    writer.writerow(headers)

    # Write data rows
    for item in data_store:
        row = [
            item.get('timestamp', ''),
            item.get('clientId', ''),
            item.get('categoryId', ''),
            item.get('skip', ''),
            item.get('size', ''),
            item.get('appState', ''),
            ', '.join(item.get('currentBusinessTypes', [])),
            ', '.join(item.get('areas', [])),
            item.get('clientId', ''),
            item.get('os', ''),
            item.get('noImpulse', ''),
            ', '.join(item.get('basketIds', []))
        ]

        # Add systemInfo fields
        system_info = item.get('systemInfo', {})
        row.extend([
            system_info.get('regionCode', ''),
            system_info.get('countryCode', ''),
            system_info.get('platform', ''),
            system_info.get('timestamp', ''),
            system_info.get('deviceId', ''),
            system_info.get('countryId', ''),
            system_info.get('instashopSessionId', ''),
            system_info.get('lang', ''),
            system_info.get('timezone', ''),
            system_info.get('LVC', ''),
            system_info.get('appVersion', ''),
            system_info.get('environment', ''),
            system_info.get('appBuild', ''),
            system_info.get('idfa', '')
        ])

        writer.writerow(row)

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='location_data.csv'
    )

# Reverse proxy endpoint for getting all users
@app.route('/proxy/users', methods=['GET'])
def proxy_users():
    try:
        response = requests.get(TARGET_ENDPOINT, params=request.args)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 