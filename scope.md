# 📋 Docwheech MVP - Technical Scope & Project Structure

## 1. Project Overview

**Project Name:** Docwheech MVP  
**Version:** v1.1  
**Objective:** Automate commercial insurance submissions by converting unstructured client data into completed ACORD forms in under 30 minutes.

## 2. Scope Definition

### 2.1 Core Scope (Must-Have Features)
- **Multi-file Upload System**: Drag-and-drop interface for PDFs, Excel, Word documents
- **Manual Extraction Trigger**: User-controlled "Extract Data" button after file upload completion
- **AI Data Extraction Engine**: Extract structured data using OpenAI GPT-4/5 + AWS Textract
- **ACORD Schema Converter**: Normalize extracted data into ACORD 125 JSON schema
- **Form Auto-Filler**: Automatically populate ACORD 125 PDF forms
- **Broker Review Interface**: Editable table for data validation and correction
- **PDF Export Engine**: Generate submission-ready packets with forms and attachments
- **Authentication System**: Secure user access via Firebase Auth

### 2.2 User Workflow Design
**Transition**: Manual trigger approach
- User uploads all required documents
- System displays uploaded files with delete option
- User clicks "Extract Data" button to initiate AI processing
- Clear progress indication during extraction
- Better user control and error handling compared to automatic triggers

**File Storage Strategy**: Immediate storage approach
- Files are immediately saved to AWS S3/Firebase Storage upon upload
- Ensures data safety and allows for resume capability
- User can navigate away and return without losing uploaded files

**Resume Capability**: Session recovery feature
- System tracks incomplete submissions in database
- When user logs back in, shows "Continue Previous Submission" option
- User can resume exactly where they left off
- Displays uploaded files and allows adding/removing before extraction
- Auto-cleanup of old incomplete submissions after 30 days

### 2.2 Extended Scope (Nice-to-Have Features)
- **Risk Narrative Generator**: AI-generated business risk summaries
- **Multi-form Support**: Beyond ACORD 125 to other ACORD forms
- **Advanced Validation**: Business rule validation for insurance data
- **Audit Trail**: Track changes and user actions
- **API Integration**: Connect with carrier submission systems

### 2.3 Out of Scope (Future Versions)
- Real-time carrier communication
- Policy management system
- Billing and payment processing
- Mobile applications
- Multi-tenant architecture for agencies

## 3. Technical Architecture

### 3.1 Frontend Stack
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **File Upload**: react-dropzone
- **PDF Handling**: PDF-lib for client-side operations

### 3.2 Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **File Storage**: AWS S3
- **Authentication**: Firebase Auth + JWT
- **PDF Processing**: ReportLab + PyPDF2

### 3.3 AI/ML Stack
- **Primary LLM**: OpenAI GPT-4 Turbo
- **Document Processing**: AWS Textract
- **Text Extraction**: PyPDF2 + python-docx
- **Data Validation**: Pydantic models

### 3.4 Infrastructure
- **Containerization**: Docker + Docker Compose
- **Cloud Provider**: AWS
- **CI/CD**: GitHub Actions
- **Monitoring**: AWS CloudWatch

## 4. Project Structure

