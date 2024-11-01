<h1 align="center">Development</h1>

<p align="center">
    Welcome to the <strong>Earth Defenders Assistant</strong> development documentation. This guide provides essential information for developers contributing to our platform, which leverages <a href="https://wwebjs.dev/">whatsapp-web.js</a> for creating customizable WhatsApp bots. Our system employs a flexible plugin architecture to support a wide range of applications, enabling the deployment of personalized bots tailored to diverse community needs.
    <br />
    <br />
    <a href="#getting-started"><strong>Getting Started</strong></a> ·
    <a href="#architecture"><strong>Architecture</strong></a> ·
    <a href="#contributing"><strong>Contributing</strong></a> ·
    <a href="#deployment"><strong>Deployment</strong></a>
</p>

## Getting Started

This project uses [Turborepo](https://turbo.build/repo/docs) as a monorepo architecture to manage multiple packages and applications. The codebase is split between TypeScript (for core processing, database interactions, and frontend applications) and Python (for AI/ML services and natural language processing).
### Prerequisites

- **Node.js** (v20 or later)
- **[Bun](https://bun.sh/)** (v1.1.33) - NodeJS manager
- **Python** (v3.11)
- **[uv](https://docs.astral.sh/uv/)** - Python manager
- **Git**
- **Docker** (optional, for containerized deployment)

**Installing**

Make sure you have the necessary dependencies. The following commands will install the required development tools:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash # install Node Version Manager
curl -fsSL https://bun.sh/install | bash # Install Bun NodeJS package manager and runtime
curl -LsSf https://astral.sh/uv/install.sh | sh # Install uv Python package manager
```

Install Node.js v20 and pin it using nvm:

```
nvm install 20
nvm use 20
nvm alias default 20
```

And Python 3.11 and pin it using uv:
```
uv python install 3.11
uv python pin 3.11
```

### External Services

The platform's core services can be run either locally or accessed via cloud providers during development. While local setup instructions are available in the deployment section, running all services locally can be resource-intensive. Each service provider offers a free tier that you can use by creating an account, making cloud-based development a viable alternative for resource-constrained environments.

| Service                             | Purpose                                | Required   |
| ----------------------------------- | -------------------------------------- | ---------- |
| [Supabase](https://supabase.com/)   | Backend-as-a-Service (BaaS) platform   | Yes        |
| [Trigger.dev](https://trigger.dev/) | Workflow automation and job scheduling | Yes        |
| [Langtrace](https://langtrace.ai/)  | LLM observability and monitoring       | For AI Dev |

### Optional Monitoring Services

| Service                             | Purpose                                   |
| ----------------------------------- | ----------------------------------------- |
| [OpenPanel](https://openpanel.dev/) | Analytics and data visualization          |
| [Upstash](https://upstash.com/)     | Redis-compatible database and caching     |
| [Sentry](https://sentry.io/)        | Error tracking and performance monitoring |

### Installation

Clone this repo locally with the following command:

```bash
git clone https://github.com/digidem/earth-defender-assistant.git
cd earth-defenders-assistant
```

1. Install dependencies using bun:

```sh
bun i
```

2. Copy `.env.example` to `.env` and update the variables.

```sh
# Copy .env.example to .env for each app
cp packages/simulator/.env.example packages/simulator/.env
cp packages/jobs/.env.example packages/jobs/.env
cp apps/api/.env.example apps/api/.env
cp apps/ai_api/.env.example apps/ai_api/.env
cp apps/dashboard/.env.example apps/dashboard/.env
cp apps/landingpage/.env.example apps/landingpage/.env
cp apps/whatsapp/.env.example apps/whatsapp/.env
cp deploy/trigger-stack/.env.example deploy/trigger-stack/.env
cp deploy/langtrace-stack/.env.example deploy/langtrace-stack/.env
```

3. Before starting the development server, ensure you have the required environmental variables in place:

- Connect to Trigger instance by setting the correct `TRIGGER_PROJECT_ID` and `TRIGGER_API_URL` variables in the `packages/jobs/.env` file from [Local Trigger](http://localhost:3040/) or [Cloud Trigger](https://cloud.trigger.dev)
- Add the correct `TRIGGER_SECRET_KEY` to `apps/whatsapp/.env` and `packages/simulator/.env` from [Local Trigger](http://localhost:3040/) or [Cloud Trigger](https://cloud.trigger.dev) ([docs](https://trigger.dev/docs/apikeys))
- Add the correct `SUPABASE_SERVICE_ROLE_KEY` to the `packages/jobs/.env` from [Local Supabase](http://localhost:54323/project/default/settings/api) or [Cloud Supabase](https://supabase.com/dashboard/)
- Add valid `CEREBRAS_API_KEY` or `OPENAI_API_KEY` to `apps/ai_api/.env` from [Cerebras](https://cloud.cerebras.ai/platform) or [OpenAI](https://platform.openai.com/api-keys)
- (optional) Add the correct `LANGTRACE_API_KEY` to the `.env` in `apps/ai_api/.env` and `packages/simulator/.env`
- Add a valid `GROQ_API_KEY` to `packages/simulator/.env` from [Groq Console](https://console.groq.com/keys)
- Add the correct `SERPER_API_KEY` to the `apps/ai_api/.env`

4. Finally start the development server from either bun or turbo:

```ts
// Basic development
bun prepare:db // prepares database and pre-commit hooks
bun dev // starts simulator, Supabase api and Trigger.dev jobs
// Other available commands
bun dev:all // starts all services in development mode
bun dev:simulator // starts a user simulation using a LLM
bun dev:api // starts the Supabase API service in development mode
bun dev:jobs // starts the Trigger.dev service in development mode
bun dev:ai // starts the AI API service in development mode (uses Python uv)
bun dev:whatsapp // starts the WhatsApp service in development mode
bun dev:dashboard // starts the dashboard in development mode
bun dev:landingpage // starts the landing page in development mode
bun dev:email // starts the email service in development mode
bun dev:docs // starts the documentation service in development mode
bun deploy:trigger // deploys local Trigger.dev instance using Docker
bun deploy:langtrace // deploys local LangTrace instance using Docker
// Database
bun migrate // run Supabase migrations
bun seed // run Supabase seed
```

5. Running `bun dev` starts three key development services in parallel:

- The simulator (@eda/simulator) which simulates a community member interacting with the system
- The API service (@eda/api) which handles core backend functionality using Supabase (will run a local Supabase instance using Docker)
- The jobs service (@eda/jobs) which processes background tasks using Trigger.dev
- The AI API service (@eda/ai-api) which handles AI-related functionality exposing plugins through a [FastAPI](https://fastapi.tiangolo.com/) server.

**Access the Applications:**

- **Dashboard**: Visit [http://localhost:8080](http://localhost:8080) to access the main dashboard interface.
- **Landing Page**: Visit [http://localhost:8081](http://localhost:8081) to view the landing page.
- **Documentation**: Visit [http://localhost:8082](http://localhost:8082) to browse the documentation.
- **AI API**: Visit [http://localhost:8083/docs](http://localhost:8083/docs) to access the API documentation.
- **Supabase Studio**: Visit [http://localhost:54323](http://localhost:54323) to manage your database, view API documentation, and perform backend tasks.
- **Trigger.dev Dashboard**: Visit [http://localhost:3040](http://localhost:3040) to manage jobs. Use `docker logs -f trigger-webapp` to view the magic link in the logs.

Development should be done primarily through the simulator, which creates realistic scenarios of community members interacting with the system. The simulator enables testing conversations between two AI agents - one representing a community member and another representing the assistant.

If using a local Trigger.dev instance for job processing, first run `bun deploy:trigger` before `bun dev`. For local LangTrace observability, deploy with `bun deploy:langtrace`.

## Architecture

This project follows a modular architecture, organized as a Turborepo monorepo. Key components include:

- **Apps:** Front-end applications such as the landingpage, user dashboard and WhatsApp web interface.
- **Packages:** Shared libraries and utilities used across applications, including analytics, email templates, background jobs, key-value storage, logging, simulation tools, database clients, TypeScript types, and UI components.
- **Plugins:** Extensible AI service modules and plugins that can be integrated into the core applications, currently including grant analysis and evaluation tools with potential for additional domain-specific plugins.
- **Deploy:** Utilize Docker Compose and scripts for deploying services used by the applications.

### Tech Stack

[Turborepo](https://turbo.build) - Build system<br>
[Biome](https://biomejs.dev) - Linter, formatter<br>
[Supabase](https://supabase.com/) - Authentication, database, storage<br>
[Trigger.dev](https://trigger.dev/) - Background jobs<br>
[FastAPI](https://fastapi.tiangolo.com/) - Python web framework<br>
[Langtrace](https://www.langtrace.ai/) - LLM monitoring and evaluation<br>
[Starlight](https://starlight.astro.build/) - Documentation<br>
[Upstash](https://upstash.com/) - Cache and rate limiting<br>
[React Email](https://react.email/) - Email templates<br>
[Sentry](https://sentry.io/) - Error handling/monitoring<br>
[OpenPanel](https://openpanel.dev/) - Analytics<br>

### Directory Structure

```
.
├── apps                         # App workspace
│    ├── ai_api                  # Python FastAPI for exposing and calling AI plugins
│    ├── api                     # Supabase (API, Auth, Storage, Realtime, Edge Functions)
│    ├── dashboard               # User dashboard
│    ├── landingpage             # Product Landing Page
│    ├── whatsapp                # Whatsapp Web instance
│    └── docs                    # Product Documentation
├── packages                     # Shared packages between apps
│    ├── analytics               # OpenPanel analytics
│    ├── email                   # React email library
│    ├── jobs                    # Trigger.dev background jobs
│    ├── kv                      # Upstash rate-limited key-value storage
│    ├── logger                  # Logger library
│    ├── simulator               # Simulates scrapping and user interactions
│    ├── supabase                # Supabase - Queries, Mutations, Clients
│    ├── types                   # Shared TypeScript type definitions
│    ├── typescript-config       # Shared TypeScript configuration
│    └── ui                      # Shared UI components (Shadcn)
├── deploy                       # Deploy workspace
│    ├── langtrace               # Langtrace stack
│    ├── briefer-stack           # Briefer stack components
│    ├── supabase-stack          # Supabase (API, Auth, Storage, Realtime, Edge Functions)
│    ├── training-stack          # LLM-training framework stack
│    ├── trigger-stack           # Trigger.dev stack components
│    └── zep-stack               # Zep stack components
├── plugins                      # Plugin workspace
│    └── grant_plugin            # The AI grant plugin for EDA
├── tooling                      # Shared configuration that are used by the apps and packages
│    └── typescript              # Shared TypeScript configuration
├── .cursorrules                 # Cursor rules specific to this project
├── biome.json                   # Biome configuration
├── turbo.json                   # Turbo configuration
├── LICENSE
└── README.md
```

### Project Diagram

```mermaid
    flowchart TD

    %% Define styles for different components
    classDef userStyle fill:#A0C4FF,stroke:#003F5C,stroke-width:1.5px,color:#000
    classDef externalStyle fill:#BDB2FF,stroke:#6A4C93,stroke-width:1.5px,color:#000
    classDef botStyle fill:#C9F0FF,stroke:#69C0FF,stroke-width:1.5px,color:#000
    classDef processStyle fill:#FFC6FF,stroke:#9D4EDD,stroke-width:1.5px,color:#000
    classDef databaseStyle fill:#FFFFB5,stroke:#FFCA3A,stroke-width:1.5px,color:#000
    classDef serviceStyle fill:#B9FBC0,stroke:#43AA8B,stroke-width:1.5px,color:#000
    classDef llmStyle fill:#FFD6A5,stroke:#F9844A,stroke-width:1.5px,color:#000
    classDef externalAppStyle fill:#FFADAD,stroke:#D00000,stroke-width:1.5px,color:#000

    %% User Interaction
    subgraph UserInteraction["User Interaction"]
        direction LR
        User["User"]:::userStyle
        WhatsApp["WhatsApp"]:::externalStyle
        Bot["Earth Defenders Assistant"]:::botStyle
    end

    %% Orchestration & Processing
    subgraph Orchestration["Orchestration & Processing"]
        direction TB
        MessageProcessor["Message Processor"]:::processStyle
        TriggerDev["Trigger.dev<br>(Events Monitoring)"]:::externalAppStyle

        subgraph Supabase["Supabase DB"]
            direction TB
            receivedMessages["receivedMessages"]:::databaseStyle
            toSendMessages["toSendMessages"]:::databaseStyle
            MemoryDB["Graph Memory<br>(Supabase DB)"]:::databaseStyle
        end
    end

    %% Memory Management
    subgraph MemoryLayer["Long Term Memory"]
        direction TB
        Zep["Zep"]:::externalAppStyle
    end

    %% LLMTraining
    subgraph LLMTraining["Training and Fine-Tuning"]
        direction TB
        LLM-training["LLM-training"]:::externalAppStyle
    end


    %% Plugins
    subgraph LLMProcessing["Plugins"]
        direction TB
        Plugins["Plugins<br>(Intent Classification,<br>Tool Calling)"]:::processStyle
        LLMOperations["LLM Operations"]:::llmStyle
        Tools["Tools"]:::serviceStyle
        Briefer["Briefer<br>(Human Readable DB)"]:::externalAppStyle
        ExternalTools["External Tools"]:::serviceStyle
        Langtrace["Langtrace<br>(Monitoring and Evaluation)"]:::externalAppStyle
    end

    %% Connections
    User -->|Communicates| WhatsApp
    WhatsApp -->|Routes| Bot
    Bot -->|Orchestrates| TriggerDev
    TriggerDev -->|Adds Messages to| receivedMessages
    receivedMessages -->|Read by| MessageProcessor
    MessageProcessor -->|Processes| Plugins
    Plugins -->|Call| LLMOperations
    Plugins -->|Call| Tools
    LLMOperations -->|Call| Tools
    LLMOperations -->|Feedback to| Langtrace
    MessageProcessor -->|Memory Update| Zep
    Zep <-->|Stores and Retrieves| MemoryDB
    Zep -->|Add to prompt|LLMOperations
    LLM-training -->|Inference|LLMOperations
    Tools -->|Call|Briefer
    Tools <-->|Call|ExternalTools
    Tools -->|Queue message|toSendMessages
    Briefer -->|Feed data|LLM-training
    Langtrace -->|Feed data| LLM-training
    Bot -->|Responds| WhatsApp
    WhatsApp -->|Delivers| User
```

## Contributing

We welcome contributions from the community. To get started:

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature/your-feature-name`).
3. Commit your changes (`git commit -m 'Add your feature message'`).
4. Push to the branch (`git push origin feature/your-feature-name`).
5. Open a [Pull Request](https://github.com/digidem/earth-defenders-assistant/pulls).

Please adhere to the project's [Code of Conduct](./CODE_OF_CONDUCT.md) and ensure all tests pass before submitting your pull request.

## Deployment

For detailed deployment instructions, please refer to our comprehensive [Deployment Guide](./deploy/README.md). This guide provides step-by-step instructions for setting up and deploying each component of our stack.
