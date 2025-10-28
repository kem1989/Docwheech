# ACORD 125 Form Data Structure
## Commercial Insurance Application - Field Mapping Schema

---

## Page 1 of 4: Application Header & Basic Information

### Date of Filing the application
```json
{
  "Date": {
    "Date_application": "date (MM/DD/YYYY)",
  }
}
```

### Agency Information
-- Important fields are (name, address, contact_name, phone, email)
```json
{
  "agency": {
    "name": "string",
    "code": "string",
    "subcode": "string",
    "agency_customer_id": "string",
    "address": "string",
    "contact_name": "string",
    "phone": "string (format: (A/C, No, Ext))",
    "fax": "string (format: (A/C, No))",
    "email": "string"
  }
}
```

### Transaction Status

-- Important (type e,g QUOTE)
```json
{
  "transaction_status": {
    "type": "enum [QUOTE, RENEWAL, ISSUE_POLICY, BOUND, CANCEL, CHANGE]",
    "bound_date": "date (MM/DD/YYYY)",
    "bound_time": "time (HH:MM AM/PM)"
  }
}
```

### Carrier Information
```json
{
  "carrier": {
    "name": "string",
    "naic_code": "string",
    "policy_number": "string",
    "company_policy_program_name": "string",
    "program_code": "string"
  }
}
```

### Policy Information
--- Important (proposed_effective_date, proposed_expiration_date and billing_plan)
```json
{
  "policy": {
    "proposed_effective_date": "date (MM/DD/YYYY)",
    "proposed_expiration_date": "date (MM/DD/YYYY)",
    "billing_plan": "string",
    "payment_plan": "string",
    "audit": "boolean",
    "deposit_premium": "decimal",
    "minimum_premium": "decimal",
    "method_of_payment": "enum [DIRECT, AGENCY]"
  }
}
```

### Lines of Business & Premiums
-- Important (Line of Business must be ticked)
```json
{
  "lines_of_business": [
    {
      "line": "COMMERCIAL_GENERAL_LIABILITY",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "COMMERCIAL_PROPERTY",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "BUSINESS_AUTO",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "WORKERS_COMPENSATION",
      "selected": "boolean (ACORD 130)",
      "premium": "decimal"
    },
    {
      "line": "UMBRELLA",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "BUSINESS_OWNERS",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "GARAGE_AND_DEALERS",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "CRIME",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "BOILER_AND_MACHINERY",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "COMMERCIAL_INLAND_MARINE",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "CYBER_AND_PRIVACY",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "FIDUCIARY_LIABILITY",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "LIQUOR_LIABILITY",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "MOTOR_CARRIER",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "TRUCKERS",
      "selected": "boolean",
      "premium": "decimal"
    },
    {
      "line": "YACHT",
      "selected": "boolean",
      "premium": "decimal"
    }
  ]
}
```

### Attachments/Supplements
-- Important (Based on the document submitted, we will know the Attachments)
```json
{
  "attachments": [
    "ACORD_101_ADDITIONAL_REMARKS",
    "ACORD_823_ADDITIONAL_PREMISES",
    "ADDITIONAL_INTEREST_SCHEDULE",
    "ADDITIONAL_PREMISES_INFORMATION_SCHEDULE",
    "APARTMENT_BUILDING_SUPPLEMENT",
    "CONDO_ASSN_BYLAWS",
    "CONTRACTORS_SUPPLEMENT",
    "COVERAGES_SCHEDULE",
    "DRIVER_INFORMATION_SCHEDULE",
    "HOTEL_MOTEL_SUPPLEMENT",
    "INTERNATIONAL_LIABILITY_EXPOSURE_SUPPLEMENT",
    "INTERNATIONAL_PROPERTY_EXPOSURE_SUPPLEMENT",
    "LOSS_SUMMARY",
    "PREMIUM_PAYMENT_SUPPLEMENT",
    "PROFESSIONAL_LIABILITY_SUPPLEMENT",
    "RESTAURANT_TAVERN_SUPPLEMENT",
    "STATEMENT_SCHEDULE_OF_VALUES",
    "STATE_SUPPLEMENT",
    "VACANT_BUILDING_SUPPLEMENT",
    "VEHICLE_SCHEDULE",
    "ACCOUNTS_RECEIVABLE_VALUABLE_PAPERS",
    "DEALERS_SECTION",
    "ELECTRONIC_DATA_PROCESSING_SECTION",
    "GLASS_AND_SIGN_SECTION",
    "INSTALLATION_BUILDERS_RISK_SECTION",
    "OPEN_CARGO_SECTION"
  ]
}
```

