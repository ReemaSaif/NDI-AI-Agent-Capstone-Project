# Applied AI Bootcamp Capstone Project - SDAIA

# NDI-AI-Agent-Capstone-Project

## **Project Name:**  معيار

## **Team Members:**
1- Tasneem Almutairi (AI Governance & RAG Systems Engineer).

2- Reema Almutawa (Data Systems, Evaluation & Reporting Engineer).

3- Ibtihal Alfayez (Computer Vision & UI Engineer)

## **Project Title:** 
**NDI-Sentinel: The Autonomous Governance & Sync Agent** 

AI-Powered Autonomous Data Governance and NDI Compliance System 

## **Problem Statement:** 
Government entities and organizations struggle to continuously measure and maintain 
compliance with NDMO regulations and the National Data Index (NDI). Currently, compliance 
assessments are mostly manual, periodic, and dependent on spreadsheets, static reports, and 
human review. 

This creates several problems: 

  * Governance policies exist in documents, while actual data is scattered across databases and files
  * Sensitive data may remain undiscovered for long periods 
  * Evidence collection for SDAIA evaluations is slow and labor-intensive 
  * Organizations lack real-time visibility into their governance maturity level 
  * Manual audits increase human error and operational cost 

The problem mainly affects: 

* Data Management Offices (DMOs)
* Compliance teams 
* IT and security departments 
* Government organizations required to follow NDMO standards
  
The project aims to automate governance monitoring and provide continuous visibility into 
organizational compliance and NDI maturity.


# How to Run the NDI‑AI‑Agent Capstone Project
Follow the steps below to set up the environment, run the dashboard, and generate the final PDF report.

#### **1- Clone the Repository:**
Download the project to your machine:
```
git clone https://github.com/ReemaSaif/NDI-AI-Agent-Capstone-Project.git
cd NDI-AI-Agent-Capstone-Project
```
#### **2- Create & Activate a Virtual Environment:**
This keeps dependencies clean and isolated.

**On Windows:**
```
python -m venv venv
venv\Scripts\activate
```

**On Mac/Linux:**
```
python3 -m venv venv
source venv/bin/activate
```

#### **3- Install Project Dependencies:**
Make sure your virtual environment is active, then run:

```
pip install -r requirements.txt
```
If you are using UV:

```
uv pip install -r requirements.txt
```

#### **4- Configure Environment Variables (Required to run the agent):**
If any agent requires API keys, create a .env file in the project root and put:
```
OPENAI_API_KEY=your_api_key_here
```

**How to Get Your `OPENAI_API_KEY`:**

- Go to the OpenAI dashboard:  
   https://platform.openai.com/login

- Sign in with your OpenAI account.

- Click -**“Create new secret key”**.

- Copy the generated API key.

- Create a `.env` file in the project root and add:
```
OPENAI_API_KEY=your_api_key_here
```

- Save the file — your project will now load the key automatically.


**Important Note:**  
Your API key is generated only once. Make sure to copy the key and save it in the .env file immediately, because you will not be able to view it again after it is created.


#### **5- Run the Dashboard (NDI Scoring Dashboard):**
This launches the main dashboard interface.
* Navigate to the dashboard folder:
```
cd dashboard
```
* Run the dashboard:
```
python app.py
```

#### **6- Generate the PDF Report (Reporting Engine):**
This creates the final Arabic PDF report using the scoring output.

Navigate to the reporting folder:
```
cd reporting
```
Run the report generator:

```
python run_report.py
```
The generated PDF will appear as:

```
OE_Arabic_Report.pdf
```
