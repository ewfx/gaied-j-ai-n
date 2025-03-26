import streamlit as st
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
import io

# Download NLTK data
nltk.download('punkt')

# Initialize models with caching for Streamlit Cloud
@st.cache_resource
def load_classifier():
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

@st.cache_resource
def load_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

classifier = load_classifier()
embedder = load_embedder()

# Request Types and Sub-Request Types
REQUEST_TYPES = [
    "Adjustment", "AU Transfer", "Closing Notice", "Commitment Change", "Fee Payment",
    "Money Movement - Inbound", "Money Movement - Outbound"
]

SUB_REQUEST_TYPES = {
    "Adjustment": [],
    "AU Transfer": [],
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
def parse_email(email_content):
    msg = email.message_from_string(email_content, policy=policy.default)
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
def extract_fields(text, request_type, sub_request_type=None):
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
    if "fee_type" in config and sub_request_type:
        fields["fee_type"] = sub_request_type
    if "currency" in config:
        currency = re.search(r'\b(USD|EUR|GBP)\b', text, re.IGNORECASE)
        fields["currency"] = currency.group() if currency else None
    if "date" in config:
        date = re.search(r'\d{2}/\d{2}/\d{4}', text)
        fields["date"] = date.group() if date else None

    return fields

# Processing Email
def process_email(email_content, previous_emails=[]):
    subject, body, attachments = parse_email(email_content)
    full_text = f"{subject} {body}"

    classification = classify_email(full_text)
    request_type = classification["request_type"]["label"]
    sub_request_type = classification["sub_request_type"]["label"] if classification["sub_request_type"] else None

    fields = extract_fields(full_text, request_type, sub_request_type)
    duplicate_flag = full_text in previous_emails

    team = ROUTING_RULES.get(request_type, {}).get(sub_request_type, ROUTING_RULES.get(request_type, "Unassigned"))

    result = {
        "request_type": request_type,
        "sub_request_type": sub_request_type,
        "extracted_fields": fields,
        "duplicate": duplicate_flag,
        "assigned_team": team,
        "source_text": full_text
    }
    return result

# Streamlit UI
st.title("Email Classification for Loan Servicing Requests")

st.write("Upload an `.eml` file to classify the email and extract relevant information.")

# File uploader
uploaded_file = st.file_uploader("Choose an email file (.eml)", type=["eml"])

# Maintain a session state for previous emails (for duplicate detection)
if 'previous_emails' not in st.session_state:
    st.session_state.previous_emails = []

if uploaded_file is not None:
    try:
        # Read the uploaded file
        email_content = uploaded_file.read().decode('utf-8', errors='ignore')

        # Process the email
        with st.spinner("Processing email..."):
            result = process_email(email_content, st.session_state.previous_emails)

        # Update previous emails for duplicate detection
        st.session_state.previous_emails.append(result["source_text"])

        # Display results
        st.subheader("Classification Results")
        st.write(f"- **Request Type:** {result['request_type']['label']} (Confidence: {result['request_type']['confidence']:.2f})")
        if result['sub_request_type']:
            st.write(f"- **Sub-Request Type:** {result['sub_request_type']['label']} (Confidence: {result['sub_request_type']['confidence']:.2f})")
        st.write(f"- **Extracted Fields:** {result['extracted_fields']}")
        st.write(f"- **Duplicate:** {result['duplicate']}")
        st.write(f"- **Assigned Team:** {result['assigned_team']}")
        st.write(f"- **Source Text:** {result['source_text']}")
        st.write("---")

        # Display raw JSON output
        st.subheader("Raw JSON Output")
        st.json(result)

        # Option to download JSON
        st.download_button(
            label="Download JSON Result",
            data=json.dumps(result, indent=2),
            file_name="classification_result.json",
            mime="application/json"
        )
    except Exception as e:
        st.error(f"Error processing email: {str(e)}")