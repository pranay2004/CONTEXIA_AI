# Contributing to CONTEXIA

First off, thank you for considering contributing to CONTEXIA! 🎉

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates.

**When submitting a bug report, include:**
- Clear, descriptive title
- Exact steps to reproduce
- Expected vs. actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, Node version)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues.

**Include:**
- Clear use case description
- Expected benefits
- Potential implementation approach
- Any mockups or examples

### Your First Code Contribution

Unsure where to begin? Look for issues labeled:
- `good first issue` - Simple tasks for beginners
- `help wanted` - Issues that need assistance

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our style guidelines
3. **Test thoroughly** - ensure all tests pass
4. **Update documentation** if needed
5. **Submit a pull request**

## Development Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+
- Redis

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Running Tests

**Backend:**
```bash
cd backend
pytest
```

**Frontend:**
```bash
cd frontend
npm test
```

## Pull Request Process

1. **Update README.md** with any new environment variables or setup steps
2. **Update requirements.txt** or `package.json` if adding dependencies
3. **Ensure all tests pass** and add new tests for new features
4. **Follow commit message conventions** (see below)
5. **Request review** from maintainers

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(generator): Add support for Instagram Reels generation

- Implemented Reels-specific content formatting
- Added vertical video script generation
- Updated tests for new platform

Closes #123
```

## Style Guidelines

### Python (Backend)

- Follow **PEP 8** style guide
- Use **Black** for code formatting: `black .`
- Use **type hints** where appropriate
- Maximum line length: 100 characters
- Use **docstrings** for functions and classes

**Example:**
```python
def generate_content(
    text: str,
    platforms: List[str],
    tone: str = "professional"
) -> Dict[str, Any]:
    """
    Generate platform-specific content from input text.
    
    Args:
        text: Source content to transform
        platforms: List of target platforms
        tone: Content tone (default: professional)
        
    Returns:
        Dictionary with platform-specific content
    """
    pass
```

### TypeScript/JavaScript (Frontend)

- Follow **Airbnb JavaScript Style Guide**
- Use **Prettier** for formatting
- Use **TypeScript** for type safety
- Functional components with hooks
- Use **named exports** over default exports

**Example:**
```typescript
interface ContentGenerationProps {
  uploadedFile: File | null
  onGenerate: (content: GeneratedContent[]) => void
}

export const ContentGenerator: React.FC<ContentGenerationProps> = ({
  uploadedFile,
  onGenerate
}) => {
  // Component logic
}
```

### Git Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Make commits:**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. **Keep branch updated:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

4. **Push and create PR:**
   ```bash
   git push origin feat/your-feature-name
   ```

## Testing Guidelines

### Backend Testing

- Write tests for all new features
- Maintain >80% code coverage
- Use **pytest** and **factory_boy**

```python
def test_content_generation():
    """Test content generation for LinkedIn platform."""
    result = generate_content(
        text="Sample text",
        platforms=["linkedin"]
    )
    assert "linkedin" in result
    assert len(result["linkedin"]) > 0
```

### Frontend Testing

- Test user interactions
- Test edge cases and error states
- Use **Jest** and **React Testing Library**

```typescript
describe('ContentGenerator', () => {
  it('should generate content on file upload', () => {
    // Test implementation
  })
})
```

## Documentation

- Update README.md for user-facing changes
- Add JSDoc/docstrings for all public APIs
- Include code examples in documentation
- Update API documentation when endpoints change

## Questions?

Feel free to:
- Open an issue with the `question` label
- Join our [Discord community](https://discord.gg/contexia)
- Email: support@contexia.ai

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

Thank you for contributing to CONTEXIA! 🚀
