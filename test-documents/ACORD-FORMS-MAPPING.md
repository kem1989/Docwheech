# ACORD Forms Mapping for Test Client Scenarios

This document outlines which ACORD forms should be filled for each client scenario based on their coverage requests.

---

## Overview: ACORD Form Types

| Form | Full Name | Purpose | Status |
|------|-----------|---------|--------|
| **ACORD 125** | Commercial Insurance Application | Base application with business info, lines of business | ✅ Supported |
| **ACORD 126** | Commercial General Liability Section | Detailed GL coverage information | ✅ Supported |
| **ACORD 127** | Commercial Auto Section | Detailed auto/trucking coverage information | ✅ Supported |
| **ACORD 130** | Workers Compensation Application | Detailed WC coverage information | ✅ Supported |
| **ACORD 140** | Property Section | Detailed property coverage information | ✅ Supported |

**Note:** ACORD 125 is typically required for ALL commercial insurance applications as it contains the base business information and lists the lines of business requested.

---

## Client 001: ABC Long Haul Trucking LLC

### Coverage Requested:
- ✅ Commercial Auto Liability
- ✅ Motor Carrier Coverage
- ✅ General Liability

### ACORD Forms to Fill:

| Form | Required? | Why |
|------|-----------|-----|
| **ACORD 125** | ✅ **YES** | Base commercial application - contains business info, lines of business (Auto, GL) |
| **ACORD 126** | ✅ **YES** | General Liability detailed information |
| **ACORD 127** | ✅ **YES** | Commercial Auto detailed information |

### Current Implementation:
- ✅ ACORD 125 - Can be filled
- ✅ ACORD 126 - Can be filled  
- ✅ ACORD 127 - Can be filled

### What Data Goes Where:

**ACORD 125:**
- Business name, FEIN, address
- Lines of business: Commercial Auto, Motor Carrier, General Liability
- Nature of business description
- Premises information
- Prior carriers
- Loss history summary

**ACORD 126 (General Liability):**
- GL-specific questions
- Products/completed operations details
- Additional insured requests
- GL limits requested

**ACORD 127 (Commercial Auto):**
- Vehicle schedule (15 power units, 20 trailers)
- Driver information (12 drivers)
- DOT/MC numbers
- Cargo types
- Radius of operations
- Garage locations
- Liability limits (CSL, BI/PD)
- Physical damage coverage

---

## Client 002: Bella Italia Restaurant LLC

### Coverage Requested:
- ✅ Commercial General Liability
- ✅ Commercial Property
- ✅ Liquor Liability

### ACORD Forms to Fill:

| Form | Required? | Why |
|------|-----------|-----|
| **ACORD 125** | ✅ **YES** | Base commercial application - contains business info, lines of business (GL, Property) |
| **ACORD 126** | ✅ **YES** | General Liability detailed information |
| **ACORD 140** | ✅ **YES** | Property detailed information (building, contents, values) |

### Current Implementation:
- ✅ ACORD 125 - Can be filled
- ✅ ACORD 126 - Can be filled
- ✅ ACORD 140 - Can be filled

### What Data Goes Where:

**ACORD 125:**
- Business name, FEIN, address
- Lines of business: General Liability, Property, Liquor Liability
- Nature of business (restaurant operations)
- Premises information (2500 Restaurant Row)
- Prior carriers
- Loss history summary

**ACORD 126 (General Liability):**
- GL-specific questions
- Products/completed operations (food service)
- Additional insured requests
- GL limits requested ($1M/$2M)

**ACORD 140 (Property):**
- Property address details
- Building information (4,500 sq ft, masonry construction, year built 2012)
- Building value: $850,000 (replacement cost)
- Contents breakdown: $180,000 (kitchen equipment, furniture, inventory)
- Construction type, year built, square footage
- Interest: Tenant
- Fire protection systems

**Note:** Liquor Liability details would typically be included in ACORD 125 or a separate liquor liability form, depending on carrier requirements.

---

## Client 003: Smith & Associates Construction Inc.

### Coverage Requested:
- ✅ Workers Compensation

### ACORD Forms to Fill:

| Form | Required? | Why |
|------|-----------|-----|
| **ACORD 125** | ✅ **YES** | Base commercial application - contains business info, line of business (Workers Comp) |
| **ACORD 130** | ✅ **YES** | Workers Compensation detailed information |

### Current Implementation:
- ✅ ACORD 125 - Can be filled
- ✅ ACORD 130 - Can be filled

### What Data Goes Where:

**ACORD 125:**
- Business name, FEIN, address
- Line of business: Workers Compensation
- Nature of business (general contractor)
- Premises information
- Prior carriers
- Loss history summary

**ACORD 130 (Workers Compensation):**
- Payroll by classification code (6 different codes)
  - Class 5606 (Carpentry): $480,000
  - Class 5437 (Drywall): $360,000
  - Class 5474 (Painting): $240,000
  - Class 5190 (Electrical): $180,000
  - Class 8810 (Clerical): $96,000
  - Class 9002 (Executive): $360,000
- Total annual payroll: $1,716,000
- States of operation: Texas (primary), Oklahoma (occasional)
- Experience modification: 1.05
- Owner/officer payroll: $300,000 (included)
- Subcontractor information

---

## Summary Table

| Client | Coverage Types | Forms to Fill | Status |
|--------|---------------|---------------|--------|
| **001 - Trucking** | Auto, Motor Carrier, GL | ACORD 125, ACORD 126, ACORD 127 | ✅ Ready |
| **002 - Restaurant** | GL, Property, Liquor | ACORD 125, ACORD 126, ACORD 140 | ✅ Ready |
| **003 - Construction** | Workers Comp | ACORD 125, ACORD 130 | ✅ Ready |

---

## Testing Workflow

### For Each Client:

1. **Upload Documents** → Extract data using AI
2. **Review Extracted Data** → Verify accuracy
3. **Run Gap Detection** → Identify missing information
4. **Fill Data Gaps** → Use Editable Data Review (Feature 3)
5. **Generate ACORD Forms:**
   - Select forms based on coverage types
   - Generate forms from extracted data
   - Download filled PDFs
6. **Verify Forms** → Check all required fields are populated

---

## Form Selection Logic

The system automatically suggests forms based on detected coverages:

```
IF coverage includes "COMMERCIAL_GENERAL_LIABILITY":
    → Suggest ACORD 125 + ACORD 126

IF coverage includes "COMMERCIAL_PROPERTY":
    → Suggest ACORD 125 + ACORD 140

IF coverage includes "WORKERS_COMPENSATION":
    → Suggest ACORD 125 + ACORD 130

IF coverage includes "BUSINESS_AUTO" or "MOTOR_CARRIER" or "TRUCKERS":
    → Suggest ACORD 125 + ACORD 127
```

**Note:** ACORD 125 is always included as it's the base application form.

---

## Future Enhancements

- [x] ~~Add ACORD 127 (Commercial Auto Section) support~~ ✅ Completed
- [ ] Add ACORD 835 (Liquor Liability) support
- [x] ~~Auto-select forms based on coverage detection~~ ✅ Implemented
- [ ] Form dependency validation (e.g., "ACORD 126 requires ACORD 125")
- [ ] Verify ACORD 127 PDF field mappings against actual template