```
docwheech-mvp/
├── docker-compose.yml              # Docker orchestration
├── Dockerfile                      # Backend container
├── Dockerfile.frontend             # Frontend container
├── requirements.txt                # Python dependencies
├── package.json                    # Node.js dependencies
├── .env.example                    # Environment variables template
├── README.md                       # Project documentation
│
├── backend/                        # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Configuration management
│   │   ├── database.py             # Database connection
│   │   │
│   │   ├── api/                    # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── upload.py           # File upload endpoints
│   │   │   ├── extraction.py       # AI extraction endpoints
│   │   │   ├── acord.py            # ACORD form endpoints
│   │   │   └── export.py           # PDF export endpoints
│   │   │
│   │   ├── core/                   # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── security.py         # Authentication & authorization
│   │   │   ├── acord_schema.py     # ACORD 125 schema definition
│   │   │   ├── pdf_generator.py    # PDF form filling logic
│   │   │   └── validation.py       # Data validation rules
│   │   │
│   │   ├── models/                 # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User model
│   │   │   ├── submission.py       # Submission model
│   │   │   └── document.py         # Document model
│   │   │
│   │   ├── services/               # Business services
│   │   │   ├── __init__.py
│   │   │   ├── ai_extraction.py    # OpenAI + Textract integration
│   │   │   ├── file_processor.py   # File parsing and processing
│   │   │   ├── acord_converter.py  # Data to ACORD conversion
│   │   │   └── pdf_service.py      # PDF generation service
│   │   │
│   │   ├── schemas/                # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py             # User request/response schemas
│   │   │   ├── submission.py       # Submission schemas
│   │   │   └── acord.py            # ACORD data schemas
│   │   │
│   │   └── utils/                  # Utility functions
│   │       ├── __init__.py
│   │       ├── file_helpers.py     # File handling utilities
│   │       ├── aws_client.py       # AWS service clients
│   │       └── openai_client.py    # OpenAI API client
│   │
│   ├── tests/                      # Backend tests
│   │   ├── __init__.py
│   │   ├── conftest.py             # Test configuration
│   │   ├── test_auth.py
│   │   ├── test_extraction.py
│   │   └── test_acord.py
│   │
│   └── migrations/                 # Database migrations
│       └── alembic/
│
├── frontend/                       # Next.js Frontend
│   ├── public/                     # Static assets
│   │   ├── icons/
│   │   └── acord-templates/        # ACORD 125 template PDFs
│   │
│   ├── src/
│   │   ├── app/                    # Next.js 13+ App Router
│   │   │   ├── layout.tsx          # Root layout
│   │   │   ├── page.tsx            # Home page
│   │   │   ├── login/              # Authentication pages
│   │   │   ├── upload/             # File upload page
│   │   │   ├── review/             # Data review page
│   │   │   ├── export/             # PDF export page
│   │   │   └── api/                # API routes (if needed)
│   │   │
│   │   ├── components/             # Reusable UI components
│   │   │   ├── ui/                 # shadcn/ui components
│   │   │   │   ├── button.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   └── ...
│   │   │   ├── forms/              # Form components
│   │   │   │   ├── file-upload.tsx
│   │   │   │   ├── acord-review.tsx
│   │   │   │   └── validation-form.tsx
│   │   │   └── layout/             # Layout components
│   │   │       ├── header.tsx
│   │   │       ├── sidebar.tsx
│   │   │       └── footer.tsx
│   │   │
│   │   ├── hooks/                  # Custom React hooks
│   │   │   ├── use-auth.ts
│   │   │   ├── use-file-upload.ts
│   │   │   └── use-acord-data.ts
│   │   │
│   │   ├── lib/                    # Utility libraries
│   │   │   ├── api.ts              # API client
│   │   │   ├── auth.ts             # Authentication helpers
│   │   │   ├── utils.ts            # General utilities
│   │   │   └── constants.ts        # Application constants
│   │   │
│   │   ├── store/                  # State management
│   │   │   ├── auth-store.ts       # Authentication state
│   │   │   ├── submission-store.ts # Submission state
│   │   │   └── ui-store.ts         # UI state
│   │   │
│   │   └── types/                  # TypeScript type definitions
│   │       ├── auth.ts
│   │       ├── submission.ts
│   │       └── acord.ts
│   │
│   ├── styles/                     # Global styles
│   │   └── globals.css
│   │
│   └── tests/                      # Frontend tests
│       ├── __tests__/
│       └── setup.ts
│
├── docs/                          # Documentation
│   ├── api/                       # API documentation
│   ├── deployment/                # Deployment guides
│   └── user-guide/                # User documentation
│
└── scripts/                       # Utility scripts
    ├── setup.sh                   # Development setup
    ├── deploy.sh                  # Deployment script
    └── test.sh                    # Test runner
```

## 5. Framework Justifications

### 5.1 Frontend: Next.js 14 over Alternatives

**Chosen**: Next.js 14 with React 18  
**Alternatives Considered**: Vite + React, Create React App, Angular, Vue.js

**Justification**:
- **Full-Stack Capabilities**: Next.js provides both frontend and API routes, reducing complexity for MVP
- **Performance**: Built-in optimizations (SSR, SSG, Image optimization) improve user experience
- **Developer Experience**: Excellent TypeScript support and hot reloading for rapid development
- **SEO & Accessibility**: Server-side rendering benefits for documentation and marketing pages
- **Production Ready**: Mature framework with extensive documentation and community support
- **Deployment**: Seamless deployment to Vercel or any Node.js hosting platform

**Why not Vite + React**: While Vite offers faster development builds, Next.js provides more out-of-the-box features crucial for an MVP (routing, API routes, optimization).

**Why not Angular/Vue**: React ecosystem has better AI/ML integration libraries and more developers familiar with it for faster development.

### 5.2 Backend: FastAPI over Alternatives

**Chosen**: FastAPI (Python)  
**Alternatives Considered**: Django, Flask, Express.js (Node.js), Spring Boot (Java)

**Justification**:
- **AI/ML Integration**: Python's superior ecosystem for OpenAI, AWS Textract, and PDF processing libraries
- **Performance**: FastAPI is one of the fastest Python frameworks, crucial for file processing
- **Automatic Documentation**: Built-in OpenAPI/Swagger documentation generation
- **Type Safety**: Native support for Pydantic models with automatic validation
- **Async Support**: Excellent async/await support for handling multiple file uploads simultaneously
- **Developer Productivity**: Minimal boilerplate code allows focus on business logic
- **PDF Processing**: Superior libraries (ReportLab, PyPDF2) for ACORD form manipulation

**Why not Django**: Django is more heavyweight for an API-focused application. FastAPI's simplicity aligns better with MVP timeline.

