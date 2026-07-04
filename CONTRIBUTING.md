# Contributing to Last-Mile Route Optimizer

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/routeoptim.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests and linting
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

Follow the setup instructions in README.md to set up your development environment.

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where possible
- Format code with `black`
- Lint with `ruff`
- Maximum line length: 100 characters

### TypeScript/React (Frontend)
- Follow the Airbnb JavaScript Style Guide
- Use functional components with hooks
- Format code with `prettier`
- Lint with `eslint`
- Use TypeScript strict mode

## Testing

### Backend
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend
```bash
cd frontend
npm run test
```

## Pull Request Guidelines

1. **Title**: Use a clear and descriptive title
2. **Description**: Explain what changes you made and why
3. **Tests**: Include tests for new features
4. **Documentation**: Update README.md if needed
5. **Commits**: Use clear commit messages

## Reporting Issues

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Environment (OS, browser, Python/Node version)

## Feature Requests

Feature requests are welcome! Please:
- Check if the feature already exists
- Provide a clear use case
- Explain why it would be valuable

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what is best for the community

## Questions?

Feel free to open an issue for any questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
