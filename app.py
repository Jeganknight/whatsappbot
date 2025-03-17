import os
from flask import Flask, request
from twilio.rest import Client
import pymssql

app = Flask(__name__)

# Load environment variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Twilio Client
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Database Connection
try:
    conn = pymssql.connect(
        server=DB_SERVER,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    print("✅ Connected to Azure SQL Database successfully!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# Function to store message in database
def store_message(phone_number, message_text):
    try:
        query = "INSERT INTO UserMessages (phone_number, message_text) VALUES (%s, %s)"
        cursor.execute(query, (phone_number, message_text))
        conn.commit()
    except Exception as e:
        print(f"❌ Error storing message: {e}")

# Function to send WhatsApp message via Twilio
def send_whatsapp_message(to, message):
    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        body=message,
        to=f"whatsapp:{to}"
    )

# Flask route to handle incoming WhatsApp messages
@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    incoming_msg = request.values.get("Body", "").strip()  # User's message
    sender_number = request.values.get("From", "").replace("whatsapp:", "")  # User's phone number

    store_message(sender_number, incoming_msg)  # Save message to database

    # Simple chatbot logic
    if incoming_msg.lower() == "hi":
        response_text = "Hello! Please send your *Name* and *Address*."
    elif "," in incoming_msg:  # Assuming user sends "John, Chennai"
        response_text = "Thank you! Your details have been saved. ✅"
    else:
        response_text = "Sorry, I didn't understand. Please send your Name and Address."

    # Send response message via Twilio
    send_whatsapp_message(sender_number, response_text)

    return "Message processed successfully", 200

# Run Flask server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
