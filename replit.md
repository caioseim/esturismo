# ES Turismo - Driver Registration System

## Overview

ES Turismo is a Flask-based web application designed to manage driver registration for a Brazilian tourism bus company. The system provides a complete solution for registering drivers, managing their documents, tracking document expiration dates, and maintaining backup capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Bootstrap 5.3.0 for responsive UI components
- **JavaScript**: Vanilla JavaScript with custom validation and masking utilities
- **Template Engine**: Jinja2 (Flask's default templating engine)
- **Styling**: Custom CSS with Bootstrap integration, using CSS variables for theming

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: Simple MVC pattern with routes, templates, and utility functions
- **File Structure**: Modular approach with separate files for routes, utilities, and application configuration
- **Session Management**: Flask sessions with configurable secret key

### Data Storage
- **Primary Storage**: JSON file-based storage (`data/motoristas.json`)
- **File Storage**: Local filesystem for document uploads in `uploads/` directory
- **Backup Strategy**: Manual backup functionality with file compression

## Key Components

### Core Application (`app.py`)
- Flask application initialization
- Upload folder configuration (16MB max file size)
- Session secret key management
- Debug mode configuration for development

### Routing Layer (`routes.py`)
- Main application routes including index, registration, and listing
- File upload handling with security validation
- Document expiration tracking and alerts
- Backup functionality

### Data Management (`utils.py`)
- JSON-based data persistence
- CPF validation using Brazilian algorithm
- Phone number formatting for Brazilian standards
- Driver data CRUD operations

### Frontend Components
- **Base Template**: Responsive navigation with Bootstrap navbar
- **Dashboard**: Statistics overview with document expiration alerts
- **Registration Form**: Multi-step form with file uploads and validation
- **Driver Listing**: Searchable and filterable driver table
- **Individual Driver View**: Detailed driver profile with document status

## Data Flow

1. **Driver Registration**: Form submission → File upload → Data validation → JSON storage
2. **Document Tracking**: Automatic expiration date calculation → Alert generation → Dashboard display
3. **File Management**: Secure file upload → File validation → Filesystem storage with UUID naming
4. **Search/Filter**: Client-side JavaScript filtering → Real-time table updates

## External Dependencies

### Frontend Libraries
- **Bootstrap 5.3.0**: UI framework for responsive design
- **Font Awesome 6.4.0**: Icon library for consistent iconography

### Python Packages
- **Flask**: Web framework
- **Werkzeug**: WSGI utilities (included with Flask)
- **Standard Library**: `os`, `json`, `uuid`, `datetime`, `shutil`, `re`

### File Handling
- **Allowed Formats**: PNG, JPG, JPEG, GIF, PDF
- **Security**: Filename sanitization using `secure_filename`
- **Storage**: Local filesystem with organized directory structure

## Deployment Strategy

### Development Environment
- **Host**: `0.0.0.0` (all interfaces)
- **Port**: 5000
- **Debug Mode**: Enabled for development
- **Logging**: DEBUG level logging enabled

### File System Requirements
- **Upload Directory**: `uploads/` (auto-created)
- **Data Directory**: `data/` (auto-created)
- **Static Assets**: `static/` for CSS and JavaScript files
- **Templates**: `templates/` for HTML templates

### Configuration
- **Session Secret**: Environment variable `SESSION_SECRET` with fallback
- **Upload Limits**: 16MB maximum file size
- **File Extensions**: Restricted to safe formats only

### Security Considerations
- CPF validation using official Brazilian algorithm
- File extension validation for uploads
- Secure filename handling to prevent directory traversal
- Session-based user interaction (no authentication system currently)

## Recent Changes

### January 2025
- ✅ Sistema completo de cadastro de motoristas implementado
- ✅ Upload e armazenamento de fotos dos motoristas
- ✅ Upload de documentos (CNH, Curso de Passageiros, Comprovante de Residência)  
- ✅ Sistema de holerites organizados por ano/mês
- ✅ Controle de vencimento de documentos com alertas
- ✅ Sistema de backup completo dos dados
- ✅ Busca e filtros avançados
- ✅ Validação de CPF brasileiro
- ✅ Máscaras automáticas para telefone
- ✅ Preview de imagens no formulário
- ✅ Interface responsiva com Bootstrap
- ✅ Campo de tipo de vínculo (Registrado/Freelancer)
- ✅ Sistema de ativação/desativação de motoristas
- ✅ Funcionalidade de exclusão permanente de motoristas
- ✅ Download de holerites individuais
- ✅ Filtros por tipo de vínculo na listagem
- ✅ Indicação visual de motoristas inativos

## Notes

The application uses a simple JSON file for data storage, which could be migrated to PostgreSQL with Drizzle ORM for better scalability and data integrity. The current architecture supports easy migration to a database system while maintaining the existing API structure.

All data is stored locally on the user's computer with no external server dependencies, making it perfect for desktop use within the company.