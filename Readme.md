# Personal Test Data Generator – Group I  
![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![Flask](https://img.shields.io/badge/Backend-Flask-lightgrey?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?logo=sqlite)
![Pytest](https://img.shields.io/badge/Tests-Pytest-green?logo=pytest)
![Postman](https://img.shields.io/badge/API-Postman-orange?logo=postman)
![Playwright](https://img.shields.io/badge/E2E-Playwright-purple?logo=microsoft)
![SonarQube](https://img.shields.io/badge/Static--Analysis-SonarQube-lightblue?logo=sonarqube)
![GitHub Actions](https://img.shields.io/badge/CI/CD-GitHub%20Actions-black?logo=githubactions)


---

## Overview  
Grocery Store Manager (GSM) is a web-based management application designed for small grocery stores.
The system allows store owners to:

* Manage products and units of measurement (UOM)

* Track inventory quantities

* Create and manage orders

* Perform revenue simulations

* Calculate inventory spending by month

* Gain insights into sales, profit, and cost drivers

The project was developed as part of the Testing in Software Development exam and focuses heavily on test design, automation, and quality assurance.

Reference sources:  
- [Insperation for backend and UI design](https://github.com/codebasics/python_projects_grocery_webapp.git)  

---

## Project Scope & Goals

This project demonstrates the use of:

* Black-box test design (EP, BVA, Decision Tables)

* White-box testing (unit tests with coverage)

* Integration testing (API + DB, Postman)

* End-to-End testing (Playwright)

* Static analysis tools (Pylint, ESLint, SonarCloud)

* CI/CD automation using GitHub Actions

---

## Project Structure
This is an **outline** of how we planned to organize files and folders for the assignment. 
```
/frontend
/backend
├── dao
├── routes
├── services
├── db
├── app.py

/UI
├── dashboard.html
├── manage-product.html
├── orders.html
├── js

/tests
├── /unittest
├── /integration
│   └── /postman
└── /e2e

/.github
└── /workflows
    └── main.yml

/pdf
├── black-box-test-design.pdf
├── static-analysis-report.pdf
├── risk-assessment.pdf
├── review-report.pdf

requirements.txt
README.md

```

---
## Run the project in local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```
Backend runs on:
* http://127.0.0.1:5050

---

## Frontend (Static HTML)
```bash
cd UI
npx http-server -p 8000
```

Frontend runs on:

* http://127.0.0.1:8000

---

## API Endpoints (Backend)

### Products
| Method | Endpoint              | Description           |
| ------ | --------------------- | --------------------- |
| GET    | `/getProducts`        | Retrieve all products |
| POST   | `/addProduct`         | Add new product       |
| POST   | `/updateProduct`      | Update product        |
| DELETE | `/deleteProduct/<id>` | Delete product        |

### Units of measure
| Method | Endpoint  | Description       |
| ------ | --------- | ----------------- |
| GET    | `/getUOM` | Retrieve all UOMs |

### Orders
| Method | Endpoint            | Description                 |
| ------ | ------------------- | --------------------------- |
| POST   | `/addOrder`         | Create or update order      |
| GET    | `/getOrders`        | Retrieve all orders         |
| GET    | `/getRecentOrders`  | Retrieve latest orders      |
| GET    | `/getOrder/<id>`    | Retrieve order with details |
| DELETE | `/deleteOrder/<id>` | Delete order                |

### Calculations
| Method | Endpoint            | Description             |
| ------ | ------------------- | ----------------------- |
| POST   | `/api/calc/revenue` | Revenue simulation      |
| POST   | `/api/calc/spend`   | Monthly inventory spend |


## Testing Strategy

1. Unit Testing (White-box)

**Tool**: Pytest
**Scope**: DAO and service-layer logic
**Includes**:

* Control flow validation

* Data validation

* Boundary checks

* Error handling

* Code coverage
```bash
pytest tests/unittest --cov=backend
```

---

2. Black-box Test Design

The following techniques were used and documented:

* Equivalence Partitioning (EP)

* Boundary Value Analysis (BVA)

* Decision Tables

* State transitions (where applicable)

📄 See:
    * /pdf/black-box-test-design.pdf

--- 

3. Integration Testing

* API ↔ Database using Pytest

* API ↔ Client using Postman

* Automated execution using Newman
```bash
pytest tests/integration
newman run tests/integration/postman/GSM.postman_collection.json
```

---

4. End-to-End Testing (E2E)

**Tool**: Playwright + Pytest

Tested flows:

* Product creation

* Order creation

* Revenue simulation

* User-visible UI behavior
```bash
playwright install
pytest tests/e2e
```

---

## Static Analysis & Quality Tools

### Python

* Pylint for code quality

* pytest-cov for coverage

### Frontend

* ESLint for JavaScript analysis

### Code Quality Platform

* SonarCloud integrated into CI pipeline

* Tracks:

    * Code smells

    * Duplications

    * Coverage

    * Maintainability issues

---

## CI/CD Pipeline

**Tool**: GitHub Actions

* Automated steps:

1. Install dependencies

2. Run Pylint & ESLint

3. Run unit tests with coverage

4. Start backend & frontend

5. Run integration tests

6. Run E2E tests

7. Upload coverage to SonarCloud

Pipeline configuration:
```bash
.github/workflows/main.yml
```

---

## Academic Focus

This project emphasizes:

* Test design over feature complexity

* Clear traceability between requirements and tests

* Practical use of testing theory

* Automation and reproducibility

* All required deliverables for the exam are included as PDFs.

---

## Authors

Sofie Thorlund

Viktor Back


### Final Note

This project was developed explicitly for academic evaluation, with a strong focus on software testing methods, tooling, and documentation, rather than production deployment.