# Contributing guide to Dataset Cleaner

First of all, thank you for your interest in contributing. Projects like this improve because of people like you.

To keep the project organized, maintainable, and scalable, please follow these guidelines before submitting code or reporting issues.

---

## 1. Reporting bugs or suggesting features

Before opening a new *Issue*, please:

1. Check the **Issues** tab to ensure the bug or suggestion has not already been reported.
2. If it is a new issue, open an *Issue* including:

   * Your operating system and Python version
   * Exact steps to reproduce the problem
   * Expected behavior vs. actual behavior
   * Screenshots, if the issue is UI-related


## 2. Development environment setup

Setting up the development environment is intentionally simple thanks to the automated orchestration script.

1. **Fork** this repository to your GitHub account.

2. **Clone** your fork locally:

   ```bash
   git clone https://github.com/VR-Alejandro/dataset-cleaner.git
   cd dataset-cleaner
   ```

3. Create a descriptive branch for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   # or for bug fixes:
   git checkout -b fix/bug-description
   ```

4. Run the application:

   No manual virtual environment setup is required. Simply execute:

   ```bash
   python3 run.py
   ```

   This script will:

   * Create an isolated `.venv`
   * Install all required dependencies
   * Start the application automatically


## 3. Code and design standards

To maintain a professional and cohesive codebase, please follow these standards:

### Backend (Python / FastAPI)

* Follow **PEP 8** for code readability
* Ensure complex functions include:

  * Clear docstrings
  * Proper type hints
* If you add a new dependency, update:

  ```
  app/requirements.txt
  ```

### Frontend (HTML / CSS / JavaScript)

* **Glassmorphism design**:

  * Use translucent backgrounds (`rgba`)
  * Apply blur effects (`backdrop-filter: blur()`)
  * Maintain soft shadows and consistent visual hierarchy

* Avoid inline styles in HTML

  * Use the `styles.css` or `report.css` files instead


## 4. Submitting pull requests (PRs)

When your changes are ready:

1. Ensure the application runs cleanly with:

   ```bash
   python3 run.py
   ```

   and produces no console errors.

2. Push your changes to your fork.

3. Open a pull request targeting the `main` branch of the original repository.

4. In your PR description, clearly explain:

   * What problem this change solves
   * How the change can be tested (visually or logically)
   * Reference the related Issue if applicable (e.g., `Closes #12`)


## Final note

By defining explicit design standards, you prevent inconsistent contributions that could break the visual identity of the project (for example, introducing outdated UI elements that conflict with the glassmorphic style).

---

Thank you for contributing. Your work is appreciated and will be reviewed as soon as possible.
