import requests
import hashlib

# Function to create the hash of your space data
def generate_data_hash(space_data):
    return hashlib.sha256(space_data.encode('utf-8')).hexdigest()

# Function to send data to WhatsOnChain
def send_to_blockchain(data_hash, api_key):
    url = 'https://api.whatsonchain.com/v1/bsv/main/tx/raw'

    # Create a transaction that will store the hash on the blockchain
    transaction = {
        "tx": {
            "version": 1,
            "inputs": [
                {
                    "prevTxId": "b7b5e0d87e9c1972d46b24a2e3f0d52f3f784ae0a863920fe7b2184c7f315db0",  # Replace with actual previous transaction ID
                    "outputIndex": 0,
                    "scriptSig": {
                        "asm": "OP_CHECKSIG",
                        "hex": "483045022100cc6ab537fefcd2769b39721c5b267e8c5709ecb62865b84e515659017b6ec2902206a99b1708885edff9b7f0b3a643a9f8d68a5ea0d7bcf44c07abf84e8a41d493601"
                    },
                    "sequence": 4294967295
                }
            ],
            "outputs": [
                {
                    "value": 0,  # Set the appropriate value in satoshis
                    "scriptPubKey": {
                        "asm": f"OP_RETURN {data_hash}",
                        "hex": f"6a{len(data_hash)//2:02x}{data_hash}"
                    }
                }
            ],
            "locktime": 0
        }
    }

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, json=transaction, headers=headers)

    if response.status_code == 200:
        print("Data successfully stored on the blockchain!")
        print(response.json())
    else:
        print("Error storing data on blockchain:", response.status_code, response.text)

# Your space data (e.g., satellite data)
space_data = "Satellite sensor data: Temperature: 25°C, Pressure: 1013 hPa"

# Generate the hash of the space data
data_hash = generate_data_hash(space_data)
print(f"Data Hash: {data_hash}")

# Replace with your WhatsOnChain API key
api_key = 'your_api_key'

# Send the data hash to the blockchain
send_to_blockchain(data_hash, api_key)
