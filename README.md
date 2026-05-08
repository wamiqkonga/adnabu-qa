# AdNabu QA Assignment — Setup & Run Guide

**Store URL:** https://adnabu-store-assignment1.myshopify.com/  
**Store Password:** AdNabuQA  
**Automated Scenario:** Search for a product and add it to the cart  

---

## Project Structure

```
adnabu-qa/
├── tests/
│   └── test_search_and_add_to_cart.py   # Automated test
├── docs/
│   └── TEST_CASES.md                    # 6 manual test cases
├── requirements.txt                     # Python dependencies
└── README.md                            # This file
```

---

## Prerequisites

Make sure the following are installed on your machine before you begin:

- **Python 3.9+** — check with `python3 --version`
- **Google Chrome** — latest stable version
- **pip** — usually comes with Python

> ChromeDriver is handled automatically by `webdriver-manager`. You do not need to install it manually.

---

## Installation

**1. Clone the repository**

```bash
git clone https://github.com/wamiqkongwani/adnabu-qa.git
cd adnabu-qa
```

**2. Install dependencies**

```bash
pip3 install selenium webdriver-manager pytest pytest-html
```

Or using the requirements file:

```bash
pip3 install -r requirements.txt
```

---

## Running the Tests

Make sure you are inside the `adnabu-qa/` folder, then run:

```bash
pytest tests/ -v
```

A Chrome window will open automatically and execute the test. Do not interact with the browser while it runs.

**Expected terminal output on success:**

```
tests/test_search_and_add_to_cart.py::test_search_and_add_to_cart

  → Found product: 'The Complete Snowboard'
  → Cart count: 1

PASSED

1 passed in 11.2s
```

---

## Generating a Test Report

Run the following command to generate an HTML report:

```bash
pytest tests/ -v --html=test-report.html --self-contained-html
```

Then open it in your browser:

```bash
open test-report.html        # Mac
start test-report.html       # Windows
```

---

## Configuration

All configurable values are at the top of `tests/test_search_and_add_to_cart.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `STORE_URL` | `https://adnabu-store-assignment1.myshopify.com/` | Store base URL |
| `STORE_PASS` | `AdNabuQA` | Password to unlock the store |
| `SEARCH_TERM` | `snowboard` | Product name to search for |
| `TIMEOUT` | `10` | Max wait time in seconds for any element |

To run headless (no browser window), change line 18 in the test file:

```python
d = build_driver(headless=True)
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `zsh: command not found: pytest` | Run `pip3 install pytest` and use `python3 -m pytest tests/ -v` |
| `No search results found` | Visit the store manually, find a product that exists, and update `SEARCH_TERM` |
| `SessionNotCreatedException` | Chrome and ChromeDriver are out of sync — run `pip3 install -U webdriver-manager` |
| Chrome opens but test fails immediately | Increase `TIMEOUT` from 10 to 15 if your internet connection is slow |
| Asked for GitHub password in terminal | Use a Personal Access Token — generate one at github.com → Settings → Developer Settings → Tokens |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `selenium` | Browser automation |
| `webdriver-manager` | Auto-manages ChromeDriver version |
| `pytest` | Test runner |
| `pytest-html` | HTML report generation |
