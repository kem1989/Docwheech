# MyInsurance Application - Complete Workflow Documentation

> **Last Updated:** December 2, 2025  
> **Purpose:** Reference guide for testing the complete extraction and form generation flow

---

## 🚛 Complete Workflow: Client-001 Trucking Submission

### Documents Being Uploaded
Based on `test-documents/client-001-application.md`:
- **Application** - Contains: Legal name, FEIN, contact info, **"Coverages Requested: Commercial Auto Liability, General Liability"**
- **Vehicle Schedule** - 15 power units, 20 trailers with VINs
- **Driver List** - 12 drivers with licenses, DOBs
- **Financial Statement** - $2.4M annual revenue
- **Loss Runs** - Claims history

---

## Step-by-Step Workflow

### 1️⃣ Document Upload (Frontend → S3)
```
User uploads documents → Frontend calls /api/files/upload
                      → Documents stored in S3
                      → Document metadata saved to database
```

### 2️⃣ Start Extraction (Review Page)
```
User clicks "Start AI Extraction"
        ↓
POST /api/extraction/extract
        ↓
Background task started: _run_extraction_task()
```

### 3️⃣ Phase 1: Base Extraction (20-50%)

**Step 3a: Text Extraction (AWS Textract)**
```
For each document:
    → textract_service.extract_text_from_s3()
    → OCR text extracted from PDFs/images
    → Progress: 20% → 40%
```

**Step 3b: AI Structured Extraction (OpenAI GPT-4)**
```
openai_service.extract_insurance_data()
        ↓
Uses prompt with ACORD 125 schema fields:
- first_named_insured: "ABC Long Haul Trucking LLC"
- fein_or_ssn: "12-3456789"
- coverage_requested: {
    "value": ["Commercial Auto Liability", "General Liability"],
    "source": "EXPLICIT"  ← Found explicitly in document!
  }
- lines_of_business: ["BUSINESS_AUTO", "COMMERCIAL_GENERAL_LIABILITY"]
- nature_of_business.description: "Long-haul freight transportation..."
- premises[0].annual_revenues: "2400000"
        ↓
Progress: 45% → 50%
```

### 4️⃣ Coverage Detection (Two-Tier System)

```python
detect_coverages_from_extraction(extracted_data)
```

**TIER 1: Check Explicit Coverage Requested** ✅
```
coverage_requested.source = "EXPLICIT"
coverage_requested.value = ["Commercial Auto Liability", "General Liability"]
        ↓
Normalized to:
  - BUSINESS_AUTO ✅ (supported via ACORD 127)
  - COMMERCIAL_GENERAL_LIABILITY ✅ (supported via ACORD 126)
```

**TIER 2: Fallback (Only if TIER 1 finds nothing)**
```
- Check lines_of_business field
- Check nature_of_business description
- Infer from business type keywords
```

**Result for Client-001:**
```python
{
  "method": "EXPLICIT",
  "supported_coverages": ["BUSINESS_AUTO", "COMMERCIAL_GENERAL_LIABILITY"],
  "unsupported_coverages": []
}
```

### 5️⃣ Phase 2: Form-Specific Extraction (50-70%)

Based on detected coverages, run parallel extractions:

```python
COVERAGE_TO_FORM_MAP = {
    "COMMERCIAL_GENERAL_LIABILITY": "ACORD_126",
    "WORKERS_COMPENSATION": "ACORD_130",
    "COMMERCIAL_PROPERTY": "ACORD_140",
    "BUSINESS_AUTO": "ACORD_127",
    "MOTOR_CARRIER": "ACORD_127",
    "TRUCKERS": "ACORD_127",
}
```

**Parallel Tasks for Client-001:**

| Coverage | Form | Extraction Function | Data Extracted |
|----------|------|---------------------|----------------|
| `COMMERCIAL_GENERAL_LIABILITY` | ACORD 126 | `extract_acord126_data()` | GL limits, classifications, products/CO |
| `BUSINESS_AUTO` | ACORD 127 | `extract_acord127_data()` | Vehicle schedule (15 units), Driver schedule (12 drivers), DOT#, cargo types |