**Why not Express.js**: While Node.js is fast, Python's AI/ML ecosystem is significantly stronger for document processing and OpenAI integration.

### 5.3 Database: PostgreSQL over Alternatives

**Chosen**: PostgreSQL  
**Alternatives Considered**: MongoDB, Firebase Firestore, MySQL

**Justification**:
- **ACID Compliance**: Critical for financial/insurance data integrity
- **JSON Support**: Native JSON columns for flexible ACORD schema storage
- **Performance**: Excellent performance for complex queries and large datasets
- **Maturity**: Battle-tested in production environments
- **SQLAlchemy Integration**: Excellent ORM support with FastAPI
- **Scalability**: Can handle growth from MVP to enterprise scale

**Why not MongoDB**: While MongoDB offers flexibility, the structured nature of insurance data benefits from relational constraints and ACID properties.

**Why not Firebase Firestore**: Serverless is appealing but vendor lock-in and cost scaling concerns for data-intensive operations.

### 5.4 File Storage: AWS S3 over Alternatives

**Chosen**: AWS S3  
**Alternatives Considered**: Firebase Storage, Google Cloud Storage, Azure Blob

**Justification**:
- **Integration**: Seamless integration with AWS Textract for document processing
- **Cost Efficiency**: Pay-per-use pricing model suitable for MVP
- **Security**: Enterprise-grade security with fine-grained access controls
- **Scalability**: Virtually unlimited storage capacity
- **CDN Integration**: Easy integration with CloudFront for global content delivery
- **Versioning**: Built-in file versioning for audit trails

### 5.5 Authentication: Firebase Auth over Alternatives

**Chosen**: Firebase Auth  
**Alternatives Considered**: Auth0, AWS Cognito, Custom JWT implementation

**Justification**:
- **Rapid Development**: Pre-built authentication flows accelerate MVP development
- **Security**: Google's security infrastructure and best practices
- **Multiple Providers**: Support for email/password, Google, Microsoft, etc.
- **Cost**: Generous free tier suitable for MVP
- **Integration**: Easy integration with both frontend and backend
- **User Management**: Built-in user management dashboard

**Why not Auth0**: While Auth0 offers more features, Firebase Auth provides sufficient functionality for MVP at lower cost.

**Why not AWS Cognito**: More complex setup and configuration compared to Firebase Auth's simplicity.

### 5.6 AI Services: OpenAI + AWS Textract over Alternatives

**Chosen**: OpenAI GPT-4 Turbo + AWS Textract  
**Alternatives Considered**: Azure Cognitive Services, Google Cloud AI, Anthropic Claude

**Justification**:
- **Best-in-Class LLM**: GPT-4 Turbo provides superior reasoning for complex document extraction
- **Document Processing**: AWS Textract excels at structured data extraction from PDFs and forms
- **Integration**: Both services integrate well with Python/FastAPI backend
- **Reliability**: Proven track record in production environments
- **Cost-Effectiveness**: Pay-per-use pricing suitable for MVP scale
- **API Quality**: Well-documented APIs with excellent error handling

**Why not Azure/Google AI**: While competitive, OpenAI currently leads in general reasoning capabilities crucial for understanding unstructured insurance documents.

## 6. Development Phases

### Phase 1: Foundation (Weeks 1-2)
- [x] Project setup and Docker configuration ✅
- [x] Basic authentication system ✅
- [x] User workflow design and requirements ✅
- [x] File upload infrastructure ✅
- [x] Database schema design ✅

### Phase 2: Core Features (Weeks 3-5)
- AI extraction engine integration
- ACORD schema implementation
- Review interface development
- PDF form filling functionality

### Phase 3: Integration & Testing (Weeks 6-7)
- End-to-end workflow integration
- Comprehensive testing
- Performance optimization
- Security hardening

### Phase 4: Deployment & Launch (Week 8)
- Production deployment
- User acceptance testing
- Documentation completion
- MVP launch

## 7. Success Metrics

### Technical Metrics
- File upload processing time < 30 seconds
- AI extraction accuracy > 90%
- System uptime > 99.5%
- API response time < 2 seconds

### Business Metrics
- Time reduction: 15 hours → 30 minutes (97% improvement)
- User adoption rate
- Error reduction in submissions
- User satisfaction scores

## 8. Risk Mitigation

### Technical Risks
- **AI Accuracy**: Implement confidence scoring and human review workflows
- **File Processing**: Use robust error handling and retry mechanisms
- **PDF Compatibility**: Test with various ACORD form versions and formats
- **Scalability**: Design for horizontal scaling from day one

### Business Risks
- **ACORD Compliance**: Regular validation against official ACORD specifications
- **Data Security**: Implement comprehensive security measures for sensitive insurance data
- **User Adoption**: Provide extensive training materials and support

---

*This scope document serves as the technical foundation for Docwheech MVP development and should be reviewed and updated as requirements evolve.*
