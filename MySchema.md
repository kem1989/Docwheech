# MyInsurance Database Schema Documentation

## Overview

This document describes the complete database schema for the MyInsurance ACORD 125 Commercial Insurance Application processing system. The schema supports AI-powered data extraction from insurance documents and stores structured data in both JSON and normalized relational formats.

---

## 📊 Database Architecture

### Storage Strategy
The system uses a **dual storage approach**:
1. **JSON Storage** - Raw and processed data in `submissions` table
   - `extracted_data` (JSON) - Raw AI-extracted data with confidence scores
   - `acord_data` (JSON) - Cleaned ACORD-compliant structured data
2. **Normalized Tables** - Relational ACORD 125 data for querying and reporting

### Database Engine
- **PostgreSQL 15** (Alpine)
- **UUID** primary keys for all tables
- **Cascade delete** relationships
- **Timezone-aware** timestamps

---

## 🗄️ Core Tables

### 1. Users (`users`)
User authentication and account management.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `email` | VARCHAR(255) | NO | User email (unique) |
| `firebase_uid` | VARCHAR(255) | NO | Firebase authentication ID |
| `name` | VARCHAR(255) | YES | User display name |
| `created_at` | TIMESTAMP | NO | Account creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

### 2. Submissions (`submissions`)
Main container for insurance application submissions.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | NO | - | Primary key |
| `user_id` | UUID | NO | - | Foreign key to `users.id` |
| `title` | VARCHAR(255) | YES | - | Submission title |
| `status` | VARCHAR(50) | NO | 'draft' | Status: draft, processing, completed, failed |
| `submission_type` | VARCHAR(50) | NO | 'acord_125' | Type of submission |
| `acord_data` | JSON | YES | - | **Cleaned ACORD-compliant data** |
| `extracted_data` | JSON | YES | - | **Raw AI extraction with confidence scores** |
| `extraction_status` | VARCHAR(50) | NO | 'pending' | Extraction status: pending, processing, completed, failed |
| `extraction_progress` | INTEGER | NO | 0 | Progress percentage (0-100) |
| `extraction_error` | TEXT | YES | - | Error message if extraction fails |
| `total_files` | INTEGER | NO | 0 | Total number of uploaded files |
| `processed_files` | INTEGER | NO | 0 | Number of processed files |
| `created_at` | TIMESTAMP | NO | now() | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | now() | Last update timestamp |
| `completed_at` | TIMESTAMP | YES | - | Completion timestamp |

**Relationships:**
- One-to-Many: `documents`, `agencies`, `contacts`, `premises`, etc.
- Belongs-to: `users`

---

### 3. Documents (`documents`)
Uploaded insurance documents.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `original_filename` | VARCHAR(255) | NO | Original file name |
| `file_type` | VARCHAR(50) | NO | File extension (pdf, jpg, etc.) |
| `file_size` | INTEGER | NO | File size in bytes |
| `mime_type` | VARCHAR(100) | NO | MIME type |
| `s3_bucket` | VARCHAR(255) | NO | S3 bucket name |
| `s3_key` | VARCHAR(500) | NO | S3 object key |
| `s3_url` | VARCHAR(1000) | YES | Presigned download URL |
| `processing_status` | VARCHAR(50) | NO | Status: uploaded, processing, completed |
| `is_valid` | BOOLEAN | NO | File validation flag |
| `created_at` | TIMESTAMP | NO | Upload timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

## 🏢 ACORD 125 Data Tables

### 4. Agencies (`agencies`)
Insurance agency information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `name` | VARCHAR(255) | NO | Agency name |
| `code` | VARCHAR(50) | YES | Agency code |
| `subcode` | VARCHAR(50) | YES | Agency subcode |
| `agency_customer_id` | VARCHAR(100) | YES | Customer ID |
| `address` | TEXT | YES | Agency address |
| `contact_name` | VARCHAR(255) | YES | Contact person name |
| `phone` | VARCHAR(50) | YES | Phone number |
| `fax` | VARCHAR(50) | YES | Fax number |
| `email` | VARCHAR(255) | YES | Email address |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

### 5. Transaction Statuses (`transaction_statuses`)
Transaction type and binding information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `type` | ENUM | NO | Transaction type (see ENUMs below) |
| `bound_date` | DATE | YES | Binding date |
| `bound_time` | VARCHAR(20) | YES | Binding time (HH:MM AM/PM) |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

