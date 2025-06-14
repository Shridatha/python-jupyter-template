import requests
from flask import Flask, request, jsonify

import requests

def get_iam_token(api_key: str) -> str:
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = f"apikey={api_key}&grant_type=urn:ibm:params:oauth:grant-type:apikey"

    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


app = Flask(__name__)

PREDICTION_URL = "https://eu-de.ml.cloud.ibm.com/ml/v4/deployments/89a96b10-e9f0-4a92-90b9-a6c084ea6375/predictions?version=2021-05-01"
iam_token = get_iam_token("your_ibm_cloud_api_key")

class_map = {0: "Healthy", 1: "Faulty"}
 
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()

        headers = {
            "Authorization": f"Bearer {get_iam_token()}",
            "Content-Type": "application/json"
        }

        response = requests.post(PREDICTION_URL, headers=headers, json=data)

        if response.status_code == 200:
            prediction_data = response.json()
            predictions = prediction_data.get("predictions", [{}])[0].get("values", [])
            
            if not predictions:
                return jsonify({"error": "No predictions found"}), 500

            predicted_class = predictions[0][0]
            probability = predictions[0][1]
            confidence = round(max(probability) * 100, 2)

            return jsonify({
                "prediction": class_map.get(predicted_class, "Unknown"),
                "confidence": confidence
            })

        else:
            return jsonify({"error": response.text}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
