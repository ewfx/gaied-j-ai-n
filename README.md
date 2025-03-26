📌 Project Overview
🌟 Inspiration
This project was inspired by the need to automate and streamline email classification and processing in financial and business environments. Manually handling emails for different request types (e.g., adjustments, fee payments, money movement) can be time-consuming and error-prone. By leveraging AI, this project automates classification, field extraction, and routing, reducing manual effort and improving efficiency.

⚙️ What It Does
The project is an AI-powered email classification system that:
✅ Parses incoming emails (.eml format) and extracts subject, body, and attachments
✅ Uses zero-shot classification (NLP) to determine request type & sub-request type
✅ Extracts key fields (amount, deal name, date) using regex
✅ Detects duplicate emails to prevent redundant processing
✅ Assigns emails to the correct teams based on predefined routing rules
✅ Stores structured data in a JSON file for further processing

🛠️ How We Built It
We combined Natural Language Processing (NLP) and automation tools to create a robust system:
🔹 Python as the primary programming language
🔹 Transformers (BART-large-mnli) for AI-based classification
🔹 SentenceTransformers (MiniLM-L6-v2) for text embedding and similarity checks
🔹 NLTK for text tokenization and processing
🔹 Regex (re module) for structured field extraction
🔹 pdfplumber to process attachments (if required)
🔹 Sklearn (cosine similarity) to check for duplicate emails
🔹 JSON to store structured results

🚧 Challenges We Faced
🔴 Accuracy of AI classification – Fine-tuning the model for financial terminology was challenging
🟠 Field extraction complexity – Emails have varied formats, making regex-based extraction tricky
🟡 Handling duplicate emails – Needed a reliable way to flag duplicates based on text similarity
🟢 Team routing logic – Ensuring correct mapping between request types and team assignments

🏗️ Tech Stack
💻 Programming Language: Python
🤖 AI Models: BART (Zero-shot classification), MiniLM (Embedding)
📜 NLP Libraries: Transformers, SentenceTransformers, NLTK
🛠️ Parsing Tools: email, pdfplumber, regex
📊 Data Processing: JSON, Scikit-learn
