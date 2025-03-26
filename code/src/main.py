import email
from email import policy
import re
import pdfplumber
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
import json
import os

# Download NLTK data
nltk.download('punkt')

# Initialize models
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

# Request Types and Sub-Request Types
REQUEST_TYPES = [
    "Adjustment", "AU Transfer", "Closing Notice", "Commitment Change", "Fee Payment",
    "Money Movement - Inbound", "Money Movement - Outbound"
]

SUB_REQUEST_TYPES = {
    "Closing Notice": ["Reallocation Fees", "Amendment Fees", "Reallocation Principal"],
    "Commitment Change": ["Cashless Roll", "Decrease", "Increase"],
    "Fee Payment": ["Ongoing Fee", "Letter of Credit Fee"],
    "Money Movement - Inbound": ["Principal", "Interest", "Principal + Interest", "Principal + Interest + Fee"],
    "Money Movement - Outbound": ["Timebound", "Foreign Currency"]
}

FIELD_CONFIG = {
    "Adjustment": ["amount", "expiration_date"],
    "AU Transfer": ["deal_name", "amount"],
    "Closing Notice": ["deal_name", "amount", "date"],
    "Commitment Change": ["amount", "date"],
    "Fee Payment": ["amount", "fee_type"],
    "Money Movement - Inbound": ["amount", "currency"],
    "Money Movement - Outbound": ["amount", "currency"]
}

ROUTING_RULES = {
    "Adjustment": "Team A",
    "AU Transfer": "Team B",
    "Closing Notice": {"Reallocation Fees": "Team C", "Amendment Fees": "Team D", "Reallocation Principal": "Team E"},
    "Commitment Change": {"Cashless Roll": "Team F", "Decrease": "Team G", "Increase": "Team H"},
    "Fee Payment": {"Ongoing Fee": "Team I", "Letter of Credit Fee": "Team J"},
    "Money Movement - Inbound": {"Principal": "Team K", "Interest": "Team L", "Principal + Interest": "Team M", "Principal + Interest + Fee": "Team N"},
    "Money Movement - Outbound": {"Timebound": "Team O", "Foreign Currency": "Team P"}
}

# Classification Functions
def classify_request_type(text):
    result = classifier(text, REQUEST_TYPES, multi_label=False)
    return {"label": result['labels'][0], "confidence": result['scores'][0]}

def classify_sub_request_type(text, request_type):
    sub_types = SUB_REQUEST_TYPES.get(request_type, [])
    if sub_types:
        result = classifier(text, sub_types, multi_label=False)
        return {"label": result['labels'][0], "confidence": result['scores'][0]}
    return None

def classify_email(text):
    request_type = classify_request_type(text)
    sub_request_type = classify_sub_request_type(text, request_type['label'])
    return {"request_type": request_type, "sub_request_type": sub_request_type}

# Email Parsing
def parse_email(file_path):
    with open(file_path, 'rb') as f:
        msg = email.message_from_binary_file(f, policy=policy.default)

    subject = msg['subject'] or ""
    body = ""
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == 'text/plain':
                body += part.get_payload(decode=True).decode(errors='ignore')
            elif content_type == 'application/pdf':
                attachments.append(part.get_payload(decode=True))
    else:
        body = msg.get_payload(decode=True).decode(errors='ignore')

    return subject, body, attachments

# Field Extraction
def extract_fields(text, request_type):
    fields = {}
    config = FIELD_CONFIG.get(request_type, [])

    if "amount" in config:
        amount = re.search(r'\$\d+(?:\.\d{2})?', text)
        fields["amount"] = amount.group() if amount else None
    if "expiration_date" in config:
        date = re.search(r'\d{2}/\d{2}/\d{4}', text)
        fields["expiration_date"] = date.group() if date else None
    if "deal_name" in config:
        deal = re.search(r'deal\s+(\w+)', text, re.IGNORECASE)
        fields["deal_name"] = deal.group(1) if deal else None

    return fields

# Processing Email
def process_email(file_path, previous_emails=[]):
    subject, body, attachments = parse_email(file_path)
    full_text = f"{subject} {body}"

    classification = classify_email(full_text)
    request_type = classification["request_type"]["label"]
    sub_request_type = classification.get("sub_request_type", {}).get("label")

    fields = extract_fields(full_text, request_type)
    duplicate_flag = full_text in previous_emails

    team = ROUTING_RULES.get(request_type, {}).get(sub_request_type, "Unassigned")
    result = {
        "request_type": request_type,
        "sub_request_type": sub_request_type,
        "extracted_fields": fields,
        "duplicate": duplicate_flag,
        "assigned_team": team,
        "source_text": full_text
    }
    return result

# Main Execution
def main(input_dir, output_file):
    previous_emails = []
    results = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".eml"):
            file_path = os.path.join(input_dir, filename)
            output = process_email(file_path, previous_emails)
            results.append(output)
            previous_emails.append(output["source_text"])

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Processed {len(results)} requests. Output saved to {output_file}")

if __name__ == "__main__":
    input_dir = "/src/data/emails"  # Update as needed
    output_file = "/src/result/output.json"
    main(input_dir, output_file)
