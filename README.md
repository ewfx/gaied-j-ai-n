🚀 Email Request Classifier

📌 Table of Contents
- Introduction
- Demo
- Inspiration
- What It Does
- How We Built It
- Challenges We Faced
- How to Run
- Tech Stack
- Team

🎯 Introduction

The Email Request Classifier is an intelligent system designed to automatically process and categorize financial email requests. It solves the problem of manual email sorting by extracting key information and routing requests to appropriate teams, saving time and reducing human error in financial operations.

🎥 Demo

🔗 Live Demo: Not available  
📹 Video Demo: Coming soon  
🖼️ Screenshots:  

**Screenshot 1: Sample Output JSON**  
![Sample Output](https://via.placeholder.com/600x400.png?text=Sample+JSON+Output)

💡 Inspiration

We were inspired by the inefficiencies in manual email processing in financial institutions, where staff spend hours sorting through requests like fund transfers, fee payments, and commitment changes. Our goal was to automate this process using AI to improve accuracy and efficiency.

⚙️ What It Does

- Parses email files (.eml) to extract subject, body, and attachments  
- Classifies email requests into predefined types (e.g., "Money Movement", "Fee Payment")  
- Identifies sub-request types (e.g., "Principal", "Foreign Currency")  
- Extracts key fields like amounts, dates, and deal names  
- Routes requests to appropriate teams based on predefined rules  
- Flags duplicate emails to prevent redundant processing  

🛠️ How We Built It

We leveraged natural language processing (NLP) and machine learning tools to analyze email content. The system uses pre-trained models for classification and custom regex patterns for field extraction, with a modular design for easy scalability.

🚧 Challenges We Faced

- Handling varied email formats and inconsistent data presentation  
- Fine-tuning zero-shot classification for domain-specific financial terms  
- Ensuring accurate field extraction with regex across diverse email styles  
- Managing dependencies and model loading times for efficient processing  

🏃 How to Run

1. Clone the repository  
   ```
   git clone https://github.com/your-repo.git
   ```
2. Install dependencies  
   ```
   pip install -r requirements.txt
   ```
3. Run the project  
   ```
   python main.py
   ```
   - Ensure your email files are in `/src/data/emails/`  
   - Output will be saved to `/src/result/output.json`  

🏗️ Tech Stack

🔹 Backend: Python  
🔹 NLP/ML: Transformers (BART), Sentence-Transformers (MiniLM)  
🔹 Data Processing: pdfplumber, NLTK, scikit-learn  
🔹 Other: Regular Expressions (re)  

👥 Team

- Dhruv Bansal 
- Prateek Singh Sidhu
- Yash Modhwadia
- Vardhaman Jain 

--- 

Feel free to customize the placeholders (e.g., GitHub links, screenshots, team names) to fit your specific project and team details! Let me know if you'd like help refining any section further.
