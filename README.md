# Anime ELO Rating Web App

A simple web application to rate your favorite anime using the ELO rating system.

## Features

- Import anime list in `.xml` format.
- Compare pairs of anime to update ELO ratings.
- Normalize ELO ratings to a 1-10 scale.
- Restart the process anytime.
- Containerized using Docker for easy setup.

## Requirements

- Docker installed on your system.

## Setup and Running

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/anime-elo-app.git
   cd anime-elo-app
---

## Explanation of Key Components

- **Flask Framework**: Used for building the web application.
- **Session Management**: Utilized to store the state between requests, such as the anime list and comparisons made.
- **ELO Rating System**: Implemented in `app/elo.py` to update the ratings based on user selections.
- **XML Parsing**: Handled by `app/parser.py` using Python's built-in `xml.etree.ElementTree` module.
- **Docker**: The `Dockerfile` is provided to containerize the application for easy deployment.

---

## How to Run the App

1. **Ensure Docker is installed** on your machine.

2. **Build the Docker Image**

   Open a terminal in the project directory and run:

   ```bash
   docker build -t anime-elo-app .