**ENUM Values:** `QUOTE`, `RENEWAL`, `ISSUE_POLICY`, `BOUND`, `CANCEL`, `CHANGE`

---

### 6. Policies (`policies`)
Policy details and premium information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `proposed_effective_date` | DATE | YES | Proposed policy start date |
| `proposed_expiration_date` | DATE | YES | Proposed policy end date |
| `billing_plan` | VARCHAR(100) | YES | Billing plan description |
| `payment_plan` | VARCHAR(100) | YES | Payment plan description |
| `audit` | BOOLEAN | NO | Audit flag (default: false) |
| `deposit_premium` | DECIMAL(15,2) | YES | Deposit premium amount |
| `minimum_premium` | DECIMAL(15,2) | YES | Minimum premium amount |
| `method_of_payment` | VARCHAR(50) | YES | Payment method: DIRECT, AGENCY |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

### 7. Lines of Business (`lines_of_business`)
Coverage types for the policy (multiple per submission).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `line` | ENUM | NO | Line of business type (see ENUMs below) |
| `selected` | BOOLEAN | NO | Whether this line is selected |
| `premium` | DECIMAL(10,2) | YES | Premium amount for this line |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

**ENUM Values:** 
- `COMMERCIAL_GENERAL_LIABILITY`
- `COMMERCIAL_PROPERTY`
- `BUSINESS_AUTO`
- `WORKERS_COMPENSATION`
- `UMBRELLA`
- `BUSINESS_OWNERS`
- `GARAGE_AND_DEALERS`
- `CRIME`
- `BOILER_AND_MACHINERY`
- `COMMERCIAL_INLAND_MARINE`
- `CYBER_AND_PRIVACY`
- `FIDUCIARY_LIABILITY`
- `LIQUOR_LIABILITY`
- `MOTOR_CARRIER`
- `TRUCKERS`
- `YACHT`

---

### 8. First Named Insureds (`first_named_insureds`)
Primary insured business information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `name` | VARCHAR(255) | NO | Legal business name |
| `mailing_address` | TEXT | YES | Mailing address |
| `business_structure` | ENUM | YES | Business structure type (see ENUMs below) |
| `number_of_members` | INTEGER | YES | Number of LLC members |
| `number_of_managers` | INTEGER | YES | Number of LLC managers |
| `naics_code` | VARCHAR(10) | YES | 6-digit NAICS code |
| `sic_code` | VARCHAR(10) | YES | SIC code |
| `gl_code` | VARCHAR(10) | YES | General Liability code |
| `fein_or_ssn` | VARCHAR(20) | YES | Federal EIN or SSN |
| `business_phone` | VARCHAR(50) | YES | Business phone number |
| `website_address` | VARCHAR(255) | YES | Website URL |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

**ENUM Values:** 
- `INDIVIDUAL`
- `PARTNERSHIP`
- `CORPORATION`
- `LLC`
- `JOINT_VENTURE`
- `NOT_FOR_PROFIT_ORG`
- `SUBCHAPTER_S_CORPORATION`
- `TRUST`

---

### 9. Contacts (`contacts`)
Contact information (multiple per submission).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `contact_type` | VARCHAR(100) | YES | Type of contact |
| `contact_name` | VARCHAR(255) | YES | Contact person name |
| `primary_email` | VARCHAR(255) | YES | Primary email address |
| `secondary_email` | VARCHAR(255) | YES | Secondary email address |
| `primary_phone` | VARCHAR(50) | YES | Primary phone number |
| `primary_phone_type` | VARCHAR(20) | YES | HOME, BUSINESS, CELL |
| `secondary_phone` | VARCHAR(50) | YES | Secondary phone number |
| `secondary_phone_type` | VARCHAR(20) | YES | HOME, BUSINESS, CELL |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

