# Virtual TA 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/PythonicVarun/Virtual-TA)](https://github.com/PythonicVarun/Virtual-TA/issues)
[![GitHub forks](https://img.shields.io/github/forks/PythonicVarun/Virtual-TA)](https://github.com/PythonicVarun/Virtual-TA/network)
[![GitHub stars](https://img.shields.io/github/stars/PythonicVarun/Virtual-TA)](https://github.com/PythonicVarun/Virtual-TA/stargazers)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-v2.1-ff69b4.svg)](CODE_OF_CONDUCT.md)

**Last Updated:** 2025-05-31

## Overview

Virtual-TA is a Teaching Assistant Discourse responder designed for the IITM BS TDS (Tools in Data Science) course. This project aims to automate responses to common student queries and assist in managing course-related discussions.

**Project Status:** Active Development

## ✨ Features

*   **Automated Responses:** Provides quick answers to frequently asked questions.
*   **Discourse Integration:** Seamlessly works with discourse platforms.
*   **Course-Specific:** Tailored for the IITM BS TDS course curriculum and common queries.
*   **Extensible:** Designed to be easily updated with new Q&A pairs and functionalities.

## 🛠️ Tech Stack

*   **Language:** Python
*   **Deployment:** Docker (Dockerfile and docker-compose.yml provided)

## 📂 Project Structure

```
PythonicVarun/Virtual-TA/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
├── app/                  # Main application code
├── scripts/              # Utility and automation scripts
├── tests/                # Test suites
├── .env.example          # Example environment variables
├── .gitignore            # Specifies intentionally untracked files that Git should ignore
├── CODE_OF_CONDUCT.md    # Community guidelines
├── CONTRIBUTING.md       # Guidelines for contributors
├── Dockerfile            # Defines the Docker image
├── LICENSE               # Project license (MIT License)
├── README.md             # Project overview and instructions
├── docker-compose.yml    # Docker Compose configuration
└── requirements.txt      # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

*   Python 3.x
*   Docker (Optional, for containerized deployment)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/PythonicVarun/Virtual-TA.git
    cd Virtual-TA
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Rename `.env.example` to `.env` and fill in the necessary configuration details.
    ```bash
    cp .env.example .env
    # Open .env and update variables
    ```

### Running the Application

*   **Directly with Python:**
    ```bash
    # (Ensure your virtual environment is activated and .env is configured)
    # Runs at localhost:8000
    uvicorn app.main:app --reload
    ```

*   **With Docker:**
    1.  Build the Docker image:
        ```bash
        docker build -t virtual-ta .
        ```
    2.  Run using Docker Compose:
        ```bash
        docker-compose up
        ```
        Or run the image directly:
        ```bash
        docker run -d --env-file .env virtual-ta
        ```

## ⚙️ Scripts

This directory contains various utility and automation scripts for data preparation, processing, and automation:

### [`get_discourse_threads.py`](scripts/get_discourse_threads.py)
- **Purpose:** Downloads all Discourse threads in a specific category between two dates, including all posts in each thread (with pagination support). Supports authentication via API key or cookies.
- **Usage:**
    ```bash
    python scripts/get_discourse_threads.py \
      --base-url "https://discourse.onlinedegree.iitm.ac.in" \
      --category-path "courses/tds-kb/34" \
      --start-date "2025-01-01" \
      --end-date "2025-04-14" \
      --output-dir "data/raw_discourse_threads" \
      [--api-key KEY --api-username USER] \
      [--cookies "name=value; name2=value2"]
    ```

### [`jsonpost2text.py`](scripts/jsonpost2text.py)
- **Purpose:** Converts Discourse thread JSON files into plain-text Markdown summaries. Can process a single file or all JSON files in a directory.
- **Usage:**
    ```bash
    python scripts/jsonpost2text.py input_path [--output OUTPUT_DIR]
    # Example:
    python scripts/jsonpost2text.py thread.json
    python scripts/jsonpost2text.py data/raw_discourse_threads --output data/discourse_posts
    ```

### [`get_course_content.py`](scripts/get_course_content.py)
- **Purpose:** Downloads a GitHub repository (by branch or commit) as a ZIP, extracts it, and keeps only `.md` files, deleting everything else.
- **Usage:**
    ```bash
    python scripts/get_course_content.py [--branch BRANCH | --commit SHA] <repo_url> [--output OUTPUT_DIR]
    # Example:
    python scripts/get_course_content.py --branch tds-2025-01 --output data/course_content https://github.com/sanand0/tools-in-data-science-public
    ```

### [`create_vector_db.py`](scripts/create_vector_db.py)
- **Purpose:** Builds a FAISS vector database from text, Markdown, or HTML files (e.g., course content or discourse posts). Chunks and embeds text using OpenAI API, and saves the index and metadata for later retrieval.
- **Usage:**  
    Edit configuration variables if needed, then run:
    ```bash
    python scripts/create_vector_db.py
    ```
    By default, processes content in the `data/` directory and saves output to `model/`.

---

For more details about each script, see the script source files in the [`scripts/`](scripts) directory.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Code of Conduct

We have a [Code of Conduct](CODE_OF_CONDUCT.md) that we expect all contributors and community members to adhere to. Please read it to understand the expectations.

## 📧 Contact

PythonicVarun ([hello@pythonicvarun.me](mailto:hello@pythonicvarun.me))
