from flask import Flask, render_template, redirect, url_for, request, jsonify
import subprocess
import pymongo
from bson import ObjectId
from flask.json.provider import DefaultJSONProvider

app = Flask(__name__)

# Custom JSON provider class
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Set the custom JSON provider
app.json_provider_class = CustomJSONProvider

def get_latest_trends():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["twitter_trends"]
    collection = db["trends"]
    latest_entry = list(collection.find().sort([('_id', -1)]).limit(1))
    if len(latest_entry) > 0:
        # Convert ObjectId to string for proper JSON serialization
        latest_entry[0]['_id'] = {'$oid': str(latest_entry[0]['_id'])}
        return latest_entry[0]
    return None

@app.route('/')
def index():
    return render_template('index.html', trends=None)

@app.route('/fetch-trends', methods=['POST'])
def fetch_trends():
    subprocess.run(["python", "selenium_script.py"])
    return redirect(url_for('show_trends'))

@app.route('/show-trends', methods=['GET'])
def show_trends():
    latest_trends = get_latest_trends()
    return render_template('index.html', trends=latest_trends)

@app.route('/latest-trends-json', methods=['GET'])
def latest_trends_json():
    latest_trends = get_latest_trends()
    if latest_trends:
        return jsonify(latest_trends)
    else:
        return jsonify({"error": "No trends found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
