<div align="center">
  <img src="fasty.svg" alt="Fasty Logo" width="450">
  
 <p>
  <strong>Fasty is a dynamic REST API server that instantly turns a YAML configuration file into fully-featured mock API endpoints, complete with routes, pagination, HATEOAS links, and rich <code>faker</code> data for rapid frontend prototyping.</strong>
</p>
  
<p>
    <a href="https://github.com/dandyArise/fasty"><img src="https://img.shields.io/badge/App-Fasty-4285F4?style=for-the-badge" alt="App Name Badge"/></a>
    <a href="https://github.com/dandyArise/fasty/stargazers"><img src="https://img.shields.io/github/stars/dandyArise/fasty?style=for-the-badge&color=ffd166" alt="Stars Badge"/></a>
    <a href="https://github.com/dandyArise/fasty/network/members"><img src="https://img.shields.io/github/forks/dandyArise/fasty?style=for-the-badge&color=06d6a0" alt="Forks Badge"/></a>
    <a href="https://github.com/dandyArise/fasty/issues"><img src="https://img.shields.io/github/issues/dandyArise/fasty?style=for-the-badge&color=ef476f" alt="Issues Badge"/></a>
    <a href="https://github.com/dandyArise/fasty/blob/main/LICENSE.md"><img src="https://img.shields.io/badge/License-BSL%201.1-118ab2?style=for-the-badge" alt="License Badge"/></a>
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge"/>
    <img src="https://img.shields.io/badge/FastAPI-0.68+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI Badge"/>
    <img src="https://img.shields.io/badge/Docker-Supported-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker Badge"/>
</p>
</div>

## 🌟 Overview

**Fasty** is a dynamic REST API server. It aims to solve the problem of rapidly generating mock, fully-featured API endpoints for frontend prototyping or testing by taking a single YAML configuration file and instantly binding HTTP routes, pagination, HATEOAS links, and injecting rich `faker` generated data.

It uses `watchdog` to monitor changes in your YAML file and seamlessly updates the application's routes and data without ever requiring a server restart.

## ✨ Features

- 🚀 **Dynamic Endpoint Generation** - Endpoints are created instantly based on the models defined in the YAML file.
- ⚡ **Real-Time Hot-Reloading** - Automatic atom-swap reloading of data and dynamic route mounting when the YAML file is modified.
- 🎭 **Data Generation** - Leverages `faker` underneath to generate thousands of realistic mock data records directly from YAML schemas.
- 📄 **Pagination & HATEOAS** - Add standards-compliant pagination headers and HATEOAS references instantly with a single boolean flag.
- 🐳 **Docker Ready** - Fully containerized with an included `docker-compose.yml`, supporting both HTTP and HTTPS out of the box.

## 🎯 Quick Start

### Prerequisites

- Python 3.7+
- Docker & Docker Compose (optional, for the containerized version)

### Installation (Local)

1. **Clone the repository**
   ```bash
   git clone https://github.com/dandyArise/fasty.git
   cd fasty
   ```

2. **Create a virtual environment** (optional but recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Installation (Docker)

1. **Build and spin up the containers**
   ```bash
   docker-compose up --build -d
   ```

## 🛠️ Configuration

Create a file named `fasty.yml` in the root directory. This YAML file defines the schemas, amount of fake data, and any hardcoded data objects you need to inject.

```yaml
locale: "en_US"
models:
  users: # Automatically mounts endpoints at /users and /users/{id}
    pagination: true
    hateoas: true
    fake: # faker generator patterns mapping
      _count: 10
      first_name: first_name
      last_name: last_name
      email: email
    data: # manually injected hardcoded data
      - id: 100
        first_name: John
        last_name: Doe
        email: john.doe@example.com
        
  posts:
    fake:
      _count: 5
      title: sentence
      body: text
```

### Configuration Fields
- **`pagination: true/false`**: Enables chunked lists.
- **`hateoas: true/false`**: Enables `_links` injection referencing the collection and self endpoints.
- **`_count`**: Number of randomized records to generate on startup.
- **`faker_*`**: Map any column name to its respective `faker` method (e.g., `first_name`, `email`, `sentence`, `text`).

## 🚀 Running the Application

### Local

You can run the application either in standard HTTP mode or in secure HTTPS mode.

**HTTP Mode:**
```bash
python -m fasty.main --port 8000
```

**HTTPS Mode (Auto-generates self-signed certificates):**
```bash
python -m fasty.main --https --port 8443
```

### Accessing the Interface

- **Interactive API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- *(Note: Changing `fasty.yml` will not break the documentation page! Keep hitting save and refreshing Swagger)*

## 📡 API Endpoints

The application dynamically generates the following endpoints based on the models defined in `fasty.yml`:

- **`GET /api/users`** : Retrieve a paginated collection of users.
- **`GET /api/users/{item_id}`** : Retrieve a specific user record by its ID.
- **`GET /api/posts`** : Retrieve a collection of posts.
- **`GET /api/posts/{item_id}`** : Retrieve a specific post record by its ID.
- **`GET /health`** : Simple health check endpoint to verify server status.

## 🏗️ Project Structure

```text
fasty/                  # Root project directory
├── fasty/              # Main package
│   ├── api/            # API endpoints & routing
│   ├── core/           # Core logic (config, store, exceptions)
│   ├── utils/          # Utility functions (YAML loader)
│   └── main.py         # App entrypoint & server bootstrap
├── certs/              # Auto-generated HTTPS certificates
├── fasty.yml           # Global data modeling & configuration
├── requirements.txt    # Python dependencies
├── docker-compose.yml  # Docker services
├── Dockerfile          # Container build instructions
├── README.md           # Documentation
├── LICENSE.md          # Business Source License 1.1
├── CHANGE_DATE.md      # Date of transition to Apache 2.0
├── NOTICE.md           # Attribution & Contacts
└── COMMERCIAL_LICENSE.md # Commercial License instructions
```

## 🤝 Contributing

We love your input! We want to make contributing to **Fasty** as easy and transparent as possible. 

### Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests

## 📄 License

This project is licensed under a modified **Business Source License 1.1 (BSL 1.1)**. 

- **Free for Personal/Non-Profit Use**: You may use Fasty freely for personal use, internal research, or educational purposes.
- **Commercial Use Restricted**: Commercial use (such as production SaaS, hosting, or offering as a service) is **prohibited** without a separate Commercial License until the Change Date.
- **Change Date**: On **2031-01-01** (see `CHANGE_DATE.md`), the license automatically converts to the **Apache License 2.0**.

For commercial use inquiries, please refer to `COMMERCIAL_LICENSE.md` and `NOTICE.md` or contact the author.

## 🙏 Acknowledgments

- Highly inspired by the `json-server` ecosystem
- Built gracefully upon [FastAPI](https://fastapi.tiangolo.com/) and [Faker](https://faker.readthedocs.io/)

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/dandyArise">@dandy</a>
</div>
