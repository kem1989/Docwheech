# 🚀 Docwheech MVP

Automated ACORD form processing for commercial insurance submissions.

## Overview

Docwheech transforms unstructured client data into completed ACORD forms in under 30 minutes, reducing a 15-hour manual process by 97%.

## Features

- **Multi-file Upload**: Drag-and-drop interface for PDFs, Excel, Word documents
- **AI Data Extraction**: Intelligent extraction using OpenAI GPT-4 + AWS Textract
- **ACORD Schema Conversion**: Automatic normalization to ACORD 125 standard
- **Form Auto-Fill**: Dynamic population of ACORD 125 PDF forms
- **Review Interface**: Editable validation and correction system
- **PDF Export**: Submission-ready packet generation

## Tech Stack

### Backend
- **FastAPI** (Python 3.11+)
- **PostgreSQL** with SQLAlchemy ORM
- **Redis** for caching
- **AWS S3** for file storage
- **Firebase Auth** for authentication

### Frontend
- **Next.js 14** with React 18
- **Tailwind CSS** + shadcn/ui components
- **Zustand** for state management
- **TypeScript** for type safety

### AI/ML
- **OpenAI GPT-4 Turbo** for data extraction
- **AWS Textract** for document processing
- **ReportLab** for PDF generation

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Setup

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd MyInsurance
   ./scripts/setup.sh
   ```

2. **Configure environment**:
   ```bash
   cp env.example .env
   # Update .env with your API keys and configuration
   ```

3. **Start services**:
   ```bash
   docker-compose up
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Development

#### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
docwheech-mvp/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core business logic
│   │   ├── models/         # Database models
│   │   ├── services/       # Business services
│   │   └── schemas/        # Pydantic schemas
│   └── tests/              # Backend tests
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom hooks
│   │   └── lib/           # Utilities
│   └── tests/             # Frontend tests
├── docs/                  # Documentation
├── scripts/               # Utility scripts
└── docker-compose.yml     # Docker orchestration
```

## Development Phases

### Phase 1: Foundation (Weeks 1-2)
- [x] Project setup and Docker configuration
- [ ] Basic authentication system
- [ ] File upload infrastructure
- [ ] Database schema design

### Phase 2: Core Features (Weeks 3-5)
- [ ] AI extraction engine integration
- [ ] ACORD schema implementation
- [ ] Review interface development
- [ ] PDF form filling functionality

### Phase 3: Integration & Testing (Weeks 6-7)
- [ ] End-to-end workflow integration
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Security hardening

### Phase 4: Deployment & Launch (Week 8)
- [ ] Production deployment
- [ ] User acceptance testing
- [ ] Documentation completion
- [ ] MVP launch

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license here]

## Support

For support and questions, please [create an issue](link-to-issues).
