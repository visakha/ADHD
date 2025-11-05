# Claude Code Instructions

## Project Context
This is an ADHD Productivity Trio application - a three-way team productivity system with AI agents (Spark and Proto) built using Python, TKinter, and the Anthropic Claude API.

## Coding Preferences

### Type Hints
- **ALWAYS use strong typing** in Python code
- Add type hints to:
  - All function parameters
  - All function return types
  - Class attributes (declare types in `__init__` or as class variables)
  - Local variables where it improves clarity
- Import from `typing` module: `Dict`, `List`, `Optional`, `Tuple`, `Any`, etc.
- Use `-> None` for functions that don't return a value
- Use `Optional[Type]` for values that can be None

### Code Style
- Follow PEP 8 conventions
- Use descriptive variable names
- Add docstrings to all functions and classes
- Keep functions focused and modular
- Use type-safe patterns throughout

### Examples
```python
from typing import Dict, List, Optional, Tuple, Any

def process_data(data: List[Dict[str, Any]], threshold: int = 10) -> Optional[str]:
    """Process data and return result."""
    result: Optional[str] = None
    # ... implementation
    return result

class MyClass:
    def __init__(self, name: str) -> None:
        self.name: str = name
        self.items: List[str] = []
```

## Project Structure
- Main application: `productivity_trio.py`
- Database: SQLite (productivity_trio.db)
- Configuration: JSON (config.json)

## Development Guidelines
1. Maintain thread-safe database access using locks
2. Keep UI components separated from business logic
3. Use background threads for API calls to prevent UI blocking
4. Follow the existing agent architecture patterns
5. Test thoroughly before committing

## Git Workflow
- Work on feature branches
- Write clear, descriptive commit messages
- Push to the designated branch when changes are complete
