# Test Documents for Gap Detection Feature

This folder contains realistic client documents organized by client. Each client has multiple separate documents that would typically be uploaded together for a single insurance submission.

**📋 See Also:** [ACORD Forms Mapping](./ACORD-FORMS-MAPPING.md) - Which ACORD forms should be filled for each client scenario.

---

## Client 001: ABC Long Haul Trucking LLC

A trucking company requesting Commercial Auto and General Liability coverage.

### Documents Included:

1. **`client-001-application.md`**
   - Insurance quote request form
   - Business information
   - Coverage requests
   - Basic operations description
   - **Note:** Mentions documents will be attached (vehicle schedule, driver list, financial statement, loss runs)

2. **`client-001-financial-statement.md`**
   - Income statement summary
   - Balance sheet summary
   - Annual revenue: $2,400,000
   - Payroll information
   - **Gap:** Provides revenue but doesn't have DOT/MC numbers

3. **`client-001-loss-runs.md`**
   - 5-year loss history (2019-2023)
   - 3 claims totaling $50,000
   - Detailed claim descriptions
   - **Status:** ✅ Complete loss runs document

4. **`client-001-vehicle-schedule.md`**
   - 15 power units with full details (Year, Make, Model, VIN)
   - 20 trailers with full details
   - Vehicle values
   - **Status:** ✅ Complete vehicle schedule

5. **`client-001-driver-list.md`**
   - 12 drivers with full information
   - Dates of birth
   - License numbers and states
   - CDL information
   - Hire dates
   - **Status:** ✅ Complete driver list
   - **Note:** Mentions MVRs are on file but not included

### Expected Gaps After Upload:

**Missing Documents:**
- ❌ MVR Reports (mentioned in driver list but not uploaded)
- ❌ DOT Number document/verification
- ❌ MC Number document/verification

**Missing Data Fields:**
- ❌ DOT Number (mentioned in application but value not provided)
- ❌ MC Number (if applicable)
- ⚠️ Annual mileage (not in any document)
- ⚠️ Radius of operations details (mentioned but could be more specific)

**Present Data (Should NOT be flagged):**
- ✅ Business name, FEIN
- ✅ Vehicle VINs (all 15 vehicles)
- ✅ Driver information (all 12 drivers with DOB, license)
- ✅ Loss runs (5-year history)
- ✅ Annual revenue
- ✅ Business description

### Expected Completeness Score: 65-75%

The gap detection should identify:
1. Missing MVR documents (even though mentioned as "on file")
2. Missing DOT/MC numbers in the extracted data
3. Missing annual mileage data

---

## How to Test