### Underwriter Information
```json
{
  "underwriter": {
    "name": "string",
    "office": "string",
    "date": "date (MM/DD/YYYY)"
  }
}
```

---

## Page 2 of 4: Applicant Information Section

### First Named Insured

-- Important (name, mailing_address, business_structure, fein_or_ssn, business_phone, website_address)
```json
{
  "first_named_insured": {
    "name": "string",
    "mailing_address": "string (including ZIP+4)",
    "business_structure": "enum [INDIVIDUAL, PARTNERSHIP, CORPORATION, LLC, JOINT_VENTURE, NOT_FOR_PROFIT_ORG, SUBCHAPTER_S_CORPORATION, TRUST]",
    "number_of_members": "integer (if LLC)",
    "number_of_managers": "integer (if LLC with managers)",
    "naics_code": "string",
    "sic_code": "string",
    "gl_code": "string",
    "fein_or_ssn": "string",
    "business_phone": "string",
    "website_address": "string"
  }
}
```

### Other Named Insureds (Array - Can have multiple)

-- Important, if they have other names insured, you should fill in the details as we did in first insured
```json
{
  "other_named_insureds": [
    {
      "name": "string",
      "mailing_address": "string (including ZIP+4)",
      "business_structure": "enum [INDIVIDUAL, PARTNERSHIP, CORPORATION, LLC, JOINT_VENTURE, NOT_FOR_PROFIT_ORG, SUBCHAPTER_S_CORPORATION, TRUST]",
      "number_of_members": "integer",
      "number_of_managers": "integer",
      "naics_code": "string",
      "sic_code": "string",
      "gl_code": "string",
      "fein_or_ssn": "string",
      "business_phone": "string",
      "website_address": "string"
    }
  ]
}
```

### Contact Information (Array - Can have multiple contacts)
-- Important (contact_type, contact_name, primary_email, primary_phone). If there is a second contact, fill the other section with the corresponding info
```json
{
  "contacts": [
    {
      "contact_type": "string",
      "contact_name": "string",
      "primary_email": "string",
      "secondary_email": "string",
      "primary_phone": "string (format: (A/C, No, Ext))",
      "primary_phone_type": "enum [HOME, BUSINESS, CELL]",
      "secondary_phone": "string",
      "secondary_phone_type": "enum [HOME, BUSINESS, CELL]"
    }
  ]
}
```

### Nature of Business
-- Important (date_business_started, business_type, description_of_primary_operations)
```json
{
  "nature_of_business": {
    "date_business_started": "date (MM/DD/YYYY)",
    "business_type": "array [MANUFACTURING, CONTRACTOR, RETAIL, WHOLESALE, SERVICE, OFFICE, RESTAURANT, INSTITUTIONAL, CONDOMINIUMS, APARTMENTS]",
    "description_of_primary_operations": "text",
    "retail_stores_or_service_operations": "boolean",
    "retail_percent_of_total_sales": "decimal",
    "installation_service_repair_work": "boolean",
    "off_premises_installation_service_repair": "boolean",
    "description_of_operations_other_named_insureds": "text"
  }
}
```

### Premises Information (Array - Up to 4 locations on this page, use ACORD 823 for more)

-- Important (location_number, building_number, street_address, city, county, state, zip, description_of_operations, [these field are important but it depends - interest, number_full_time_employee, number_part_time_employee], annual_revenues, total_building_area_sqft)
```json
{
  "premises": [
    {
      "location_number": "integer",
      "building_number": "integer",
      "street_address": "string",
      "city": "string",
      "county": "string",
      "state": "string (2-letter code)",
      "zip": "string (ZIP+4)",
      "city_limits": "boolean",
      "description_of_operations": "text",
      "interest": "enum [OWNER, TENANT]",
      "owner_or_tenant_inside": "boolean",
      "owner_or_tenant_outside": "boolean",
      "number_full_time_employees": "integer",
      "number_part_time_employees": "integer",
      "annual_revenues": "decimal",
      "occupied_area_sq_ft": "decimal",
      "total_building_area_sq_ft": "decimal",
      "open_to_public_area_sq_ft": "decimal",
      "any_area_leased_to_others": "boolean"
    }
  ]
}
```

