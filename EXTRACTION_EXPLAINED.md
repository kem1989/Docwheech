# How Document Extraction Works: Textract + OpenAI

## Overview

Your application uses a **two-stage extraction pipeline** that combines AWS Textract (OCR) and OpenAI GPT-4 (AI understanding) to extract structured insurance data from documents.

Think of it like this:
- **Textract** = The "eyes" 👁️ (reads text from PDFs/images)
- **OpenAI** = The "brain" 🧠 (understands and structures the text)

---

## 🔄 Complete Extraction Flow

```
📄 PDF/Image Document
        ↓
    [STAGE 1]
  AWS Textract 👁️
  "Read the text"
        ↓
   Raw Text Output
        ↓
    [STAGE 2]
   OpenAI GPT-4 🧠
 "Understand & Structure"
        ↓
  Structured ACORD Data
```

---

## 📊 Stage 1: AWS Textract (OCR - Optical Character Recognition)

### What Textract Does
Textract is Amazon's **document text extraction service**. It uses machine learning to:
1. **Detect text** in PDFs and images (JPG, PNG, TIFF)
2. **Recognize words and lines** using OCR technology
3. **Preserve layout** and reading order
4. **Extract tables** (optional feature)
5. **Provide confidence scores** for each detected word/line

### Input
- Document stored in S3
- File type: PDF, JPG, PNG, TIFF, DOCX

### Output Example
```json
{
  "text": "ACORD 125 COMMERCIAL INSURANCE APPLICATION\nAgency: ABC Insurance Group\nPhone: (555) 123-4567\nApplicant Name: Tech Solutions LLC\nAddress: 123 Main St, Dallas, TX 75201\nNAICS Code: 541511\nBusiness Type: Computer Systems Design\nEffective Date: 01/15/2024...",
  
  "page_count": 3,
  
  "confidence_scores": {
    "average_line_confidence": 98.5,
    "average_word_confidence": 97.8,
    "total_lines": 245,
    "total_words": 1523
  },
  
  "status": "completed"
}
```

### How It Works in Your Code

```python
# From: backend/app/services/textract_service.py

# For PDFs - Asynchronous processing
response = self.textract_client.start_document_text_detection(
    DocumentLocation={
        'S3Object': {
            'Bucket': bucket,
            'Name': key
        }
    }
)

# Wait for Textract to finish processing (polls every 5 seconds)
job_result = self._wait_for_job_completion(job_id)

# Extract text from Textract "blocks" (words, lines, pages)
extracted_text = self._extract_text_from_blocks(job_result.get('Blocks', []))
```

### What Textract Returns
```python
# Each "block" represents a piece of detected text
{
    'BlockType': 'LINE',  # or 'WORD', 'PAGE'
    'Text': 'Tech Solutions LLC',
    'Confidence': 99.2,
    'Page': 1,
    'Top': 0.15,  # Position on page
    'Left': 0.10
}
```

### Limitations of Textract
❌ **Cannot understand context** - It just reads text character by character  
❌ **Cannot identify field types** - Doesn't know what "Tech Solutions LLC" means  
❌ **Cannot structure data** - Returns flat text, not organized fields  
❌ **Cannot handle handwriting well** - Best with printed text  

**Example:**
- Textract sees: "01/15/2024"
- Textract returns: "01/15/2024" (just text)
- Textract doesn't know: Is this a date? Effective date? Birth date? Invoice date?

---

## 🧠 Stage 2: OpenAI GPT-4 (AI Understanding & Structuring)

### What OpenAI Does
OpenAI GPT-4 is a **large language model** that:
1. **Reads the raw text** from Textract
2. **Understands context** and meaning
3. **Identifies insurance fields** (agency name, policy dates, coverage types, etc.)
4. **Structures data** into ACORD 125 format
5. **Assigns confidence scores** based on clarity
6. **Handles ambiguity** and makes intelligent inferences

### Input
The raw text output from Textract (up to 6000 characters):

```
ACORD 125 COMMERCIAL INSURANCE APPLICATION
Agency: ABC Insurance Group
Phone: (555) 123-4567
Applicant Name: Tech Solutions LLC
Address: 123 Main St, Dallas, TX 75201
NAICS Code: 541511
Business Type: Computer Systems Design
Effective Date: 01/15/2024
Expiration Date: 01/15/2025
Premium: $12,500
Coverage: General Liability, Property
...
```