### 10. Nature of Business (`nature_of_business`)
Business operations and type information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `date_business_started` | DATE | YES | Business start date |
| `business_type` | TEXT | YES | JSON array of business types |
| `description_of_primary_operations` | TEXT | YES | Operations description |
| `retail_stores_or_service_operations` | BOOLEAN | NO | Has retail operations |
| `retail_percent_of_total_sales` | DECIMAL(5,2) | YES | Retail percentage |
| `installation_service_repair_work` | BOOLEAN | NO | Does installation/repair |
| `off_premises_installation_service_repair` | BOOLEAN | NO | Off-premises work flag |
| `description_of_operations_other_named_insureds` | TEXT | YES | Other insureds description |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

### 11. Premises (`premises`)
Location and property information (multiple per submission).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `location_number` | INTEGER | YES | Location number |
| `building_number` | INTEGER | YES | Building number |
| `street_address` | VARCHAR(255) | YES | Street address |
| `city` | VARCHAR(100) | YES | City |
| `county` | VARCHAR(100) | YES | County |
| `state` | VARCHAR(2) | YES | State abbreviation |
| `zip` | VARCHAR(10) | YES | ZIP code |
| `city_limits` | BOOLEAN | NO | Within city limits flag |
| `description_of_operations` | TEXT | YES | Operations at location |
| `interest` | ENUM | YES | OWNER or TENANT |
| `owner_or_tenant_inside` | BOOLEAN | NO | Inside interest flag |
| `owner_or_tenant_outside` | BOOLEAN | NO | Outside interest flag |
| `number_full_time_employees` | INTEGER | YES | Full-time employee count |
| `number_part_time_employees` | INTEGER | YES | Part-time employee count |
| `annual_revenues` | DECIMAL(15,2) | YES | Annual revenues at location |
| `occupied_area_sq_ft` | DECIMAL(10,2) | YES | Occupied square footage |
| `total_building_area_sq_ft` | DECIMAL(10,2) | YES | Total building square footage |
| `open_to_public_area_sq_ft` | DECIMAL(10,2) | YES | Public area square footage |
| `any_area_leased_to_others` | BOOLEAN | NO | Area leased to others flag |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

**ENUM Values:** `OWNER`, `TENANT`

---

### 12. Prior Carriers (`prior_carriers`)
Previous insurance carrier information (multiple per submission).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `category` | ENUM | YES | Coverage category (see ENUMs below) |
| `carrier_name` | VARCHAR(255) | YES | Insurance carrier name |
| `policy_number` | VARCHAR(100) | YES | Policy number |
| `effective_date` | DATE | YES | Policy effective date |
| `expiration_date` | DATE | YES | Policy expiration date |
| `premium` | DECIMAL(10,2) | YES | Premium amount |
| `years_with_carrier` | INTEGER | YES | Years with this carrier |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

**ENUM Values:** `GENERAL_LIABILITY`, `AUTOMOBILE`, `PROPERTY`, `OTHER`

---

### 13. Loss Histories (`loss_histories`)
Loss summary information.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `has_losses` | BOOLEAN | NO | Has any losses flag |
| `total_losses_amount` | DECIMAL(15,2) | YES | Total amount of all losses |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

### 14. Losses (`losses`)
Individual loss records (multiple per loss history).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `loss_history_id` | UUID | NO | Foreign key to `loss_histories.id` |
| `date_of_loss` | DATE | YES | Date loss occurred |
| `line_type` | VARCHAR(50) | YES | Type of coverage line |
| `description_of_occurrence` | TEXT | YES | Loss description |
| `amount_paid` | DECIMAL(10,2) | YES | Amount paid on claim |
| `amount_reserved` | DECIMAL(10,2) | YES | Amount reserved |
| `claim_open` | BOOLEAN | NO | Claim still open flag |
| `subrogation` | BOOLEAN | NO | Subrogation flag |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

### 15. Signatures (`signatures`)
Digital signature records (multiple per submission).

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | UUID | NO | Primary key |
| `submission_id` | UUID | NO | Foreign key to `submissions.id` |
| `signature_type` | VARCHAR(50) | NO | Type: applicant, producer |
| `signature_data` | TEXT | YES | Digital signature or image data |
| `signer_name` | VARCHAR(255) | YES | Name of signer |
| `signature_date` | DATE | YES | Date signed |
| `state_producer_license_number` | VARCHAR(100) | YES | State license number (producer) |
| `national_producer_number` | VARCHAR(100) | YES | NPN (producer) |
| `created_at` | TIMESTAMP | NO | Creation timestamp |
| `updated_at` | TIMESTAMP | NO | Last update timestamp |