### Additional Interest (Not all fields apply - provide only necessary data)
-- Important (Interests, ) We need to understand what Additional Interest means
```json
{
  "additional_interests": [
    {
      "name_and_address": "string",
      "interest_type": "enum [ADDITIONAL_INSURED, LOSS_PAYEE, MORTGAGEE, LIENHOLDER, LENDERS_LOSS_PAYABLE]",
      "reason_for_interest": "enum [OWNER, LEASEBACK, WARRANTY, BREACH_OF_CONTRACT, TRUSTEE, REGISTRANT, CO_OWNER, AS_LESSOR, INSURED_EMPLOYEE]",
      "interest_in_item_number": {
        "location": "string",
        "building": "string",
        "vehicle": "string",
        "boat": "string",
        "aircraft": "string",
        "item": "string",
        "class": "string"
      },
      "item_description": "string",
      "interest_rank": "string",
      "reference_loan_number": "string",
      "lien_amount": "decimal",
      "interest_end_date": "date",
      "phone": "string",
      "fax": "string",
      "email": "string",
      "evidence_to_send": "array [CERTIFICATE, POLICY, SEND_BILL]"
    }
  ]
}
```

---

## Page 3 of 4: General Information & Prior Carrier

-- Important (These questions must be answered, because its a General Question)
### General Information Questions (All Y/N with explanations)
```json
{
  "general_information": {
    "parent_company": {
      "is_subsidiary": "boolean",
      "parent_company_name": "string",
      "relationship_description": "string",
      "percent_owned": "decimal"
    },
    "subsidiaries": {
      "has_subsidiaries": "boolean",
      "subsidiaries": [
        {
          "subsidiary_company_name": "string",
          "relationship_description": "string",
          "percent_owned": "decimal"
        }
      ]
    },
    "safety_program": {
      "has_formal_safety_program": "boolean",
      "has_safety_manual": "boolean",
      "monthly_meetings": "boolean",
      "osha_position": "boolean"
    },
    "flammables_exposure": {
      "has_exposure": "boolean",
      "explanation": "text"
    },
    "other_insurance_with_company": {
      "has_other_insurance": "boolean",
      "policies": [
        {
          "line_of_business": "string",
          "policy_number": "string"
        }
      ]
    },
    "policy_declined_cancelled_nonrenewed": {
      "has_occurred": "boolean",
      "occurrences": [
        {
          "occur_date": "date",
          "explanation": "text",
          "reason": "enum [UNDERWRITING, NON_PAYMENT, NON_RENEWAL, AGENT_NO_LONGER_REPRESENTS_CARRIER]",
          "condition_corrected": "text",
          "resolution": "text",
          "resolve_date": "date"
        }
      ]
    },
    "sexual_abuse_discrimination_claims": {
      "has_past_losses_or_claims": "boolean",
      "explanation": "text"
    },
    "fraud_arson_conviction": {
      "has_conviction": "boolean",
      "explanation": "text"
    },
    "fire_safety_code_violations": {
      "has_uncorrected_violations": "boolean",
      "occurrences": [
        {
          "occur_date": "date",
          "explanation": "text",
          "resolution": "text",
          "resolve_date": "date"
        }
      ]
    },
    "foreclosure_bankruptcy": {
      "has_occurred": "boolean",
      "explanation": "text"
    },
    "judgement_or_lien": {
      "has_judgement_or_lien": "boolean",
      "explanation": "text"
    },
    "business_in_trust": {
      "is_in_trust": "boolean",
      "name_of_trust": "string"
    },
    "foreign_operations": {
      "has_foreign_operations": "boolean",
      "explanation": "text (If YES, attach ACORD 815 for Liability and/or ACORD 816 for Property)"
    },
    "other_business_ventures": {
      "has_other_ventures": "boolean",
      "explanation": "text"
    },
    "drones": {
      "owns_leases_operates_drones": "boolean",
      "description_of_use": "text",
      "hires_others_to_operate": "boolean",
      "hired_drone_use_description": "text"
    }
  }
}
```

### Prior Carrier Information (Can have multiple entries)

--- Important (carrier_name, policy_number, effective_date, expiration_date)
```json
{
  "prior_carriers": [
    {
      "category": "enum [GENERAL_LIABILITY, AUTOMOBILE, PROPERTY, OTHER]",
      "carrier_name": "string",
      "policy_number": "string",
      "effective_date": "date",
      "expiration_date": "date",
      "premium": "decimal",
      "years_with_carrier": "integer"
    }
  ]
}
```