**ACORD 127 Extraction Output Example:**
```json
{
  "commercial_auto": {
    "vehicle_schedule": [
      {"year": "2022", "make": "Peterbilt", "model": "579", "vin": "1XPWD40X1ED215875"},
      {"year": "2021", "make": "Kenworth", "model": "T680", "vin": "1XKYD49X5KJ269841"}
    ],
    "driver_schedule": [
      {
        "name": "James Wilson",
        "date_of_birth": "1985-03-15",
        "license_number": "TX12345678",
        "license_state": "TX",
        "years_experience": 8,
        "date_hired": "2019-06-01"
      }
    ],
    "motor_carrier_info": {
      "dot_number": "1234567",
      "mc_number": "MC-987654",
      "operation_type": "FOR_HIRE",
      "cargo_types": ["general freight", "palletized goods"],
      "hazmat_hauled": false
    },
    "fleet_summary": {
      "total_vehicles": 15,
      "total_drivers": 12
    }
  }
}
```

### 6️⃣ Merge & Generate ACORD Schema (70-85%)
```
extracted_data = _merge_extraction_results(base_data, form_specific_data)
        ↓
Merged data now contains:
- Base ACORD 125 fields
- general_liability section (from ACORD 126 extraction)
- commercial_auto section (from ACORD 127 extraction)
        ↓
create_acord_schema_from_extraction(extracted_data)
        ↓
Normalized ACORD 125 schema object + form-specific data
```

### 7️⃣ Generate Risk Narrative (75%)
```
openai_service.generate_risk_narrative(extracted_data)
        ↓
"ABC Long Haul Trucking is a regional freight carrier operating 
15 power units across TX, OK, LA, AR. 6 years in business with 
12 drivers. Primary cargo: general freight, non-hazardous..."
```

### 8️⃣ Save Results (85-100%)
```
db_service.save_extraction_results(submission_id, extraction_result)
        ↓
Stored in database:
- extracted_data
- acord_schema
- risk_narrative
- detected_coverages: ["BUSINESS_AUTO", "COMMERCIAL_GENERAL_LIABILITY"]
- form_specific_extractions: ["ACORD_126", "ACORD_127"]
```

---

## 📊 What Gets Displayed (Review Page)

### Extraction Results Panel
| Field | Value | Confidence |
|-------|-------|------------|
| Business Name | ABC Long Haul Trucking LLC | 0.95 |
| FEIN | 12-3456789 | 0.98 |
| Date Started | 2018-01-15 | 0.90 |
| Annual Revenue | $2,400,000 | 0.92 |

### Detected Coverages Badge
```
[Commercial General Liability] [Commercial Auto] 
```

### Two-Phase Extraction Info
```
Phase 1: ACORD 125 base extraction ✅
Phase 2: ACORD_126 (GL), ACORD_127 (Auto) ✅
```

---

## 📋 Gap Detection (When User Clicks "Check Completeness")

```python
gap_detection_service.analyze_submission(extracted_data, acord_schema)
```

### Coverage Detection (Two-Tier again)
```
TIER 1: coverage_requested.source = "EXPLICIT" ✅
        → ["BUSINESS_AUTO", "COMMERCIAL_GENERAL_LIABILITY"]
```

### Requirements Loaded
```python
get_requirements_for_coverages(["BUSINESS_AUTO", "COMMERCIAL_GENERAL_LIABILITY"])
        ↓
Combined requirements from:
- UNIVERSAL_REQUIREMENTS (business name, address, effective date)
- COMMERCIAL_GENERAL_LIABILITY requirements
- BUSINESS_AUTO requirements (vehicle VINs, drivers, DOT#, etc.)
```

### Gap Analysis Results Example
```json
{
  "completeness_score": 85,
  "ready_to_submit": true,
  "detected_coverages": [
    {"code": "BUSINESS_AUTO", "display_name": "Commercial Auto"},
    {"code": "COMMERCIAL_GENERAL_LIABILITY", "display_name": "Commercial General Liability"}
  ],
  "missing_data": [
    {"id": "radius_of_operations", "label": "Radius of Operations", "severity": "important"},
    {"id": "garage_location", "label": "Garage Location", "severity": "important"}
  ],
  "total_requirements": 18,
  "found_items": 15
}
```

---

## 📄 ACORD Forms Available for Generation

### Supported Forms Matrix

| Form | Full Name | Coverages | Status |
|------|-----------|-----------|--------|
| **ACORD 125** | Commercial Insurance Application | ALL | ✅ Supported |
| **ACORD 126** | Commercial General Liability Section | GL, Liquor | ✅ Supported |
| **ACORD 127** | Commercial Auto Section | Auto, Motor Carrier, Truckers | ✅ Supported |
| **ACORD 130** | Workers Compensation Application | WC | ✅ Supported |
| **ACORD 140** | Property Section | Property | ✅ Supported |

