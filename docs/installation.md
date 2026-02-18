# Installation Guide

## Prerequisites

Before installing Imperium Flow, ensure you have the following:

- **Python 3.8+**: The system is built on Python.
- **Docker & Docker Compose**: Required for running the Conductor server backend.
- **Git**: For version control.

## Step-by-Step Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/nacerdz20/Imperium-Flow.git
    cd Imperium-Flow
    ```

2.  **Set up Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # On Windows: venv\Scripts\activate
    ```

3.  **Install Requirements**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start Backend Services (Conductor)**
    ```bash
    docker-compose up -d
    ```
    *This starts the Netflix Conductor server and UI.*

5.  **Verify Installation**
    Check if Conductor UI is running at `http://localhost:5000`.

## Next Steps

- Proceed to [Configuration](configuration.md) to set up your environment keys.
- Run the [Dashboard](deployment.md) to visualize the system.
