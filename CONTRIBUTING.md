# Contributing to Dagent 🤝

Thank you for your interest in contributing to Dagent! This guide will help you get started with contributing to our multi-agent DAG framework.

## 🚀 Quick Start for Contributors

### Development Setup

1. **Fork and Clone**
```bash
git fork https://github.com/your-username/dagent.git
cd dagent
```

2. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Add your API keys to .env
```

3. **Test Your Setup**
```bash
python main.py
```

## 🎯 Ways to Contribute

### 🐛 Bug Reports
- Use GitHub Issues with the `bug` label
- Include detailed reproduction steps
- Provide relevant error messages and logs
- Include your environment details (OS, Python version, etc.)

### ✨ Feature Requests
- Use GitHub Issues with the `enhancement` label
- Describe the problem you're trying to solve
- Explain your proposed solution
- Consider backward compatibility

### 🔧 Code Contributions
- Bug fixes
- New agent tools
- Performance improvements
- Documentation improvements

### 📚 Documentation
- README improvements
- Code comments and docstrings
- Usage examples
- Architecture documentation

## 🛠️ Development Guidelines

### Code Style

**Python Standards**
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write docstrings for public methods
- Keep functions focused and atomic

**Naming Conventions**
- `snake_case` for variables and functions
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names over short names

### Architecture Principles

**Adding New Tools**
1. Extend `BaseAgnoTool` in `src/tools/base.py`
2. Add to `src/tools/__init__.py`
3. Update `src/kernel/kernel.py` tool registry
4. Add documentation and examples

**Modifying Core Components**
- **Planner**: Changes to query decomposition logic
- **DAG Builder**: Modifications to graph construction
- **Kernel**: Execution orchestration changes
- **Judge**: Quality evaluation improvements

**Agent Profiles**
- Add new task types in `AgentProfile` enum
- Update profile generation logic
- Ensure compatibility with existing profiles

### Testing Guidelines

**Manual Testing**
```bash
# Test basic functionality
python main.py

# Test with different query types
python -c "
import asyncio
from src.framework import AgenticDAG

async def test():
    framework = AgenticDAG()
    result = await framework.execute('Your test query here')
    print('Success:', result['success'])

asyncio.run(test())
"
```

**Integration Testing**
- Test with different API providers (OpenAI, Gemini)
- Verify tool functionality works as expected
- Check DAG execution with various dependency patterns

## 📝 Pull Request Process

### Before Submitting

1. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make Your Changes**
- Follow code style guidelines
- Add appropriate comments
- Update documentation if needed

3. **Test Your Changes**
- Run manual tests with various queries
- Ensure no existing functionality breaks
- Test with both API providers if possible

### Submitting Your PR

1. **Create Pull Request**
- Use a clear, descriptive title
- Explain what your PR does and why
- Reference any related issues

2. **PR Template**
```markdown
## What This PR Does
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested manually with sample queries
- [ ] Verified no regressions
- [ ] Updated documentation

## Related Issues
Fixes #(issue number)
```

### Review Process

1. **Automated Checks** (when available)
   - Code style validation
   - Basic import/syntax checks

2. **Manual Review**
   - Code quality and architecture fit
   - Testing adequacy
   - Documentation completeness

3. **Approval and Merge**
   - Requires at least one maintainer approval
   - All conversations must be resolved

## 🏗️ Component-Specific Guidelines

### Adding New Tools

```python
# src/tools/your_new_tool.py
from .base import BaseAgnoTool

class YourNewTool(BaseAgnoTool):
    """Brief description of what this tool does."""

    def your_method(self, param: str) -> str:
        """
        Method description.

        Args:
            param: Parameter description

        Returns:
            Return value description
        """
        # Implementation
        return result
```

### Modifying Planner Logic

When changing the planner:
- Maintain backward compatibility with existing plan formats
- Update prompt templates in `src/planner/prompts.py`
- Test with various query types
- Consider impact on DAG construction

### Extending Agent Profiles

To add new agent capabilities:
- Update `AgentProfile` class in `src/planner/planner.py`
- Modify profile generation logic in `src/kernel/profiles.py`
- Update planner prompts to include new options
- Test with different complexity levels

## 🚦 Code Quality Standards

### Performance Considerations
- Minimize API calls where possible
- Use parallel execution for independent tasks
- Avoid memory leaks in long-running operations
- Consider token limits for LLM interactions

### Error Handling
- Use specific exception types
- Provide meaningful error messages
- Implement graceful degradation
- Log errors appropriately

### Security
- Never commit API keys or secrets
- Validate user inputs
- Use environment variables for configuration
- Follow secure coding practices

## 🎉 Recognition

Contributors will be:
- Added to the project's contributor list
- Credited in release notes for significant contributions
- Mentioned in documentation for major features

## 🆘 Getting Help

**Development Questions**
- Open a GitHub Discussion
- Tag maintainers for urgent issues
- Check existing issues for similar problems

**Architecture Questions**
- Review existing code patterns
- Check documentation for design decisions
- Ask in GitHub Discussions for clarification

## 📋 Checklist for Contributors

Before submitting your contribution:

- [ ] Code follows the project style guidelines
- [ ] Changes are tested manually
- [ ] Documentation is updated (if applicable)
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes
- [ ] No sensitive information (API keys, etc.) is included
- [ ] Changes are backward compatible (or breaking changes are noted)

Thank you for contributing to Dagent! Every contribution, no matter how small, helps make the project better for everyone. 🚀