### Output Example
```json
{
  "agency": {
    "name": {
      "value": "ABC Insurance Group",
      "confidence": 0.95
    },
    "phone": {
      "value": "(555) 123-4567",
      "confidence": 0.92
    }
  },
  
  "first_named_insured": {
    "name": {
      "value": "Tech Solutions LLC",
      "confidence": 0.98
    },
    "mailing_address": {
      "value": "123 Main St, Dallas, TX 75201",
      "confidence": 0.90
    },
    "naics_code": {
      "value": "541511",
      "confidence": 0.88
    },
    "business_structure": {
      "value": "LLC",
      "confidence": 0.95
    }
  },
  
  "policy": {
    "proposed_effective_date": {
      "value": "2024-01-15",
      "confidence": 0.92
    },
    "proposed_expiration_date": {
      "value": "2025-01-15",
      "confidence": 0.92
    },
    "deposit_premium": {
      "value": 12500,
      "confidence": 0.90
    }
  },
  
  "lines_of_business": {
    "value": ["COMMERCIAL_GENERAL_LIABILITY", "COMMERCIAL_PROPERTY"],
    "confidence": 0.93
  }
}
```

### How It Works in Your Code

```python
# From: backend/app/services/openai_service.py

# Send text to OpenAI with detailed extraction prompt
response = self.client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[
        {
            "role": "system",
            "content": "You are an expert insurance data extraction specialist..."
        },
        {
            "role": "user",
            "content": prompt  # Contains raw text + extraction instructions
        }
    ],
    temperature=0.1,  # Low = more consistent/predictable
    max_tokens=2000,
    response_format={"type": "json_object"}  # Force JSON output
)

# Parse the structured JSON response
extracted_data = json.loads(response.choices[0].message.content)
```

### The Extraction Prompt

Your code sends a **detailed prompt** to OpenAI (lines 91-174 in `openai_service.py`) that:

1. **Shows the raw text** from Textract
2. **Defines the exact JSON structure** expected
3. **Lists all ACORD 125 fields** to extract
4. **Provides formatting rules**:
   - Dates: YYYY-MM-DD format
   - Phone: (XXX) XXX-XXXX format
   - NAICS codes: 6 digits
   - Use specific ENUM values (LLC, CORPORATION, etc.)
5. **Requests confidence scores** for each field
6. **Instructs to use `null`** for missing data

### Why OpenAI is Powerful

✅ **Context-aware** - Knows "01/15/2024" near "Effective Date" is the policy start  
✅ **Field identification** - Recognizes "Tech Solutions LLC" is the insured name  
✅ **Format standardization** - Converts "January 15, 2024" → "2024-01-15"  
✅ **Data validation** - Formats phone numbers, validates NAICS codes  
✅ **Handles variations** - Understands "GL" means "General Liability"  
✅ **Intelligent inference** - Sees "LLC" in name, sets business structure  

---

## 🔗 How They Work Together

### Step-by-Step Process

```python
# From: backend/app/services/ai_extraction_service.py
# Lines 54-159

async def extract_from_documents(...):
    # STEP 1: Extract text from ALL documents using Textract (20-40%)
    extracted_texts = []
    
    for document in document_keys:
        # Textract reads the document
        textract_result = await run_in_threadpool(
            self.textract_service.extract_text_from_s3,
            bucket=settings.AWS_S3_BUCKET,
            key=document_key,
            document_type='pdf'
        )
        
        # Store the raw text
        extracted_texts.append(textract_result['text'])
    
    # STEP 2: Combine all extracted text
    combined_text = '\n\n--- DOCUMENT SEPARATOR ---\n\n'.join(extracted_texts)
    
    # STEP 3: Send combined text to OpenAI (40-60%)
    extracted_data = await run_in_threadpool(
        self.openai_service.extract_insurance_data,
        extracted_text=combined_text,
        file_type="combined",
        confidence_threshold=0.7
    )
    
    # STEP 4: Generate risk narrative (60-70%)
    risk_narrative = await run_in_threadpool(
        self.openai_service.generate_risk_narrative,
        extracted_data
    )
    
    # STEP 5: Convert to ACORD schema (70-85%)
    acord_schema = create_acord_schema_from_extraction(extracted_data)
    
    # STEP 6: Return structured result
    return {
        'extracted_data': extracted_data,  # With confidence scores
        'acord_schema': acord_schema.to_dict(),  # Clean ACORD format
        'risk_narrative': risk_narrative,
        'document_metadata': document_metadata
    }
```