---

## 🔗 Foreign Key Relationships

### Primary Relationships
```
users (1) ──────< submissions (many)
                      │
                      ├──────< documents
                      ├──────< agencies
                      ├──────< transaction_statuses
                      ├──────< policies
                      ├──────< lines_of_business
                      ├──────< first_named_insureds
                      ├──────< contacts
                      ├──────< nature_of_business
                      ├──────< premises
                      ├──────< prior_carriers
                      ├──────< loss_histories
                      │           │
                      │           └──────< losses
                      └──────< signatures
```

### Cascade Delete Behavior
When a `submission` is deleted, all related records are automatically deleted:
- All documents (and their S3 files)
- All ACORD data records (agencies, policies, contacts, etc.)
- All loss histories and individual losses
- All signatures

---

## 🎯 ENUM Types Summary

### 1. Business Structure (8 values)
- `INDIVIDUAL`
- `PARTNERSHIP`
- `CORPORATION`
- `LLC`
- `JOINT_VENTURE`
- `NOT_FOR_PROFIT_ORG`
- `SUBCHAPTER_S_CORPORATION`
- `TRUST`

### 2. Transaction Type (6 values)
- `QUOTE`
- `RENEWAL`
- `ISSUE_POLICY`
- `BOUND`
- `CANCEL`
- `CHANGE`

### 3. Line of Business (15 values)
- `COMMERCIAL_GENERAL_LIABILITY`
- `COMMERCIAL_PROPERTY`
- `BUSINESS_AUTO`
- `WORKERS_COMPENSATION`  #Issue here. We need to remove this in database and in openai logic. In the accord_schema.py, that premium field should be removed.
- `UMBRELLA`
- `BUSINESS_OWNERS`
- `GARAGE_AND_DEALERS`
- `CRIME`
- `BOILER_AND_MACHINERY`
- `COMMERCIAL_INLAND_MARINE`
- `CYBER_AND_PRIVACY`
- `FIDUCIARY_LIABILITY`
- `LIQUOR_LIABILITY`
- `MOTOR_CARRIER`
- `TRUCKERS`
- `YACHT`

### 4. Property Interest (2 values)
- `OWNER`
- `TENANT`

### 5. Carrier Category (4 values)
- `GENERAL_LIABILITY`
- `AUTOMOBILE`
- `PROPERTY`
- `OTHER`

---

## 📊 Indexes

### Automatic Indexes
- Primary keys (UUID) on all tables
- Foreign keys for all relationships

### Recommended Additional Indexes (for optimization)
```sql
-- Submissions by status
CREATE INDEX idx_submissions_status ON submissions(status);
CREATE INDEX idx_submissions_extraction_status ON submissions(extraction_status);

-- User submissions lookup
CREATE INDEX idx_submissions_user_id ON submissions(user_id);

-- Document lookups
CREATE INDEX idx_documents_submission_id ON documents(submission_id);
CREATE INDEX idx_documents_s3_key ON documents(s3_key);

-- ACORD data lookups
CREATE INDEX idx_agencies_submission_id ON agencies(submission_id);
CREATE INDEX idx_first_named_insureds_submission_id ON first_named_insureds(submission_id);
CREATE INDEX idx_premises_submission_id ON premises(submission_id);
```

---

## 🔄 Data Flow

### 1. Upload Phase
```
User uploads documents
    ↓
Create submission record (status: 'draft')
    ↓
Upload files to S3
    ↓
Create document records
    ↓
Update submission.total_files
```

### 2. Extraction Phase
```
Click "Start AI Extraction"
    ↓
Update submission.extraction_status = 'processing'
    ↓
Run AWS Textract on documents
    ↓
Run OpenAI GPT-4 extraction
    ↓
Store raw results in submission.extracted_data (JSON)
    ↓
Update progress: 10% → 20% → 40% → 60% → 80% → 100%
    ↓
Generate risk narrative
    ↓
Transform to ACORD schema
    ↓
Store cleaned data in submission.acord_data (JSON)
    ↓
Update submission.extraction_status = 'completed'
```

