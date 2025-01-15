from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def find_differences(df1, df2):
    """Find differences between two DataFrames."""
    all_columns = list(set(df1.columns) | set(df2.columns))
    
    # Add missing columns with NaN values
    for col in all_columns:
        if col not in df1.columns:
            df1[col] = np.nan
        if col not in df2.columns:
            df2[col] = np.nan
    
    differences = []
    for idx in range(max(len(df1), len(df2))):
        if idx < len(df1) and idx < len(df2):
            row1 = df1.iloc[idx]
            row2 = df2.iloc[idx]
            
            for col in all_columns:
                val1 = str(row1[col]) if not pd.isna(row1[col]) else ""
                val2 = str(row2[col]) if not pd.isna(row2[col]) else ""
                
                if val1 != val2:
                    differences.append({
                        'row': idx,
                        'column': col,
                        'old_value': val1,
                        'new_value': val2
                    })
        else:
            if idx >= len(df1):
                row2 = df2.iloc[idx]
                for col in all_columns:
                    val2 = str(row2[col]) if not pd.isna(row2[col]) else ""
                    differences.append({
                        'row': idx,
                        'column': col,
                        'old_value': "",
                        'new_value': val2
                    })
            else:
                row1 = df1.iloc[idx]
                for col in all_columns:
                    val1 = str(row1[col]) if not pd.isna(row1[col]) else ""
                    differences.append({
                        'row': idx,
                        'column': col,
                        'old_value': val1,
                        'new_value': ""
                    })
    
    return differences

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Both files are required'}), 400
    
    file1 = request.files['file1']
    file2 = request.files['file2']
    
    if file1.filename == '' or file2.filename == '':
        return jsonify({'error': 'Both files are required'}), 400
    
    # Save files
    filename1 = secure_filename(file1.filename)
    filename2 = secure_filename(file2.filename)
    
    file1_path = os.path.join(app.config['UPLOAD_FOLDER'], filename1)
    file2_path = os.path.join(app.config['UPLOAD_FOLDER'], filename2)
    
    file1.save(file1_path)
    file2.save(file2_path)
    
    try:
        # Read CSVs with string type for all columns to avoid type conversion issues
        df1 = pd.read_csv(file1_path, dtype=str)
        df2 = pd.read_csv(file2_path, dtype=str)
        
        # Find differences
        differences = find_differences(df1, df2)
        
        # Convert DataFrames to JSON-safe format
        data1 = df1.replace({np.nan: None}).to_dict(orient='records')
        data2 = df2.replace({np.nan: None}).to_dict(orient='records')
        columns = list(set(df1.columns) | set(df2.columns))
        
        return jsonify({
            'data1': data1,
            'data2': data2,
            'columns': columns,
            'differences': differences
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up uploaded files
        try:
            os.remove(file1_path)
            os.remove(file2_path)
        except:
            pass

@app.route('/save', methods=['POST'])
def save_result():
    try:
        data = request.json
        df = pd.DataFrame(data['result'])
        output_path = 'merged_result.csv'
        df.to_csv(output_path, index=False)
        return send_file(output_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 