### Forms Generated for Client-001

| Form | Purpose | Data Source |
|------|---------|-------------|
| **ACORD 125** | Base Commercial Application | `acord_schema` |
| **ACORD 126** | GL Section | `extracted_data.general_liability` |
| **ACORD 127** | Commercial Auto Section | `extracted_data.commercial_auto` |

### Form Generation Flow
```
User selects forms → POST /api/acord/fill-multiple
        ↓
multi_form_pdf_service.fill_multiple_forms([
    (ACORD_125, acord_schema),
    (ACORD_126, extracted_data.general_liability),
    (ACORD_127, extracted_data.commercial_auto)
])
        ↓
Filled PDFs saved to S3
        ↓
Download links returned to user
```

---

## 🔍 Key Files Reference

### Backend Services
| File | Purpose |
|------|---------|
| `backend/app/services/openai_service.py` | GPT-4 extraction, coverage detection |
| `backend/app/services/ai_extraction_service.py` | Orchestrates Phase 1 & 2 extraction |
| `backend/app/services/gap_detection_service.py` | Data completeness analysis |
| `backend/app/services/multi_form_pdf_service.py` | PDF form filling |
| `backend/app/core/coverage_requirements.py` | Coverage requirement matrix |

### API Endpoints
| Endpoint | Purpose |
|----------|---------|
| `POST /api/extraction/extract` | Start AI extraction |
| `GET /api/extraction/results/{id}` | Get extraction results |
| `POST /api/gaps/analyze` | Run gap detection |
| `POST /api/acord/fill-multiple` | Generate filled PDFs |

---

## 📊 Summary: Client-001 Complete Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  1. UPLOAD: 5 documents (application, vehicles, drivers, etc.)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. TEXTRACT: OCR all documents, combine text                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. PHASE 1: GPT-4 extracts ACORD 125 base fields               │
│     + coverage_requested: ["Commercial Auto", "GL"] (EXPLICIT)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. COVERAGE DETECTION (Two-Tier):                              │
│     TIER 1: Found EXPLICIT → BUSINESS_AUTO, GL                  │
│     Mapped to: ACORD_126, ACORD_127                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. PHASE 2: Parallel form-specific extraction                  │
│     - extract_acord126_data() → GL limits, classifications      │
│     - extract_acord127_data() → 15 vehicles, 12 drivers, DOT#   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  6. MERGE & DISPLAY: Combined extracted data shown in Review    │
│     - Risk narrative generated                                  │
│     - Editable fields for user corrections                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  7. GAP DETECTION: Check completeness for Auto + GL             │
│     Score: 85% | Missing: radius, garage location               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  8. FORM GENERATION: Fill ACORD 125 + 126 + 127                 │
│     - Vehicle schedule → ACORD 127 Page 3                       │
│     - Driver schedule → ACORD 127 Page 1                        │
│     - GL info → ACORD 126                                       │
│     → Download filled PDFs                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing Checklist

### Client-001 (Trucking) - Expected Results
- [ ] Coverage detected: `BUSINESS_AUTO`, `COMMERCIAL_GENERAL_LIABILITY`
- [ ] Detection method: `EXPLICIT` (found "Coverages Requested" in document)
- [ ] Phase 2 forms: `ACORD_126`, `ACORD_127`
- [ ] Vehicles extracted: 15
- [ ] Drivers extracted: 12
- [ ] Forms available: ACORD 125, 126, 127

### Client-002 (Restaurant) - Expected Results
- [ ] Coverage detected: `COMMERCIAL_GENERAL_LIABILITY`, `COMMERCIAL_PROPERTY`, `LIQUOR_LIABILITY`
- [ ] Phase 2 forms: `ACORD_126`, `ACORD_140`
- [ ] Forms available: ACORD 125, 126, 140

### Client-003 (Construction) - Expected Results
- [ ] Coverage detected: `WORKERS_COMPENSATION`
- [ ] Phase 2 forms: `ACORD_130`
- [ ] Forms available: ACORD 125, 130

---

## 📝 Recent Updates (December 2, 2025)

1. **Two-Tier Coverage Detection** - Now checks explicit "Coverage Requested" first before inferring
2. **ACORD 127 Support Added** - Commercial Auto extraction and form filling
3. **Document Gap Detection Removed** - Now focuses purely on data completeness
4. **619 PDF Field Mappings** - ACORD 127 field names mapped from actual PDF