---

## Page 4 of 4: Loss History & Signatures
--- Important (Check box if no Loss History, If Loss History available then important fields are number_of_years, )
### Loss History
```json
{
  "loss_history": {
    "number_of_years": "integer (typically 3-5 years)",
    "has_no_losses": "boolean",
    "total_losses_amount": "decimal",
    "losses": [
      {
        "date_of_occurrence": "date",
        "date_of_claim": "date",
        "line_type": "string (e.g., GL, Auto, Property, WC)",
        "description_of_occurrence": "text",
        "amount_paid": "decimal",
        "amount_reserved": "decimal",
        "claim_open": "boolean",
        "subrogation": "boolean"
      }
    ]
  }
}
```

### Prior Carrier Information (Continued)
```json
{
  "additional_prior_carriers": [
    {
      "category": "enum [GENERAL_LIABILITY, AUTOMOBILE, PROPERTY, OTHER]",
      "carrier_name": "string",
      "policy_number": "string",
      "effective_date": "date",
      "expiration_date": "date",
      "premium": "decimal",
      "years_with_carrier": "integer"
    }
  ]
}
```

### Remarks / Processing Instructions
```json
{
  "remarks": "text (Use ACORD 101 Additional Remarks Schedule if more space needed)"
}
```

### Fraud Warnings & Privacy Notice
```json
{
  "acknowledgements": {
    "privacy_notice_given": "boolean",
    "applicant_initials": "string"
  }
}
```

### Signatures
--- Important (signatures -applicant, producer[name, signature, date, state_producer_license_number, national_producer_number])
```json
{
  "signatures": {
    "applicant": {
      "signature": "string (digital signature or image)",
      "date": "date (MM/DD/YYYY)"
    },
    "producer": {
      "name": "string",
      "signature": "string (digital signature or image)",
      "date": "date (MM/DD/YYYY)",
      "state_producer_license_number": "string",
      "national_producer_number": "string (Required in Florida)"
    }
  }
}
```

---

## Complete JSON Schema Example

```json
{
  "acord_125": {
    "form_version": "2016/03",
    "agency": { /* ... */ },
    "transaction_status": { /* ... */ },
    "carrier": { /* ... */ },
    "policy": { /* ... */ },
    "lines_of_business": [ /* ... */ ],
    "attachments": [ /* ... */ ],
    "underwriter": { /* ... */ },
    "first_named_insured": { /* ... */ },
    "other_named_insureds": [ /* ... */ ],
    "contacts": [ /* ... */ ],
    "nature_of_business": { /* ... */ },
    "premises": [ /* ... */ ],
    "additional_interests": [ /* ... */ ],
    "general_information": { /* ... */ },
    "prior_carriers": [ /* ... */ ],
    "loss_history": { /* ... */ },
    "remarks": "",
    "acknowledgements": { /* ... */ },
    "signatures": { /* ... */ }
  }
}
```

---

## Field Validation Rules

### Required Fields (Minimum for submission)
- Agency name and contact information
- First Named Insured name and address
- Business structure (entity type)
- FEIN or SSN
- At least one premises location
- Nature of business description
- Policy effective and expiration dates
- At least one line of business selected
- Applicant signature and date
- Producer signature and date

### Conditional Required Fields
- **If LLC**: Number of members
- **If Trust**: Name of trust
- **If Subsidiary**: Parent company information
- **If Has Subsidiaries**: Subsidiary details
- **If Foreign Operations**: Must attach ACORD 815/816
- **If Florida**: National Producer Number required
- **If Additional Interests**: Complete interest details per type

### Data Type Constraints
- **Dates**: MM/DD/YYYY format
- **Phone Numbers**: (A/C, No, Ext) format
- **ZIP Codes**: ZIP+4 format preferred
- **Decimals**: Currency values (2 decimal places)
- **Percentages**: 0-100 range
- **NAICS Codes**: 6-digit format
- **SIC Codes**: 4-digit format
- **FEIN**: XX-XXXXXXX format
- **SSN**: XXX-XX-XXXX format

---

## Data Extraction Mapping Notes

### Common Source Documents → ACORD 125 Fields

