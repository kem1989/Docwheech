# 🚀 Docwheech MVP (v1.1) – Product Requirements Document (PRD)

## 1. Product Overview

**Product Name:** Docwheech  
**Version:** MVP v1.1  
**Objective:**  
Docwheech automates the most time-consuming part of commercial insurance submissions — turning messy, unstructured client data into completed, carrier-ready **ACORD forms** and submission packets in under 30 minutes.

---

## 2. Problem Statement

Insurance brokers spend **15+ hours/week** manually compiling and submitting insurance applications because they must:
- Gather unstructured data from PDFs, Excel sheets, and emails  
- Manually enter the same data across **multiple ACORD and carrier-specific forms**  
- Chase missing or inconsistent data through endless client and underwriter emails  

These tasks are repetitive, error-prone, and delay submissions — reducing brokers’ efficiency and profitability.

---

## 3. MVP Goal

**Goal:**  
Reduce a 15-hour manual process to **30 minutes** by automating:
1. Data extraction from uploaded documents  
2. Normalization into an **ACORD-standard schema**  
3. Automatic population of **ACORD 125 (Commercial Insurance Application)**  
4. Review, validation, and PDF export of the submission packet  

---

## 4. Core Features (MVP Scope)

| Manual Step | Automation in MVP | Feature |
|--------------|-------------------|----------|
| Collect client documents | Upload system for PDFs, Excel, Word | **Multi-file Upload Interface** |
| Manually read data | AI text & table extraction | **AI Data Extraction Engine** |
| Copy/paste into ACORD forms | Map extracted fields to ACORD JSON schema | **ACORD Schema Converter** |
| Fill out PDF forms | Auto-fill ACORD 125 PDF | **Form Auto-Filler (ACORD 125)** |
| Review data | Editable review table | **Broker Review & Correction UI** |
| Export submission | Generate submission-ready PDF | **PDF Export Engine** |

---

## 5. User Flow

### Step 1️⃣: Login or Demo Access
- Email/password or “Try without account” for MVP demo.

### Step 2️⃣: Upload Client Files
- Broker uploads multiple files (PDFs, XLSX, DOCX, or images).  
- System stores them securely (S3 or Firebase).

### Step 3️⃣: AI Extraction
- Backend uses **OpenAI GPT-4/5 + AWS Textract** to extract:
  - Client Name  
  - Business Address  
  - Policy Type  
  - Coverage Info  
  - Premium Amount  
  - Effective Dates  
  - Contact Info  
  - Financial or property data (if available)

### Step 4️⃣: Standardization (ACORD Schema)
- Extracted data is converted into a structured **ACORD 125 JSON Schema**.  
- Missing or incomplete fields are highlighted for review.

### Step 5️⃣: Review & Edit
- Broker reviews extracted fields in an editable web form.  
- Each field shows: value, confidence score, and ACORD field name.

### Step 6️⃣: Auto-Fill ACORD 125 Form
- Docwheech automatically fills the **fillable PDF** version of ACORD 125.  
- Only 15–20 critical fields are populated in MVP.

### Step 7️⃣: Export Submission Packet
- Final downloadable **Submission Packet PDF**:
  - Completed ACORD 125 form  
  - Generated Risk Narrative  
  - Uploaded supporting documents (merged)  

---

## 6. Key MVP Features

| Feature | Description | Priority |
|----------|--------------|----------|
| **1. File Upload** | Drag-and-drop for multiple docs (PDF/XLSX/DOCX) | Must-Have |
| **2. AI Extraction** | Extract structured data using OpenAI + Textract | Must-Have |
| **3. ACORD 125 JSON Schema** | Normalize data into standard ACORD fields | Must-Have |
| **4. Review UI** | Editable field review table | Must-Have |
| **5. Form Auto-Fill** | Fill ACORD 125 PDF dynamically | Must-Have |
| **6. Narrative Generator** | GPT-based summary of business risk | Nice-to-Have |
| **7. PDF Export** | Combine forms + attachments into one file | Must-Have |
| **8. Auth System** | Simple login via Firebase Auth | Must-Have |

---

## 7. Tech Architecture

| Layer | Stack | Description |
|--------|--------|-------------|
| **Frontend** | React (Next.js or Vite) | File upload, review, export UI |
| **Backend** | FastAPI (Python) | File handling, AI processing, PDF generation |
| **AI Layer** | OpenAI GPT-4/5 + AWS Textract | Extract + normalize data |
| **PDF Engine** | ReportLab / pdfrw | Auto-fill ACORD 125 |
| **Storage** | AWS S3 / Firebase Storage | Uploaded and filled documents |
| **Database** | PostgreSQL / Firebase Firestore | User + submission data |
| **Authentication** | Firebase Auth / JWT | Secure user access |

---

## 8. ACORD 125 Integration (MVP Backbone)

### A. ACORD Overview
ACORD forms are the standardized applications used across commercial insurance.  
MVP supports **ACORD 125 (Commercial Insurance Application)** as the core form.

### B. MVP ACORD JSON Schema Example
```json
{
  "ACORD125": {
    "InsuredInformation": {
      "Name": "Acme Corporation",
      "Address": "123 Main St, Dallas, TX",
      "City": "Dallas",
      "State": "TX",
      "Zip": "75201",
      "Phone": "214-555-1234"
    },
    "PolicyInformation": {
      "EffectiveDate": "2024-01-01",
      "ExpirationDate": "2025-01-01",
      "CoverageType": "General Liability",
      "TotalPremium": "15000"
    },
    "BrokerInformation": {
      "BrokerName": "John Doe",
      "Email": "john@agency.com",
      "Phone": "555-444-2222"
    }
  }
}
