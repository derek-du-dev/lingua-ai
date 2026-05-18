# Lingua AI - Intelligent English Learning System

## Overview

Lingua AI is an AI-powered English learning platform designed to help non-native English speakers improve their language skills through personalized, interactive, and intelligent learning experiences. The system leverages artificial intelligence to provide adaptive content, real-time feedback, and comprehensive learning resources.

## Key Features

- **AI-Powered Article Processing**: Automatically process and analyze English articles for learning
- **Intelligent Question Generation**: Generate comprehension questions based on article content
- **Audio Learning**: Support for audio-based learning materials with synchronized content
- **Personalized Learning Paths**: Adaptive learning experiences tailored to individual student progress
- **Intensive Listening Exercises**: Dedicated exercises for improving listening comprehension
- **Textbook Management**: Organize and manage learning materials in a structured way
- **User Management**: Admin interface for managing students and instructors
- **System Configuration**: Flexible system settings for customization

## System Architecture

### Technology Stack

**Backend:**

- Python with FastAPI framework
- PostgreSQL database
- JWT-based authentication
- RESTful API architecture

**Frontend:**

- Vue 3 with TypeScript
- Vite build tool
- Modern responsive UI
- OpenAPI-based API client generation

**Infrastructure:**

- Docker containerization
- Docker Compose for orchestration
- Caddy reverse proxy
- Scalable microservices architecture

## Project Structure

```
lingua-ai/
├── apps/
│   ├── api/                 # Backend API server
│   │   ├── main.py         # Application entry point
│   │   ├── models.py       # Database models
│   │   ├── auth.py         # Authentication logic
│   │   ├── database.py     # Database configuration
│   │   ├── routers/        # API endpoints
│   │   └── schemas.py      # Request/response schemas
│   └── web/                 # Frontend application
│       ├── src/            # Vue 3 application source
│       ├── api/            # Generated OpenAPI client
│       └── package.json    # Dependencies
├── docker-compose.yml      # Service orchestration
└── Caddyfile.example       # Reverse proxy configuration
```

## Core Modules

### API Endpoints

**Articles Management**

- Create, read, update, and delete articles
- Process articles with AI for learning material generation
- Store article-related media (audio, videos)

**Learning Activities**

- Track student learning progress
- Provide personalized recommendations
- Generate adaptive learning content

**Textbooks**

- Organize learning materials
- Structure content by difficulty levels
- Manage curriculum

**User Management**

- Student account management
- Instructor/admin interface
- Role-based access control

**System Settings**

- Configure system parameters
- Manage learning algorithms
- Customize user experience

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)

### Quick Start with Docker

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd lingua-ai
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start the services**

   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Web UI: http://localhost:3000
   - API documentation: http://localhost:8000/docs

### Local Development Setup

**Backend Development:**

```bash
cd apps/api
pip install -r requirements.txt
python main.py
```

**Frontend Development:**

```bash
cd apps/web
npm install
npm run dev
```

## Development Workflow

### API Development

- API server runs on port 8000
- Automatic API documentation available at `/docs` (Swagger UI)
- Database migrations handled via models
- Configuration via environment variables

### Frontend Development

- Development server with hot reload at port 5173
- TypeScript support with strict type checking
- OpenAPI-based type-safe API client
- Vue 3 Composition API with modern tooling

### Database

- PostgreSQL for persistent data storage
- SQLAlchemy ORM for data modeling
- Migration scripts for schema management

## Features in Detail

### AI Article Processing

- Extract key concepts and vocabulary
- Generate comprehension questions
- Identify difficult passages
- Provide contextual translations

### Learning Analytics

- Track student progress
- Measure comprehension levels
- Identify learning gaps
- Provide performance insights

### Personalization

- Adaptive difficulty adjustment
- Customized learning recommendations
- Progress-based content selection
- Individual learning pace support

## Configuration

### Environment Variables

Create a `.env` file in the project root with necessary configuration:

```env
DATABASE_URL=postgresql://user:password@db:5432/lingua_ai
API_WORKERS=4
DEBUG=false
```

### System Settings

System-wide settings can be configured through:

- Admin interface
- System settings API endpoint
- Configuration files in `apps/api/data/`

## API Documentation

Once the API is running, comprehensive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Create a feature branch
2. Commit your changes with clear messages
3. Submit a pull request with detailed description
4. Ensure all tests pass and code follows project standards

## License

[Add your license information here]

## Support

For issues, questions, or suggestions, please:

1. Check existing documentation
2. Open an issue on the project repository
3. Contact the development team

## Roadmap

- [ ] Mobile app version
- [ ] Gamification features
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Real-time collaboration features
- [ ] Speech recognition and pronunciation feedback

---

**Last Updated:** 2026-05-18

For more information, visit the project repository or contact the development team.
