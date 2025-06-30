# Asset Data Manager

A Django-based REST API service for managing versioned architectural and design elements, rooms, and their associated files. This system provides comprehensive version control, file management, and validation capabilities for 3D design platforms.

## Features

- **Versioned Data Management**: Complete version control for design elements and rooms with soft deletion
- **File Pipeline**: AWS S3 integration with support for CAD files (DXF), Revit families (RFA), images (PNG/JPG), and JSON metadata
- **Schema Validation**: Multi-version JSON schema validation system
- **Change Tracking**: Automated detection and categorization of data changes (Major, Minor, Patch)
- **Background Processing**: Asynchronous file processing via SQS message queues
- **Multi-Environment Support**: Configurations for local development through production

## Build Status

| Branch     | Status |
|------------|--------|
| main (dev) | [![GitHub Actions](https://github.com/veev-com/asset-data-manager/actions/workflows/studio.yml/badge.svg?branch=main)](https://github.com/veev-com/asset-data-manager/actions/workflows/studio.yml?query=branch%3Amain) |
| stage      | [![GitHub Actions](https://github.com/veev-com/asset-data-manager/actions/workflows/studio.yml/badge.svg?branch=staging)](https://github.com/veev-com/asset-data-manager/actions/workflows/studio.yml?query=branch%3Astage) |
| prod       | [![GitHub Actions](https://github.com/veev-com/asset-data-manager/actions/workflows/studio.yml/badge.svg?branch=production)](https://github.com/veev-com/asset-data-manager/actions/workflows/studio.yml?query=branch%3Aprod) |

## API Documentation

- **OpenAPI Schema**: Available at `/studio/api/schema/`
- **Swagger UI**: Available at `/studio/api/swagger/`

## Local Installation and Setup

### Prerequisites

- Python 3.8+
- pip
- Virtual environment tool (venv, virtualenv, or conda)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/veev-com/asset-data-manager.git
   cd asset-data-manager
   ```

2. **Create and activate virtual environment**

   **Windows (Command Prompt):**
   ```cmd
   # Using venv
   python -m venv venv
   venv\Scripts\activate
   
   # Or using conda
   conda create -n studio-be python=3.8
   conda activate studio-be
   ```
   
   **Windows (PowerShell):**
   ```powershell
   # Using venv
   python -m venv venv
   venv\Scripts\Activate.ps1
   
   # If execution policy error occurs:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   venv\Scripts\Activate.ps1
   
   # Or using conda
   conda create -n studio-be python=3.8
   conda activate studio-be
   ```
   
   **macOS/Linux:**
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate
   
   # Or using conda
   conda create -n studio-be python=3.8
   conda activate studio-be
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   **Windows:**
   ```cmd
   # Create .env file in root directory
   copy .env.example .env
   # Or create manually if example doesn't exist
   ```
   
   **macOS/Linux:**
   ```bash
   # Create .env file in root directory
   cp .env.example .env  # If example exists, or create manually
   ```
   
   Add the following to your `.env` file:
   ```env
   DJANGO_SETTINGS_MODULE=server.settings.veev-local
   DEBUG=True
   # Add other environment-specific variables as needed
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

### Running the Development Server

1. **Start the Django development server**
   ```bash
   python manage.py runserver
   ```
   
   The API will be available at `http://localhost:8000`

2. **Start background processing (optional, for file handling)**
   
   **Windows:**
   ```cmd
   # Open a new Command Prompt/PowerShell window
   cd path\to\asset-data-manager
   venv\Scripts\activate
   python manage.py poller_storage
   ```
   
   **macOS/Linux:**
   ```bash
   # Open a new terminal window
   cd /path/to/asset-data-manager
   source venv/bin/activate
   python manage.py poller_storage
   ```

### Accessing the API

- **Health Check**: `GET http://localhost:8000/health/`
- **API Documentation**: `GET http://localhost:8000/studio/api/swagger/`
- **Elements Endpoint**: `GET http://localhost:8000/studio/element/`
- **Rooms Endpoint**: `GET http://localhost:8000/studio/room/`
- **Validation Endpoint**: `POST http://localhost:8000/studio/validator/validate/`

## Platform-Specific Notes

### Windows

**Python Installation:**
- Download Python from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Alternatively, install via Microsoft Store or use `winget install Python.Python.3.11`

**Common Windows Issues:**
- **PowerShell Execution Policy**: If you get execution policy errors, run:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- **Long Path Names**: Enable long path support in Windows if you encounter path length issues
- **Path Separators**: Use backslashes (`\`) for Windows paths or forward slashes (`/`) which work in most contexts

**Recommended Terminal:**
- Windows Terminal (available from Microsoft Store)
- PowerShell 7+ for better compatibility
- Git Bash (comes with Git for Windows)

### macOS

**Python Installation:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Or using pyenv for multiple Python versions
brew install pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

**Common macOS Issues:**
- **Xcode Command Line Tools**: Install if you get compiler errors:
  ```bash
  xcode-select --install
  ```
- **PATH Issues**: Add Python to PATH in `~/.zshrc` or `~/.bash_profile`:
  ```bash
  export PATH="/usr/local/opt/python@3.11/bin:$PATH"
  ```

### Linux (Ubuntu/Debian)

**Python Installation:**
```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3.11 python3.11-venv python3-pip

# Create symbolic link (optional)
sudo ln -s /usr/bin/python3.11 /usr/bin/python
```

### Environment Settings

The application uses different settings files for various environments:

- **Local Development**: `server.settings.veev-local`
- **Development**: `server.settings.veev-dev`
- **Staging**: `server.settings.veev-stage`
- **Production**: `server.settings.veev-prod`

### AWS Configuration (Optional for Local Development)

For full functionality including file uploads, configure AWS credentials:

**Windows (Command Prompt/PowerShell):**
```cmd
# Set AWS credentials via environment variables
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_DEFAULT_REGION=us-east-1

# Or use AWS CLI
aws configure
```

**macOS/Linux:**
```bash
# Set AWS credentials via environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Or use AWS CLI
aws configure
```

## Testing

### Running Tests

1. **Run all tests**
   ```bash
   python manage.py test
   ```

2. **Run specific test modules**
   ```bash
   # Test elements functionality
   python manage.py test studio.tests.test_element
   
   # Test rooms functionality
   python manage.py test studio.tests.test_room
   
   # Test schema validation
   python manage.py test studio.tests.test_schema
   
   # Test validators
   python manage.py test studio.tests.test_validator
   ```

3. **Run tests with coverage**
   ```bash
   # Install coverage first
   pip install coverage
   
   # Run tests with coverage
   coverage run --source='.' manage.py test
   coverage report
   coverage html  # Generates HTML coverage report
   ```

4. **Run tests with verbose output**
   ```bash
   python manage.py test --verbosity=2
   ```

### Test Data

Test data is located in the `studio/tests/data/` directory and includes:
- Sample schema files for validation testing
- Mock S3 notification payloads
- Element and room test data

### Testing Different Scenarios

```bash
# Test element creation and versioning
python manage.py test studio.tests.test_element.TestElement.test_upgrade

# Test room-element relationships
python manage.py test studio.tests.test_room.TestRoom.test_create_room_elements

# Test schema validation with different versions
python manage.py test studio.tests.test_schema.TestSchema.test_schema_validation

# Test file type validation
python manage.py test studio.tests.test_file_type.TestFileType
```

## API Usage Examples

### Creating an Element

```bash
curl -X POST http://localhost:8000/studio/element/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Modern Door", "category": "door"}'
```

### Creating a Room

```bash
curl -X POST http://localhost:8000/studio/room/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Living Room", "category": "living", "function": "Entertainment"}'
```

### Validating Data

```bash
curl -X POST http://localhost:8000/studio/validator/validate/ \
  -H "Content-Type: application/json" \
  -d '{"version": "1.0.0", "corePlanName": "Sample Plan", "additionalData": {}}'
```

### Upgrading Element Version

```bash
curl -X POST http://localhost:8000/studio/element/1/upgrade/
```

## Development Workflow

### Making Changes

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and test**
   ```bash
   # Make your changes
   python manage.py test  # Run tests
   ```

3. **Run migrations if models changed**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add your feature description"
   git push origin feature/your-feature-name
   ```

### Database Management

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Rollback migration
python manage.py migrate studio 0001

# Show migration status
python manage.py showmigrations
```

### Debugging

```bash
# Django shell for debugging
python manage.py shell

# Database shell
python manage.py dbshell

# Check for issues
python manage.py check
```

## Troubleshooting

### Common Issues

1. **Database locked error**
   - Stop the development server and any background processes
   - Delete `db.sqlite3` file and run migrations again

2. **Module import errors**
   - Ensure virtual environment is activated
   - Verify all dependencies are installed: `pip install -r requirements.txt`

3. **AWS credential errors**
   - Verify AWS credentials are configured
   - Check AWS region settings

4. **Test failures**
   - Ensure test database is clean: `python manage.py test --keepdb=false`
   - Check for any lingering background processes

### Platform-Specific Issues

**Windows:**
- **Path issues**: Use forward slashes in file paths or escape backslashes
- **Permission errors**: Run Command Prompt/PowerShell as Administrator if needed
- **Virtual environment activation**: Ensure you're using the correct activation script:
  - Command Prompt: `venv\Scripts\activate.bat`
  - PowerShell: `venv\Scripts\Activate.ps1`

**macOS:**
- **Permission denied**: Use `sudo` for system-wide installations or fix ownership:
  ```bash
  sudo chown -R $(whoami) /usr/local/lib/python3.11/site-packages
  ```
- **SSL certificate errors**: Update certificates:
  ```bash
  /Applications/Python\ 3.11/Install\ Certificates.command
  ```

**Linux:**
- **Missing development packages**: Install if you get compilation errors:
  ```bash
  sudo apt-get install python3-dev build-essential
  ```
- **Database connector issues**: Install system packages:
  ```bash
  sudo apt-get install libpq-dev  # For PostgreSQL
  ```

### Getting Help

- Check the API documentation at `/studio/api/swagger/`
- Review test files for usage examples
- Check Django logs for detailed error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

[Add your license information here]