---

## 📈 Progress Tracking (5 Steps in UI)

| Progress % | UI Step | What's Happening | Service |
|------------|---------|------------------|---------|
| 0-20% | **Step 1: Document Analysis** | Validating documents, preparing for extraction | System |
| 20-40% | **Step 2: Text Extraction** | **Textract reading PDFs/images** | AWS Textract 👁️ |
| 40-60% | **Step 3: AI Processing** | **OpenAI structuring data** | OpenAI GPT-4 🧠 |
| 60-80% | **Step 4: Data Validation** | Generating risk narrative, validating fields | OpenAI GPT-4 🧠 |
| 80-100% | **Step 5: ACORD Mapping** | Converting to ACORD 125 schema, saving to DB | System |

---

## 🎯 Real Example

### Original Document (PDF)
```
┌─────────────────────────────────────────────┐
│     ACORD 125 - COMMERCIAL INSURANCE        │
│              APPLICATION                     │
├─────────────────────────────────────────────┤
│ AGENCY:                                     │
│ ABC Insurance Group                         │
│ 456 Insurance Blvd, Suite 200              │
│ Phone: 555-123-4567                        │
│                                             │
│ APPLICANT INFORMATION:                      │
│ Name: Tech Solutions LLC                    │
│ DBA: TechSol                               │
│ 123 Main Street                            │
│ Dallas, TX 75201                           │
│ NAICS: 541511                              │
│                                             │
│ COVERAGE REQUESTED:                         │
│ [X] General Liability                       │
│ [X] Commercial Property                     │
│ [ ] Workers Compensation                    │
│                                             │
│ Proposed Effective: 01/15/2024             │
│ Proposed Expiration: 01/15/2025            │
└─────────────────────────────────────────────┘
```

### After Textract (Raw Text)
```
ACORD 125 - COMMERCIAL INSURANCE
APPLICATION
AGENCY:
ABC Insurance Group
456 Insurance Blvd, Suite 200
Phone: 555-123-4567
APPLICANT INFORMATION:
Name: Tech Solutions LLC
DBA: TechSol
123 Main Street
Dallas, TX 75201
NAICS: 541511
COVERAGE REQUESTED:
[X] General Liability
[X] Commercial Property
[ ] Workers Compensation
Proposed Effective: 01/15/2024
Proposed Expiration: 01/15/2025
```

### After OpenAI (Structured Data)
```json
{
  "agency": {
    "name": {"value": "ABC Insurance Group", "confidence": 0.98},
    "address": {"value": "456 Insurance Blvd, Suite 200", "confidence": 0.95},
    "phone": {"value": "(555) 123-4567", "confidence": 0.92}
  },
  "first_named_insured": {
    "name": {"value": "Tech Solutions LLC", "confidence": 0.98},
    "mailing_address": {"value": "123 Main Street, Dallas, TX 75201", "confidence": 0.95},
    "naics_code": {"value": "541511", "confidence": 0.90},
    "business_structure": {"value": "LLC", "confidence": 0.95}
  },
  "lines_of_business": {
    "value": ["COMMERCIAL_GENERAL_LIABILITY", "COMMERCIAL_PROPERTY"],
    "confidence": 0.95
  },
  "policy": {
    "proposed_effective_date": {"value": "2024-01-15", "confidence": 0.95},
    "proposed_expiration_date": {"value": "2025-01-15", "confidence": 0.95}
  }
}
```

---

## 🎨 Why Use Both Services?

### Why Not Just Textract?
❌ Textract returns unstructured text  
❌ Can't identify field types (names vs addresses vs dates)  
❌ Can't map to ACORD 125 format  
❌ Can't understand business context  

### Why Not Just OpenAI?
❌ OpenAI can't read images or PDFs directly  
❌ Limited to ~6000 characters of text input  
❌ No built-in OCR capabilities  
❌ More expensive to process raw images  

