from flask import Flask, request, jsonify
from PIL import Image
import piexif
import json
import hashlib
import requests
import io
import os
import time

app = Flask(__name__)

# Ensure meta folder exists
os.makedirs("meta", exist_ok=True)

@app.route('/index')
def index():
	return "blockchain"

def extract_metadata(image_file):
    metadata = {}
    
    try:
        img = Image.open(image_file)
        
        # EXIF metadata (for JPEG and PNG if available)
        exif_bytes = img.info.get("exif")
        if exif_bytes:
            try:
                exif_data = piexif.load(exif_bytes)
                metadata["EXIF"] = {
                    piexif.TAGS[ifd][tag]["name"]: exif_data[ifd][tag]
                    for ifd in exif_data for tag in exif_data[ifd]
                    if tag in piexif.TAGS[ifd]
                }
            except Exception as e:
                metadata["EXIF_error"] = str(e)
        else:
            metadata["EXIF"] = "No EXIF data found"
        
        # Other metadata from PNG (tEXt, iTXt, etc.)
        for key, value in img.info.items():
            if isinstance(value, bytes):
                try:
                    value = value.decode(errors='ignore')
                except Exception:
                    value = str(value)
            metadata[key] = value
        
        # Technical parameters
        metadata["technical_parameters"] = {
            "format": img.format,
            "size": img.size,
            "mode": img.mode,
        }
        
        # Hash the image
        image_file.seek(0)
        image_data = image_file.read()
        hash_object = hashlib.sha256(image_data)
        metadata["hashimage"] = hash_object.hexdigest()
    
    except Exception as e:
        metadata["error"] = str(e)
    
    return metadata

def save_metadata(metadata):
    """Saves metadata JSON to the meta folder with a timestamped filename."""
    timestamp = time.strftime("%Y%m%d%H%M%S")
    json_filename = f"meta/{timestamp}.json"
    with open(json_filename, "w") as f:
        json.dump(metadata, f, indent=4)
    return json_filename

def send_to_api(metadata, api_url):
    """Sends JSON data to another API."""
    try:
        response = requests.post(api_url, json=metadata)
        return response.status_code, response.text
    except Exception as e:
        return 500, str(e)

@app.route("/upload", methods=["POST"])
def upload_file():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    
    image_file = request.files["image"]
    metadata = extract_metadata(image_file)
    
    # Save metadata locally
    json_filename = save_metadata(metadata)
    argument = metadata
   
    command = f"yarn send-op-return {metadata}" # Using an f-string
    status_code = os.system(command)  #response_text = send_to_api(metadata, api_url)
    

     # api_url = "https://example.com/receive_metadata"  # Change to actual API URL

    return jsonify({
        "message": "Metadata extracted, saved, and sent to API",
        "saved_json": json_filename,
        "api_response": response_text
    }), status_code

if __name__ == "__main__":
    app.run(debug=True)
