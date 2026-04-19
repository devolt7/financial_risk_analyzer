# Contributing to Financial Risk Analyzer

Thank you for your interest in contributing! This document provides guidelines for contributing.

## 📋 Code Standards

### Python Style Guide
- Follow PEP 8 conventions
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names

### Docstrings
- Use Google-style docstrings for all functions
- Document parameters, return values, and exceptions
- Include usage examples for complex functions

Example:
```python
def calculate_var(self, returns, confidence=0.95):
    """
    Calculate Value at Risk (VaR)
    
    Args:
        returns (pd.Series): Series of daily returns
        confidence (float): Confidence level (default: 0.95)
        
    Returns:
        dict: VaR metrics including daily and annual values
        
    Raises:
        ValueError: If confidence level is not between 0 and 1
    """
    # Implementation
```

## 🔍 Testing

Before submitting:
1. Test with multiple stock symbols
2. Test with different time periods
3. Verify numeric calculations
4. Check for edge cases (e.g., negative returns)

## 📝 Commit Messages

Use clear, descriptive commit messages:
- ✅ `Add VaR calculation to statistical analysis`
- ❌ `fix bug`

## 🚀 Pull Request Process

1. Create a descriptive PR title
2. Link to any related issues
3. Describe changes made and why
4. Test thoroughly before submission

## 🐛 Reporting Bugs

Include:
- Stock symbols used
- Expected vs actual behavior
- Error messages or logs
- Python/dependencies versions

## 💡 Feature Requests

Describe:
- Problem being solved
- Proposed solution
- Example use case
- Impact on performance

## 📚 Documentation

Help improve:
- README.md clarifications
- Code comments
- Example scripts
- Mathematical formulas

## 🎨 Areas for Contribution

- **UI/UX**: Improve dashboard design
- **Performance**: Optimize calculations
- **Features**: Add new analysis types
- **Testing**: Increase test coverage
- **Documentation**: Enhance guides

## ✅ Pre-submission Checklist

- [ ] Code follows PEP 8
- [ ] Functions are documented
- [ ] No hardcoded values
- [ ] Works with multiple stocks
- [ ] Error handling implemented
- [ ] Console logs cleaned up

## 📞 Questions?

- Check existing issues/PRs
- Review documentation
- Run examples

Thank you for contributing! 🙏