### 3. Normalization Phase (Future Enhancement)
```
Transform submission.acord_data
    ↓
Insert into ACORD tables:
    - agencies
    - policies
    - first_named_insureds
    - contacts
    - premises
    - prior_carriers
    - loss_histories & losses
    - etc.
```

### 4. Export Phase
```
Retrieve submission data
    ↓
Merge acord_data with ACORD table data
    ↓
Generate PDF ACORD 125 form
    ↓
Return to user
```

---

## 🛠️ Migration Management

### Alembic Configuration
Migrations are managed using Alembic and stored in:
- `backend/migrations/alembic/versions/`

### Current Migration
- `38136bc82556_initial_migration_with_enhanced_acord_.py`

### Running Migrations
```bash
# Generate new migration
docker exec -it docwheech_backend alembic revision --autogenerate -m "description"

# Apply migrations
docker exec -it docwheech_backend alembic upgrade head

# Rollback migration
docker exec -it docwheech_backend alembic downgrade -1
```

---

## 🔍 Common Queries

### Get Submission with All Data
```sql
SELECT 
    s.*,
    json_agg(DISTINCT d.*) as documents,
    json_agg(DISTINCT a.*) as agencies,
    json_agg(DISTINCT p.*) as premises
FROM submissions s
LEFT JOIN documents d ON d.submission_id = s.id
LEFT JOIN agencies a ON a.submission_id = s.id
LEFT JOIN premises p ON p.submission_id = s.id
WHERE s.id = 'submission-uuid'
GROUP BY s.id;
```

### Get User's Recent Submissions
```sql
SELECT 
    id,
    title,
    status,
    extraction_status,
    extraction_progress,
    total_files,
    created_at
FROM submissions
WHERE user_id = 'user-uuid'
ORDER BY created_at DESC
LIMIT 10;
```

### Get Incomplete Submissions
```sql
SELECT *
FROM submissions
WHERE user_id = 'user-uuid'
  AND status IN ('draft', 'processing')
ORDER BY updated_at DESC;
```

### Get Extraction Statistics
```sql
SELECT 
    extraction_status,
    COUNT(*) as count,
    AVG(extraction_progress) as avg_progress
FROM submissions
WHERE user_id = 'user-uuid'
GROUP BY extraction_status;
```

---

## 📝 Notes

### JSON Data Structure

#### extracted_data Format
```json
{
  "agency": {
    "name": {"value": "ABC Insurance", "confidence": 0.95},
    "phone": {"value": "(555) 123-4567", "confidence": 0.88}
  },
  "first_named_insured": {
    "name": {"value": "Tech Corp LLC", "confidence": 0.92},
    "naics_code": {"value": "541511", "confidence": 0.85}
  }
}
```

#### acord_data Format
```json
{
  "agency": {
    "name": "ABC Insurance",
    "phone": "(555) 123-4567"
  },
  "first_named_insured": {
    "name": "Tech Corp LLC",
    "naics_code": "541511"
  }
}
```

### Performance Considerations
- JSON fields (`acord_data`, `extracted_data`) support GIN indexing for fast queries
- Consider partitioning `submissions` table by `created_at` for large datasets
- Archive completed submissions older than 1 year to separate table

### Security
- All personally identifiable information (PII) should be encrypted at rest
- S3 files use presigned URLs with 1-hour expiration
- Database access restricted by user_id foreign key constraints

---

## 🔧 Maintenance

### Database Cleanup
```sql
-- Delete old failed extractions (older than 30 days)
DELETE FROM submissions 
WHERE extraction_status = 'failed' 
  AND created_at < NOW() - INTERVAL '30 days';

-- Clean up orphaned documents (if any)
DELETE FROM documents 
WHERE submission_id NOT IN (SELECT id FROM submissions);
```

### Backup Strategy
- Daily automated PostgreSQL backups
- S3 bucket versioning enabled
- Point-in-time recovery available

---

## 📚 Related Documentation
- [ACORD_Data_Structure.md](./ACORD_Data_Structure.md) - ACORD 125 field mappings
- [PROGRESS_FIX_COMPLETE.md](./PROGRESS_FIX_COMPLETE.md) - Progress tracking implementation
- [README.md](./README.md) - Application overview

---

**Last Updated:** October 29, 2025  
**Database Version:** PostgreSQL 15  
**Schema Version:** 1.0.0 (Migration: 38136bc82556)

