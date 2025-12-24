# 🧪 Testing Guide for New Features

**Date:** Testing Session  
**Status:** All services running ✅

## 🚀 Quick Start

Your Docker services are already running:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

---

## 📋 New Features to Test

### ✅ Feature 1: Context-Aware Gap Detection
**Status:** Implemented  
**Priority:** High

### ✅ Feature 2: Multi-Form Support (ACORD 126, 130, 140)
**Status:** Implemented  
**Priority:** High

### ✅ Feature 3: Editable Data Review
**Status:** Implemented  
**Priority:** High

### ✅ Feature 4: Improved Progress Display
**Status:** Implemented  
**Priority:** High

---

## 🧪 Test Scenarios

### Test 1: Multi-Form Support

**Objective:** Test the ability to generate multiple ACORD forms (125, 126, 130, 140) from extracted data.

**Steps:**
1. Navigate to http://localhost:3000
2. Log in (or create an account if needed)
3. Go to **Upload** page
4. Create a new submission
5. Upload test documents (see Test Documents section below)
6. Click **"Start AI Extraction"**
7. Wait for extraction to complete (watch the progress display)
8. Go to **Review** page
9. Look for **"Generate ACORD Forms"** section
10. Test the following:
    - ✅ Select individual forms (ACORD 125, 126, 130, 140)
    - ✅ Select multiple forms at once
    - ✅ Generate and download individual forms
    - ✅ Generate and download multiple forms as a batch

**Expected Results:**
- Form selection UI appears in review page
- Can select one or multiple forms
- Forms are generated with extracted data
- PDFs download successfully
- Forms are properly filled with data

**Test Documents:**
- Use Client 001 documents for Commercial Auto (ACORD 125, 137)
- Use Client 002 documents for Property/GL (ACORD 125, 126, 140)
- Use Client 003 documents for Workers Comp (ACORD 130)

---

### Test 2: Context-Aware Gap Detection

**Objective:** Test the intelligent gap detection that identifies missing data based on coverage types.

**Steps:**
1. Navigate to **Upload** page
2. Create a new submission for **Client 001** (Trucking Company)
3. Upload these documents:
   - `client-001-application.md`
   - `client-001-financial-statement.md`
   - `client-001-loss-runs.md`
   - `client-001-vehicle-schedule.md`
   - `client-001-driver-list.md`
4. Click **"Start AI Extraction"**
5. Wait for extraction to complete
6. Go to **Review** page
7. Click **"Analyze Gaps"** or look for gap detection section
8. Review the gap report

