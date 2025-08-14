# ![JobPilot Icon](assets/JobPilotIcon-Alpha.png) JobPilot-OpenManus

**AI-Powered Job Hunting Copilot** - An intelligent agent framework that automates job discovery, analysis, and application processes using OpenManus architecture.

JobPilot-OpenManus combines the power of OpenManus's agent framework with specialized job hunting capabilities, providing a comprehensive solution for modern job seekers.

[![GitHub stars](https://img.shields.io/github/stars/alexretana/JobPilot-OpenManus?style=social)](https://github.com/alexretana/JobPilot-OpenManus/stargazers)
&ensp;
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
&ensp;
[![Based on OpenManus](https://img.shields.io/badge/Based%20on-OpenManus-blue)](https://github.com/FoundationAgents/OpenManus)

## 🚧 **Development Status**

| Component | Status | Description |
|-----------|---------|-------------|
| **🏗️ Core Foundation** | ✅ **Complete** | Data models, database layer, type safety |
| **💾 Data Management** | ✅ **Complete** | Job listings, user profiles, applications, companies |
| **🔍 Job Discovery** | ✅ **Complete** | Demo scraper, job extraction, market analysis |
| **🧠 Semantic Search** | ✅ **Complete** | AI-powered matching, embeddings, filtering |
| **🤖 Basic Agents** | ✅ **Complete** | Job discovery agent with market analysis |
| **🧪 Testing Suite** | ✅ **Complete** | Comprehensive tests for all core components |
| **🌐 Modern Web UI** | ✅ **Complete** | Real-time chat, activity tracking, responsive design |
| **🎯 AI Integration** | ✅ **Complete** | JobPilot prompts, transparent AI reasoning |
| **📅 Timeline System** | ✅ **Complete** | Job search activity tracking, milestones, events |
| **📊 Job Analytics** | ✅ **Complete** | Statistics, insights, progress tracking |
| **🔧 Full API Suite** | ✅ **Complete** | REST + WebSocket APIs, health monitoring |
| **📊 Real Job Boards** | ⏳ **Planned** | LinkedIn, Indeed, Glassdoor integration |
| **📝 Application Tools** | ⏳ **Planned** | Automated form filling and submission |
| **📈 Advanced Analytics** | ⏳ **Planned** | Predictive modeling, market trends |

**Current Status**: ✅ **Phase 1 Complete + Phase 2 Bonus Features** - Advanced system ready for production
**Next Phase**: 🔄 **Real Job Board Integration** - See [ROADMAP.md](ROADMAP.md) for details

## 🎯 Vision

JobPilot revolutionizes job hunting by automating tedious tasks while enhancing strategic decision-making. It acts as your personal AI job hunting assistant that works 24/7 to find, analyze, and help you apply to relevant opportunities.

## ✅ **Currently Implemented Features**

### 💾 **Complete Data Management System**
- **Job Listings**: Full CRUD operations with advanced search and filtering
- **User Profiles**: Professional information, skills, preferences, and job criteria
- **Applications**: Track application status, materials, and follow-ups
- **Companies**: Store and analyze company information and culture
- **Robust Database**: SQLAlchemy ORM with SQLite/PostgreSQL support

### 🔍 **AI-Powered Job Discovery**
- **Demo Job Generator**: Creates realistic job listings for testing (20+ tech companies, multiple roles)
- **Semantic Search**: AI understands job requirements beyond keywords using sentence transformers
- **Advanced Filtering**: Multi-factor scoring based on skills, experience, salary, location, remote work
- **Job Market Analysis**: Trend analysis, salary insights, top skills and companies
- **Company Search**: Find all jobs at specific companies

### 🤖 **Intelligent Agent System**
- **JobDiscoveryAgent**: Specialized agent for job hunting workflows
- **Market Analysis**: Automated job market trend reporting
- **Integration Ready**: Built on OpenManus agent framework for extensibility

### 🔧 **Developer-Friendly Architecture**
- **Type Safety**: Full Pydantic validation throughout
- **Repository Pattern**: Clean separation of data access logic
- **Comprehensive Testing**: All core components tested and validated
- **Extensible Design**: Easy to add new job boards, tools, and agents
- **Production Ready**: Proper error handling, logging, and session management

## 🏛️ Architecture

JobPilot-OpenManus is built on top of the robust OpenManus framework with job-specific enhancements:

```
JobPilot-OpenManus/
├── app/
│   ├── agent/
│   │   ├── job_discovery.py      # ✅ Job search and extraction agent
│   │   ├── manus.py              # ✅ Core OpenManus agent
│   │   ├── browser.py            # ✅ Browser automation agent
│   │   └── [other agents]        # ✅ Data analysis, SWE, etc.
│   ├── tool/
│   │   ├── job_scraper/          # ✅ Demo job generation tool
│   │   ├── semantic_search/      # ✅ AI-powered job matching
│   │   ├── browser_use_tool.py   # ✅ Browser automation
│   │   └── [standard tools]      # ✅ File ops, Python, search, etc.
│   ├── data/
│   │   ├── models.py             # ✅ JobListing, UserProfile models
│   │   └── database.py           # ✅ SQLAlchemy repository layer
│   ├── prompt/
│   │   └── jobpilot.py           # ✅ JobPilot-specific prompts
│   └── [OpenManus core]          # ✅ LLM, config, logging, etc.
├── frontend/
│   ├── src/
│   │   ├── components/           # ✅ Modern Solid.js UI components
│   │   ├── services/             # ✅ WebSocket and API services
│   │   └── [Solid.js app]        # ✅ Real-time chat interface
│   └── dist/                     # ✅ Built frontend assets
├── tests/
│   ├── test_core_components.py   # ✅ Core functionality tests
│   └── test_jobpilot_migration.py # ✅ Migration validation
├── web_server.py                 # ✅ FastAPI + WebSocket server
├── assets/                       # ✅ JobPilot icons and images
└── config/
    └── config.example.toml       # ✅ Configuration templates
```

## 🚐 Quick Start

### Prerequisites
- Python 3.12+
- Local LLM (Ollama recommended) or OpenAI/Claude API access

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/alexretana/JobPilot-OpenManus.git
cd JobPilot-OpenManus
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
# Or on Windows:
# venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
playwright install  # For browser automation
```

## Configuration

OpenManus requires configuration for the LLM APIs it uses. Follow these steps to set up your configuration:

1. Create a `config.toml` file in the `config` directory (you can copy from the example):

```bash
cp config/config.example.toml config/config.toml
```

2. Edit `config/config.toml` to add your API keys and customize settings:

```toml
# Global LLM configuration
[llm]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
max_tokens = 4096
temperature = 0.0

# Optional configuration for specific LLM models
[llm.vision]
model = "gpt-4o"
base_url = "https://api.openai.com/v1"
api_key = "sk-..."  # Replace with your actual API key
```

## Quick Start

One line for run OpenManus:

```bash
python main.py
```

Then input your idea via terminal!

For MCP tool version, you can run:
```bash
python run_mcp.py
```

For unstable multi-agent version, you also can run:

```bash
python run_flow.py
```

### Custom Adding Multiple Agents

Currently, besides the general OpenManus Agent, we have also integrated the DataAnalysis Agent, which is suitable for data analysis and data visualization tasks. You can add this agent to `run_flow` in `config.toml`.

```toml
# Optional configuration for run-flow
[runflow]
use_data_analysis_agent = true     # Disabled by default, change to true to activate
```
In addition, you need to install the relevant dependencies to ensure the agent runs properly: [Detailed Installation Guide](app/tool/chart_visualization/README.md##Installation)

## 🌐 Modern Web Interface

JobPilot-OpenManus features a modern, responsive web interface built with Solid.js, TailwindCSS, and DaisyUI for seamless interaction with the job hunting agent.

### Quick Start

**🚀 Easy Development Mode (Recommended)**

**Windows:**
```cmd
start.bat
```

**Linux/macOS:**
```bash
./start.sh
```

The startup scripts will:
- ✅ Validate all dependencies (Node.js, npm, Python)
- ✅ Install frontend dependencies if needed
- ✅ Build the frontend for production if not already built
- ✅ Start the backend server on port 8080
- ✅ Start the frontend dev server on port 3000
- ✅ Open both services in separate shells/windows

**Manual Setup:**

1. **Build the frontend** (first time only):
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

2. **Start the web server:**
   ```bash
   python web_server.py
   ```

3. **Open your browser** to `http://localhost:8080`

### Web Interface Features

- **🎨 Modern UI**: Built with Solid.js, TailwindCSS, and DaisyUI
- **🔄 Real-time Chat**: WebSocket-based communication with the AI agent
- **🌐 Live Browser Viewport**: Watch the agent browse job sites in real-time
- **📊 Activity Dashboard**: Track all agent actions, tool usage, and reasoning
- **📈 Progress Tracking**: Visual progress indicators for long-running searches
- **🎯 Quick Actions**: Pre-built queries for common job search tasks
- **🎭 29+ Themes**: Switch between light, dark, and specialty themes
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **🔍 Transparent AI**: Full visibility into the agent's decision-making process
- **⚡ Fast & Modern**: Vite-powered development with hot reload

### URLs

- **Frontend**: `http://localhost:3000` (development with hot reload)
- **Backend API**: `http://localhost:8080` (production build served here)
- **API Health Check**: `http://localhost:8080/api/health`

See [frontend/README.md](frontend/README.md) for detailed frontend documentation.

### Architecture

- **Backend**: FastAPI server with WebSocket support
- **Frontend**: Solid.js SPA with reactive state management
- **Styling**: TailwindCSS + DaisyUI component library
- **Build**: Vite for fast builds and development
- **Types**: Full TypeScript support throughout

## How to contribute

We welcome any friendly suggestions and helpful contributions! Just create issues or submit pull requests.

Or contact @mannaandpoem via 📧email: mannaandpoem@gmail.com

**Note**: Before submitting a pull request, please use the pre-commit tool to check your changes. Run `pre-commit run --all-files` to execute the checks.



## Acknowledgement

Thanks to [anthropic-computer-use](https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo)
and [browser-use](https://github.com/browser-use/browser-use) for providing basic support for this project!

Additionally, we are grateful to [AAAJ](https://github.com/metauto-ai/agent-as-a-judge), [MetaGPT](https://github.com/geekan/MetaGPT), [OpenHands](https://github.com/All-Hands-AI/OpenHands) and [SWE-agent](https://github.com/SWE-agent/SWE-agent).

We also thank stepfun(阶跃星辰) for supporting our Hugging Face demo space.

OpenManus is built by contributors from MetaGPT. Huge thanks to this agent community!

## Cite
```bibtex
@misc{openmanus2025,
  author = {Xinbin Liang and Jinyu Xiang and Zhaoyang Yu and Jiayi Zhang and Sirui Hong and Sheng Fan and Xiao Tang},
  title = {OpenManus: An open-source framework for building general AI agents},
  year = {2025},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.15186407},
  url = {https://doi.org/10.5281/zenodo.15186407},
}
```
