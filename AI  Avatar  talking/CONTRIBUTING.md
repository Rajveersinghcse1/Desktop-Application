# Contributing to AI Avatar Studio

Thank you for your interest in contributing to AI Avatar Studio! This document provides guidelines and instructions for contributing.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [How to Contribute](#how-to-contribute)
4. [Development Workflow](#development-workflow)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)
9. [Community](#community)

## Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

**Unacceptable behavior:**
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Violations may result in temporary or permanent ban from the project. Report violations to: conduct@aiavatars.studio

## Getting Started

### Prerequisites

- Python 3.8-3.11
- Git
- FFmpeg
- Basic knowledge of Python, PyTorch, and computer vision

### Initial Setup

1. **Fork the repository**
   ```bash
   # Click 'Fork' on GitHub, then:
   git clone https://github.com/YOUR_USERNAME/ai-avatar-studio.git
   cd ai-avatar-studio
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate (Windows)
   venv\Scripts\activate
   
   # Activate (Linux/Mac)
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development tools
   pip install pytest black flake8 mypy
   ```

3. **Configure pre-commit hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. **Run tests to verify setup**
   ```bash
   python run_avatar_test.py
   pytest
   ```

## How to Contribute

### Types of Contributions

**Bug Reports**
- Use GitHub Issues
- Include system information
- Provide steps to reproduce
- Include error messages and logs

**Feature Requests**
- Use GitHub Discussions
- Describe the use case
- Explain expected behavior
- Consider implementation details

**Code Contributions**
- Bug fixes
- New features
- Performance improvements
- Documentation updates
- Test additions

**Documentation**
- Fix typos or clarify existing docs
- Add examples
- Translate documentation
- Write tutorials

### Finding Issues to Work On

- Look for `good first issue` label
- Check `help wanted` label
- Review open issues and discussions
- Ask maintainers for guidance

## Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature

# Or for bug fix
git checkout -b fix/issue-123
```

### 2. Make Changes

- Write clean, readable code
- Follow coding standards (see below)
- Add tests for new features
- Update documentation as needed
- Keep commits atomic and focused

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_face_detection.py

# Check code style
black --check .
flake8 .

# Type checking
mypy core/ utils/

# Run component tests
python run_avatar_test.py

# Run health check
python health_check.py --detailed
```

### 4. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add: Support for custom voice models"

# Push to your fork
git push origin feature/my-feature
```

### Commit Message Format

Follow conventional commits:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `Add:` - New feature
- `Fix:` - Bug fix
- `Update:` - Update existing feature
- `Refactor:` - Code refactoring
- `Docs:` - Documentation changes
- `Test:` - Test additions/changes
- `Style:` - Code style changes
- `Perf:` - Performance improvements
- `Chore:` - Maintenance tasks

**Examples:**
```
Add: Support for custom voice models in TTS engine

Implements custom voice model loading and configuration.
Adds new TTSEngine subclass for custom models.

Closes #123
```

```
Fix: Memory leak in video processing pipeline

Fixed issue where video frames were not being properly released
after processing, causing memory to grow unbounded.

Fixes #456
```

## Coding Standards

### Python Style

- Follow PEP 8
- Maximum line length: 100 characters
- Use 4 spaces for indentation
- Use single quotes for strings
- Use type hints where appropriate

### Code Formatting

```bash
# Format with black
black --line-length 100 .

# Check with flake8
flake8 --max-line-length 100 .
```

### Naming Conventions

- **Classes:** `PascalCase`
- **Functions/Methods:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Private methods:** `_leading_underscore`
- **Module names:** `lowercase` or `snake_case`

### Docstrings

Use Google-style docstrings:

```python
def my_function(arg1: str, arg2: int) -> bool:
    """
    Short description of function.
    
    Longer description explaining the function in detail.
    Can span multiple lines.
    
    Args:
        arg1: Description of first argument
        arg2: Description of second argument
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When arg2 is negative
        TypeError: When arg1 is not a string
    
    Example:
        >>> my_function('test', 42)
        True
    """
    if arg2 < 0:
        raise ValueError("arg2 must be positive")
    return True
```

### Code Structure

- Keep functions small and focused
- Use meaningful variable names
- Avoid magic numbers (use constants)
- Handle errors gracefully
- Add logging where appropriate
- Write self-documenting code

### Example Good Code

```python
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

class VideoProcessor:
    """Process video files with various operations."""
    
    def __init__(self, config: dict):
        """
        Initialize video processor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration parameters."""
        required_keys = ['input_path', 'output_path']
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
    
    def process(self, retries: int = MAX_RETRIES) -> Optional[str]:
        """
        Process video file.
        
        Args:
            retries: Number of retry attempts
        
        Returns:
            Path to processed video, or None if failed
        """
        for attempt in range(retries):
            try:
                result = self._process_internal()
                logger.info(f"Video processed successfully: {result}")
                return result
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == retries - 1:
                    logger.error("All retry attempts failed")
                    return None
        
        return None
```

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests independent
- Mock external dependencies

### Test Structure

```python
import pytest
from core.my_module import MyClass

class TestMyClass:
    """Tests for MyClass."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.instance = MyClass()
    
    def test_basic_functionality(self):
        """Test basic functionality works correctly."""
        result = self.instance.process('input')
        assert result is not None
        assert result.success is True
    
    def test_error_handling(self):
        """Test error handling for invalid input."""
        with pytest.raises(ValueError):
            self.instance.process(None)
    
    def test_edge_case_empty_input(self):
        """Test edge case with empty input."""
        result = self.instance.process('')
        assert result is not None
        assert result.success is False
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=utils --cov-report=html

# Run specific test file
pytest tests/test_face_detection.py

# Run specific test
pytest tests/test_face_detection.py::TestFaceDetector::test_detect

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Update docstrings when changing code
- Include usage examples in docstrings
- Document complex algorithms

### User Documentation

When adding features, update:
- `README.md` - If it affects getting started
- `USAGE_GUIDE.md` - For user-facing features
- `API_REFERENCE.md` - For API changes
- `FAQ.md` - For common questions

### Documentation Style

- Use clear, concise language
- Provide examples
- Include screenshots for GUI features
- Keep formatting consistent
- Test all code examples

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commits are clean and descriptive
- [ ] Branch is up to date with main
- [ ] No merge conflicts

### Submitting PR

1. **Push your branch**
   ```bash
   git push origin feature/my-feature
   ```

2. **Create Pull Request on GitHub**
   - Click "New Pull Request"
   - Select your branch
   - Fill out PR template

3. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] All tests pass
   - [ ] Added new tests
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings
   
   ## Related Issues
   Fixes #123
   Relates to #456
   ```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks
   - Coverage reports

2. **Maintainer Review**
   - Code review by maintainers
   - Feedback and requested changes
   - Discussion if needed

3. **Address Feedback**
   ```bash
   # Make changes
   git add .
   git commit -m "Update: Address review feedback"
   git push origin feature/my-feature
   ```

4. **Approval and Merge**
   - Approved by maintainer(s)
   - Squash and merge or rebase
   - Branch deleted after merge

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Email**: contact@aiavatars.studio

### Getting Help

- Check existing documentation
- Search closed issues
- Ask in GitHub Discussions
- Be patient and respectful

### Recognition

Contributors are recognized in:
- CHANGELOG.md
- Repository contributors list
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, please:
1. Check this document
2. Search existing issues/discussions
3. Create a new discussion
4. Contact maintainers

Thank you for contributing to AI Avatar Studio! 🎬✨