1. **Upload all 5 documents** for Client 001
2. **Run AI extraction** on all documents
3. **Go to Review page** and click "Analyze Gaps"
4. **Verify:**
   - System detects "Commercial Auto" and "Motor Carrier" coverages
   - System recognizes uploaded documents (loss runs, vehicle schedule, driver list)
   - System flags missing DOT/MC numbers
   - System flags missing MVR reports
   - System does NOT flag vehicle VINs or driver info (they're in the documents)
   - Completeness score is around 65-75%

---

---

## Client 002: Bella Italia Restaurant LLC

A restaurant requesting General Liability, Property, and Liquor Liability coverage.

### Documents Included:

1. **`client-002-application.md`**
   - Insurance quote request form
   - Business information
   - Coverage requests (GL, Property, Liquor Liability)
   - Business operations description
   - Revenue breakdown
   - **Note:** Mentions documents will be attached

2. **`client-002-financial-statement.md`**
   - Income statement summary
   - Balance sheet summary
   - Annual revenue: $1,800,000
   - Liquor sales breakdown: $270,000 (15% of total)
   - Employee count and payroll

3. **`client-002-loss-runs.md`**
   - 5-year loss history (2019-2023)
   - 3 claims total: 2 GL claims ($20,500), 1 Property claim ($8,500)
   - No liquor liability claims
   - **Status:** ✅ Complete loss runs document

4. **`client-002-property-schedule.md`**
   - Detailed property schedule/statement of values
   - Building value: $850,000 (replacement cost)
   - Contents breakdown: $180,000 (kitchen equipment, furniture, inventory)
   - Building details (construction, square footage, year built)
   - **Status:** ✅ Complete property schedule

5. **`client-002-liquor-license.md`**
   - Texas Mixed Beverage Permit
   - License number: MB-2023-12345
   - Valid through December 31, 2024
   - **Status:** ✅ Liquor license document provided

### Expected Gaps After Upload:

**Missing Documents:**
- ⚠️ Current policy declarations pages (mentioned but not uploaded)

**Missing Data Fields:**
- ⚠️ Employee count (mentioned as 18 but may need verification)
- ⚠️ Some property details may need verification

**Present Data (Should NOT be flagged):**
- ✅ Business name, FEIN
- ✅ Property schedule with values
- ✅ Loss runs (5-year history)
- ✅ Liquor license
- ✅ Annual revenue and liquor sales percentage
- ✅ Business description

### Expected Completeness Score: 75-85%

The gap detection should identify:
1. Mostly complete submission
2. May flag missing current policy dec pages
3. Should recognize all major documents are present

---

## Client 003: Smith & Associates Construction Inc.

A construction company requesting Workers Compensation coverage.

### Documents Included:

1. **`client-003-application.md`**
   - Workers Compensation application
   - Business information
   - Operations description
   - Current experience mod: 1.05
   - States of operation: TX (primary), OK (occasional)
   - **Note:** Mentions documents will be attached

2. **`client-003-payroll-breakdown.md`**
   - Detailed payroll by classification code
   - 6 different class codes (Carpentry, Drywall, Painting, Electrical, Clerical, Executive)
   - Total annual payroll: $1,716,000
   - Payroll by state breakdown
   - Owner/officer payroll: $300,000 (included)
   - Subcontractor payment information
   - **Status:** ✅ Complete payroll breakdown

3. **`client-003-experience-mod.md`**
   - Experience modification worksheet
   - Current mod: 1.05
   - Experience period: 2020-2022
   - 2 claims during experience period
   - Mod calculation details
   - **Status:** ✅ Complete experience mod document

4. **`client-003-loss-runs.md`**
   - 5-year workers comp loss history (2019-2023)
   - 4 claims total: 1 with lost time (42 days), 3 medical only
   - Total incurred: $53,000
   - Detailed claim descriptions
   - **Status:** ✅ Complete loss runs document

5. **`client-003-osha-logs.md`**
   - OSHA 300 Log summaries for 2020-2023
   - 2023: 1 recordable case
   - Prior years included for comparison
   - Rate calculations (TRC, DART)
   - **Status:** ✅ OSHA logs provided

### Expected Gaps After Upload:

**Missing Documents:**
- ⚠️ Subcontractor certificates of insurance (mentioned as "maintained on file" but not uploaded)

**Missing Data Fields:**
- ⚠️ May need verification of some class codes
- ⚠️ Subcontractor certificate details

**Present Data (Should NOT be flagged):**
- ✅ Business name, FEIN
- ✅ Payroll breakdown by class code
- ✅ Experience modification worksheet
- ✅ Loss runs (5-year history)
- ✅ OSHA logs
- ✅ Employee count
- ✅ States of operation

### Expected Completeness Score: 80-90%

The gap detection should identify:
1. Very complete Workers Comp submission
2. Should recognize all major required documents are present
3. May flag missing subcontractor certificates if applicable

---

## Testing Summary

### Quick Test Scenarios:

**Scenario 1: Incomplete Submission (Client 001)**
- Upload Client 001 documents
- Expected: 65-75% completeness
- Should flag: Missing MVRs, DOT/MC numbers, annual mileage

**Scenario 2: Mostly Complete (Client 002)**
- Upload Client 002 documents
- Expected: 75-85% completeness
- Should flag: Missing policy dec pages

**Scenario 3: Very Complete (Client 003)**
- Upload Client 003 documents
- Expected: 80-90% completeness
- Should flag: Minimal gaps, maybe subcontractor certs

### Testing Tips:

1. **Test coverage detection** - System should correctly identify:
   - Client 001: Commercial Auto, Motor Carrier
   - Client 002: General Liability, Property, Liquor Liability
   - Client 003: Workers Compensation

2. **Test document recognition** - System should recognize uploaded document types

3. **Test conditional requirements** - 
   - Client 001 should trigger DOT/MC requirements for trucking
   - Client 002 should trigger liquor sales requirements

4. **Test completeness scoring** - Scores should reflect actual completeness

---

## Document Types by Client

| Client | Coverage Types | Documents |
|--------|---------------|-----------|
| **001** | Commercial Auto, Motor Carrier, GL | Application, Financial Statement, Loss Runs, Vehicle Schedule, Driver List |
| **002** | GL, Property, Liquor Liability | Application, Financial Statement, Loss Runs, Property Schedule, Liquor License |
| **003** | Workers Compensation | Application, Payroll Breakdown, Experience Mod, Loss Runs, OSHA Logs |

All documents are realistic examples that would be submitted together for a single insurance application.

