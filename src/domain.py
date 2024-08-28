import os
import idna
import base64
from dotenv import load_dotenv

def load_domain():
    load_dotenv()
    domain = os.getenv('DOMAIN')
    if not domain:
        raise ValueError("The DOMAIN environment variable is not set or is empty.")
    encoded_domain = idna.encode(domain).decode('utf-8')
    return encoded_domain

def handle_failed_auth(event):
    error_text = event.get('text', '')
    error_condition = event.get('condition', '')
    
    if error_condition:
        error_message = f"Error condition: {error_condition}"
    elif error_text:
        error_message = f"Error text: {error_text}"
    else:
        error_message = "An unknown error occurred."
    
    print(f"Login failed: {error_message}")

async def process_incoming_message(message):
    if message["type"] == "chat":
        if message["body"].startswith("file://"):
            parts = message["body"].split("://")
            file_extension = parts[1]
            encoded_content = parts[2]
            file_content = base64.b64decode(encoded_content)
            file_path = f"./files/received_file.{file_extension}"
            
            with open(file_path, "wb") as file:
                file.write(file_content)
            
            sender = str(message['from']).split('/')[0]
            print(f"\n❑ You just received a file from [{sender}]: {file_path}\n")
        else:
            sender = str(message["from"]).split("/")[0]
            print(f"\n\n{sender}: {message['body']}")
    else:
        print(f"\nYou just received a message from [{message['from']}]\n")

def register_plugins(xmpp_client):
    plugins = [
        "xep_0004",  # Data Forms
        "xep_0030",  # Service Discovery
        "xep_0045",  # Multi-User Chat (MUC)
        "xep_0060",  # Publish-Subscribe
        "xep_0050",  # Ad-Hoc Commands
        "xep_0066",  # Out of Band Data
        "xep_0071",  # XHTML-IM
        "xep_0085",  # Chat State Notifications
        "xep_0199",  # XMPP Ping
    ]
    
    for plugin in plugins:
        xmpp_client.register_plugin(plugin)

def register_event_handlers(xmpp_client):
    xmpp_client.add_event_handler("session_start", xmpp_client.start_session)
    xmpp_client.add_event_handler("failed_auth", handle_failed_auth)
    xmpp_client.add_event_handler("message", process_incoming_message)
    xmpp_client.add_event_handler("message_received", xmpp_client.handle_message)