**From Business Application/Questionnaire:**
- Business name → first_named_insured.name
- Address → first_named_insured.mailing_address
- Entity type → first_named_insured.business_structure
- Tax ID → first_named_insured.fein_or_ssn
- Industry codes → naics_code, sic_code
- Years in business → nature_of_business.date_business_started

**From Loss Runs:**
- Claim data → loss_history.losses[]
- Total incurred → loss_history.total_losses_amount

**From Financial Statements:**
- Annual sales → premises[].annual_revenues
- Payroll data → (used in ACORD 130 for WC)

**From Prior Declarations Page:**
- Current carrier → prior_carriers[]
- Policy numbers → prior_carriers[].policy_number
- Expiration date → prior_carriers[].expiration_date
- Premium → prior_carriers[].premium

**From Property Information:**
- Building details → premises[]
- Square footage → premises[].occupied_area_sq_ft
- Ownership → premises[].interest

---

## AI Extraction Strategy

### Step 1: Document Classification
Identify which documents contain ACORD 125 data:
- Business applications
- Prior insurance declarations
- Loss run reports
- Financial statements
- Property schedules

### Step 2: Field Extraction Priority
**High Priority (Required for submission):**
1. Named insured information
2. Business address
3. FEIN/SSN
4. Premises information
5. Nature of business
6. Policy dates

**Medium Priority (Commonly needed):**
1. Contact information
2. Prior carrier details
3. Loss history
4. Additional insureds
5. Business structure details

**Low Priority (Often left blank initially):**
1. Subsidiary information
2. Detailed general information questions
3. Optional attachments

### Step 3: Confidence Scoring
- **Green (90%+ confidence)**: Auto-fill without review
- **Yellow (70-89% confidence)**: Pre-fill, flag for broker review
- **Red (<70% confidence)**: Leave blank or show suggestion with low confidence warning

### Step 4: Cross-Field Validation
- FEIN format matches business structure (Corporation needs FEIN, not SSN)
- State abbreviation matches ZIP code region
- Effective date is future-dated or within 30 days past
- Total building area ≥ occupied area
- Sum of line premiums ≈ total premium (if provided)

---

## Notes for Development Team

1. **Forms Library**: Store ACORD 125 template as fillable PDF with field name mappings
2. **Version Control**: Track ACORD form version (currently 2016/03)
3. **State Variations**: Some fields are state-specific (e.g., Florida requires National Producer Number)
4. **Dynamic Sections**: Premises and Additional Interests can repeat - UI must support add/remove
5. **Fraud Warnings**: State-specific fraud warning text must be displayed based on applicant state
6. **Signature Handling**: Support both digital signatures and uploaded signature images
7. **ACORD 101 Integration**: If remarks exceed space, auto-generate ACORD 101 continuation
8. **ACORD 823 Integration**: If more than 4 premises, auto-generate ACORD 823 additional premises schedule


Design Strategy

Perfect! I've created a comprehensive data structure document for the ACORD 125 form. Here's what I've included:

## Key Highlights:

### **1. Complete Field Structure (All 4 Pages):**
- **Page 1**: Agency info, carrier details, policy information, lines of business
- **Page 2**: Applicant information, named insureds, contacts, premises details
- **Page 3**: General information questions, prior carrier history
- **Page 4**: Loss history, signatures

### **2. JSON Schema Format:**
Every field is mapped with:
- Field name and data type
- Enums for dropdown/checkbox fields
- Format specifications (dates, phone numbers, etc.)
- Array structures for repeating sections

### **3. Validation Rules:**
- Required fields vs. optional fields
- Conditional requirements (e.g., "If LLC, then number of members")
- Data type constraints (date formats, FEIN format, etc.)

### **4. Extraction Mapping Guide:**
Shows which source documents map to which ACORD 125 fields:
- Business applications → Named insured info
- Loss runs → Loss history section
- Financial statements → Revenue data
- Prior declarations → Prior carrier info

### **5. AI Extraction Strategy:**
- Document classification approach
- Field extraction priority (high/medium/low)
- Confidence scoring system (Green/Yellow/Red)
- Cross-field validation logic

### **6. Developer Implementation Notes:**
- How to handle repeating sections (premises, additional interests)
- State-specific requirements
- Form version tracking
- Integration with continuation forms (ACORD 101, 823)

This structure gives your development team everything they need to:
1. Build the database schema
2. Design the UI forms
3. Map AI extraction results to form fields
4. Generate filled PDFs programmatically

