<div align="center">

# 🚀 CivicAI - AI-Powered Civic Issue Reporting using Gemma 4

### 🏆 Build with Gemma Hackathon 2026 Submission

Transform a simple photo of a civic issue into a professional complaint report using **Gemma 4 Vision**, **LangGraph Agents**, and **FastAPI**.

---

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Gemma 4](https://img.shields.io/badge/Gemma%204-Ollama-green?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-purple?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-Frontend-red?style=for-the-badge&logo=streamlit)

</div>

---

# 🌍 Problem Statement

Every day, citizens encounter civic issues like:

- 🛣️ Potholes
- 🗑️ Garbage accumulation
- 💡 Broken street lights
- 🚰 Water leakage
- 🌳 Fallen trees

However,

- they often don't know **which department** is responsible,
- struggle to write a **professional complaint**, and
- rarely create a proper report that authorities can act upon.

---

# 💡 Our Solution

**CivicAI** is an AI-powered civic reporting assistant built using **Gemma 4**.

A user simply uploads an image of the issue.

The application automatically:

✅ Detects the issue using Gemma 4 Vision

✅ Identifies the responsible government department

✅ Generates a professional complaint

✅ Creates a downloadable PDF report

✅ Prepares an email draft ready for submission

---

# ✨ Features

- 📸 Image-based civic issue detection
- 🤖 Gemma 4 Vision Integration
- 🧠 LangGraph Agent Workflow
- 🏢 Automatic Department Identification
- 📝 AI Generated Professional Complaint
- 📄 PDF Report Generation
- 📧 Email Draft Generation
- ⚡ FastAPI Backend
- 🎨 Beautiful Streamlit Interface
- 💻 Runs Locally using Ollama

---

# 🏗️ Architecture

```text
                     User

                       │

                       ▼

              Streamlit Frontend

                       │

                       ▼

                FastAPI Backend

                       │

                       ▼

             LangGraph Civic Agent

        ┌──────────┼──────────┬──────────┐

        ▼          ▼          ▼          ▼

 Gemma Vision  Department  Complaint  PDF Report
                 Mapper    Generator  Generator

                       │

                       ▼

                  Final Response
```

---

# ⚙️ Agent Workflow

```text
Upload Image
      │
      ▼
Gemma 4 Vision Analysis
      │
      ▼
Identify Civic Issue
      │
      ▼
Find Responsible Department
      │
      ▼
Generate Complaint
      │
      ▼
Generate PDF Report
      │
      ▼
Prepare Email Draft
```

---

# 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Gemma 4 |
| Local Inference | Ollama |
| Agent Framework | LangGraph |
| Backend | FastAPI |
| Frontend | Streamlit |
| PDF | ReportLab |
| Language | Python |

---

# 📂 Project Structure

```text
backend/
│
├── agents/
├── models/
├── routes/
├── services/
├── tools/
│
frontend/
│
test_images/
test_reports/
README.md
requirements.txt
```

---

# 📸 Screenshots

## 🏠 Home Screen

> <img width="1049" height="785" alt="Screenshot 2026-07-05 at 2 34 40 PM" src="https://github.com/user-attachments/assets/c2bcac55-0215-41d9-9098-735b591c1999" />


---

## 🔍 AI Analysis

> <img width="1252" height="785" alt="Screenshot 2026-07-05 at 2 33 50 PM" src="https://github.com/user-attachments/assets/ce0b831e-eea6-4266-8e49-d3c384ba1764" />




---

# 🎥 Demo Video

🎬 Demo:

**Add your YouTube / Loom / Drive link here**



---

# 📄 Example Workflow

1. Enter your details
2. Upload an image
3. AI analyzes the issue
4. Responsible department identified
5. Complaint generated
6. PDF report downloaded
7. Email ready for submission



---

# ❤️ Why Gemma 4?

Gemma 4 provided:

- Excellent multimodal image understanding
- Structured JSON responses
- Fast local inference through Ollama
- Privacy by keeping all inference on-device
- Smooth integration into an agentic workflow

---

# 👨‍💻 Author

**Debdoot Sen**

GenAI Developer

---

<div align="center">

⭐ If you found this project interesting, please consider giving it a star!

Built with ❤️ using **Gemma 4**

</div>