**Expected Results:**
- ✅ System detects "Commercial Auto" and "Motor Carrier" coverages
- ✅ System recognizes uploaded documents (loss runs, vehicle schedule, driver list)
- ✅ System flags missing DOT/MC numbers
- ✅ System flags missing MVR reports (mentioned but not uploaded)
- ✅ System does NOT flag vehicle VINs (they're in the documents)
- ✅ System does NOT flag driver info (it's complete)
- ✅ Completeness score: 65-75%

**Missing Items Should Include:**
- ❌ MVR Reports
- ❌ DOT Number document/verification
- ❌ MC Number document/verification
- ⚠️ Annual mileage

**Present Items (Should NOT be flagged):**
- ✅ Business name, FEIN
- ✅ Vehicle VINs (all 15 vehicles)
- ✅ Driver information (all 12 drivers)
- ✅ Loss runs (5-year history)
- ✅ Annual revenue

---

### Test 3: Editable Data Review

**Objective:** Test the inline editing functionality for extracted data.

**Steps:**
1. Navigate to **Review** page with an existing submission
2. Look for extracted data fields displayed in the review interface
3. Test editing:
   - ✅ Click on any field to edit it
   - ✅ Make changes to field values
   - ✅ Verify auto-save (should save after 1.5 seconds)
   - ✅ Check for "unsaved changes" banner if multiple edits
   - ✅ Test "Save All" button
   - ✅ Test "Discard" button
4. After editing:
   - ✅ Regenerate PDF with updated data
   - ✅ Verify changes appear in the regenerated PDF
   - ✅ Check edit history (if available)

**Expected Results:**
- Fields are clickable and editable
- Changes auto-save with debouncing
- Unsaved changes banner appears when needed
- Regenerated PDFs include edited values
- Original values are tracked for comparison

---

### Test 4: Improved Progress Display

**Objective:** Test the real-time progress updates during AI extraction.

**Steps:**
1. Navigate to **Upload** page
2. Create a new submission
3. Upload a document (PDF, Word, or Excel)
4. Click **"Start AI Extraction"**
5. **Watch the progress display carefully:**
   - ✅ Progress card appears immediately
   - ✅ Step 1 (Document Analysis) shows at 10%
   - ✅ Progress updates smoothly during Textract (20-40%)
   - ✅ Progress updates during OpenAI processing (45-55%)
   - ✅ Progress updates during risk narrative (60-70%)
   - ✅ Progress updates during ACORD mapping (75-85%)
   - ✅ Progress reaches 100% when complete
6. **Open browser DevTools → Console** to see progress logs

**Expected Results:**
- No long pauses at 40% (old bug)
- Progress updates every 2 seconds during processing
- Steps advance: 1 → 2 → 3 → 4 → 5
- Console shows: `📊 Extraction Status Update: { progress: X }`
- Progress timeline: 10% → 20% → 27% → 33% → 40% → 45% → 55% → 60% → 70% → 75% → 85% → 90% → 95% → 100%

**Console Output Should Show:**
```
📊 Extraction Status Update: { status: 'processing', progress: 10, ... }
📊 Extraction Status Update: { status: 'processing', progress: 20, ... }
📊 Extraction Status Update: { status: 'processing', progress: 40, ... }
📊 Extraction Status Update: { status: 'processing', progress: 45, ... }
📊 Extraction Status Update: { status: 'processing', progress: 55, ... }
📊 Extraction Status Update: { status: 'processing', progress: 60, ... }
📊 Extraction Status Update: { status: 'processing', progress: 70, ... }
📊 Extraction Status Update: { status: 'processing', progress: 85, ... }
📊 Extraction Status Update: { status: 'processing', progress: 95, ... }
✅ Extraction completed - loading results
```

---

## 📁 Test Documents Location

Test documents are located in: `/Users/kemepade/MyInsurance/test-documents/`

### Client 001: ABC Long Haul Trucking LLC
- `client-001-application.md`
- `client-001-financial-statement.md`
- `client-001-loss-runs.md`
- `client-001-vehicle-schedule.md`
- `client-001-driver-list.md`

**Coverage Types:** Commercial Auto, Motor Carrier, General Liability

### Client 002: Bella Italia Restaurant LLC
- `client-002-application.md`
- `client-002-financial-statement.md`
- `client-002-loss-runs.md`
- `client-002-property-schedule.md`
- `client-002-liquor-license.md`

**Coverage Types:** General Liability, Property, Liquor Liability

### Client 003: Smith & Associates Construction Inc.
- `client-003-application.md`
- `client-003-payroll-breakdown.md`
- `client-003-experience-mod.md`
- `client-003-loss-runs.md`
- `client-003-osha-logs.md`

**Coverage Types:** Workers Compensation

---

## 🔍 API Testing

You can also test features directly via the API:

### Test Gap Detection API
```bash
# Get gap detection for a submission
curl -X GET "http://localhost:8000/api/gap-detection/{submission_id}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Multi-Form API
```bash
# List available forms
curl -X GET "http://localhost:8000/api/acord/forms/available"

# Generate multiple forms
curl -X POST "http://localhost:8000/api/acord/forms/fill-multiple" \
  -H "Content-Type: application/json" \
  -d '{
    "submission_id": "YOUR_SUBMISSION_ID",
    "form_types": ["ACORD_125", "ACORD_126", "ACORD_130"]
  }'
```

### Test Field Editing API
```bash
# Update a single field
curl -X PATCH "http://localhost:8000/api/extraction/{submission_id}/field" \
  -H "Content-Type: application/json" \
  -d '{
    "field_name": "business_name",
    "field_value": "Updated Business Name"
  }'
```

**Full API Documentation:** http://localhost:8000/docs

---

## ✅ Testing Checklist

### Multi-Form Support
- [ ] Can select individual ACORD forms (125, 126, 130, 140)
- [ ] Can select multiple forms at once
- [ ] Forms generate successfully with extracted data
- [ ] PDFs download correctly
- [ ] Forms are properly filled

### Gap Detection
- [ ] Coverage types are detected correctly
- [ ] Missing documents are identified
- [ ] Missing data fields are flagged
- [ ] Completeness score is accurate
- [ ] Gap report is clear and actionable

### Editable Data Review
- [ ] Fields are clickable and editable
- [ ] Changes auto-save (1.5 second delay)
- [ ] Unsaved changes banner appears
- [ ] "Save All" and "Discard" work correctly
- [ ] Regenerated PDFs include edits
- [ ] Edit history is tracked

### Progress Display
- [ ] Progress appears immediately
- [ ] No long pauses at 40%
- [ ] Progress updates smoothly
- [ ] Steps advance correctly
- [ ] Console logs show progress updates

---

## 🐛 Troubleshooting

### Services Not Running
```bash
# Check status
docker ps -a --filter "name=docwheech"

# Start services
cd /Users/kemepade/MyInsurance
docker-compose up -d

# View logs
docker-compose logs -f
```

### Backend Errors
```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Frontend Errors
```bash
# Check frontend logs
docker-compose logs frontend

# Restart frontend
docker-compose restart frontend
```

### Database Issues
```bash
# Connect to database
docker-compose exec postgres psql -U docwheech_user -d docwheech

# Check tables
\dt

# View submissions
SELECT id, business_name, extraction_status FROM submissions;
```

---

## 📊 Expected Test Results Summary

| Feature | Test Status | Notes |
|---------|-------------|-------|
| Multi-Form Support | ⏳ Pending | Test with Client 001, 002, 003 |
| Gap Detection | ⏳ Pending | Test with Client 001 (should show 65-75% complete) |
| Editable Review | ⏳ Pending | Test inline editing and auto-save |
| Progress Display | ⏳ Pending | Verify no 40% freeze, smooth updates |

---

## 🎯 Next Steps After Testing

1. **Document any bugs or issues** found during testing
2. **Verify all features work as expected**
3. **Test edge cases** (empty submissions, large files, etc.)
4. **Performance testing** (multiple concurrent extractions)
5. **User acceptance testing** with real insurance documents

---

**Happy Testing! 🚀**