### Why Both Together?
✅ **Textract** handles OCR (perfect for this)  
✅ **OpenAI** handles understanding (perfect for this)  
✅ **Cost-effective** - Use each service for its strength  
✅ **Accurate** - Textract's OCR + OpenAI's intelligence  
✅ **Scalable** - Can process any number of documents  

---

## 💰 Cost Breakdown

### Textract Pricing (Approximate)
- **Detect Text API**: $1.50 per 1,000 pages
- **Analyze Document API** (with tables): $50 per 1,000 pages

**Example:** 
- 3-page ACORD form = $0.0045
- 100 submissions/month (300 pages) = $0.45

### OpenAI Pricing (GPT-4 Turbo)
- **Input**: $10 per 1M tokens (~750k words)
- **Output**: $30 per 1M tokens

**Example:**
- 3-page form ≈ 1,500 tokens input
- Extraction output ≈ 800 tokens
- Cost per extraction: $0.03
- 100 submissions/month = $3.00

**Total monthly cost for 100 submissions: ~$3.50**

---

## 🔧 Technical Details

### Multi-Document Handling
```python
# If user uploads 3 documents, the system:

# 1. Extracts text from each separately
doc1_text = textract.extract(document1.pdf)  # "Page 1 text..."
doc2_text = textract.extract(document2.jpg)  # "Page 2 text..."
doc3_text = textract.extract(document3.pdf)  # "Page 3 text..."

# 2. Combines them with separators
combined = f"{doc1_text}\n\n--- DOCUMENT SEPARATOR ---\n\n{doc2_text}\n\n--- DOCUMENT SEPARATOR ---\n\n{doc3_text}"

# 3. Sends combined text to OpenAI once
structured_data = openai.extract(combined)
```

### Confidence Scores
Both services provide confidence scores:

**Textract Confidence:**
```json
{
  "average_line_confidence": 98.5,  // How confident OCR is
  "average_word_confidence": 97.8
}
```

**OpenAI Confidence:**
```json
{
  "name": {
    "value": "Tech Solutions LLC",
    "confidence": 0.95  // How confident GPT-4 is this is the name
  }
}
```

Low confidence flags (< 0.7) are marked for manual review.

---

## 🚨 Error Handling

### What if Textract fails?
```python
try:
    textract_result = textract_service.extract_text_from_s3(...)
except HTTPException as e:
    # Falls back gracefully
    # Logs error: "Textract processing failed"
    # Returns error to user
```

### What if OpenAI fails?
```python
try:
    extracted_data = openai_service.extract_insurance_data(...)
except HTTPException as e:
    # Falls back gracefully
    # Logs error: "OpenAI extraction failed"
    # Can retry or use fallback extraction
```

### What if text is empty?
```python
if not extracted_text or len(extracted_text) < 50:
    raise HTTPException(
        status_code=400,
        detail="Document appears to be empty or unreadable"
    )
```

---

## 🎓 Summary

### The Pipeline
```
📄 Insurance PDF
    ↓
👁️ AWS Textract reads text (OCR)
    ↓ (raw text)
🧠 OpenAI GPT-4 understands & structures
    ↓ (JSON with confidence)
💾 Save to Database (both formats)
    ↓
📊 Display in UI for review
    ↓
📑 Export to ACORD 125 PDF
```

### Key Takeaways
1. **Textract = OCR** (reads characters from images/PDFs)
2. **OpenAI = Intelligence** (understands context & structures data)
3. **Together = Complete Solution** (automated ACORD extraction)
4. **Confidence Scores** = Quality assurance (flag uncertain data)
5. **Multi-document** = Combines all pages into one extraction

---

## 📚 Related Files
- `/backend/app/services/textract_service.py` - AWS Textract integration
- `/backend/app/services/openai_service.py` - OpenAI GPT-4 integration  
- `/backend/app/services/ai_extraction_service.py` - Main orchestration
- `/backend/app/core/acord_schema.py` - ACORD 125 schema definitions

---

**Questions?**
- Textract can also extract tables (not currently used)
- OpenAI generates risk narratives from extracted data
- System validates and formats all extracted data (phone numbers, dates, etc.)
- All extraction progress is tracked in real-time (0-100%)


