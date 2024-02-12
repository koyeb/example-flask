from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load data from Excel file
excel_file_path = "C:/Users/karthikeya.andhoju/Desktop/email_automation/emails.xlsx"
df = pd.read_excel(excel_file_path)

# Convert dataframe to dictionary for easier access
database = df.set_index('case_id').to_dict()['email']


@app.route('/case/<int:case_id>', methods=['GET'])
def get_case(case_id):
    if case_id in database:
        return jsonify({'case_id': case_id, 'email': database[case_id]})
    else:
        return jsonify({'message': 'Case ID not found'}), 404


@app.route('/case/<int:case_id>', methods=['POST'])
def create_case(case_id):
    email = request.json.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    if case_id in database:
        return jsonify({'message': 'Case ID already exists'}), 400
    database[case_id] = email
    # Append data to the Excel file
    df.loc[len(df)] = [case_id, email]
    df.to_excel(excel_file_path, index=False)
    return jsonify({'case_id': case_id, 'email': email}), 201


@app.route('/case/<int:case_id>', methods=['PUT'])
def update_case(case_id):
    email = request.json.get('email')
    if not email:
        return jsonify({'message': 'Email is required'}), 400
    if case_id not in database:
        return jsonify({'message': 'Case ID not found'}), 404
    database[case_id] = email
    # Update data in the Excel file
    df.loc[df['case_id'] == case_id, 'email'] = email
    df.to_excel(excel_file_path, index=False)
    return jsonify({'case_id': case_id, 'email': email}), 200


@app.route('/case/<int:case_id>', methods=['DELETE'])
def delete_case(case_id):
    if case_id not in database:
        return jsonify({'message': 'Case ID not found'}), 404
    del database[case_id]
    # Update data in the Excel file
    df.drop(df[df['case_id'] == case_id].index, inplace=True)
    df.to_excel(excel_file_path, index=False)
    return jsonify({'message': 'Case deleted'}), 200


if __name__ == '__main__':
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=8000)
    app.run(debug=True)
