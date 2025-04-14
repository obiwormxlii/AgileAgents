# Architecture Overview

## 1. Overall Architecture

The system is composed of multiple microservices, each responsible for a specific task (e.g., user story generation, design document generation, API documentation generation, problem decomposition).

A central API gateway routes requests to the appropriate microservice.

A message queue (e.g., RabbitMQ) facilitates asynchronous communication between microservices.

A metadata store (e.g., Neo4j) holds relationships between different documents and tasks.

## 2. Key Components

*   **User Interface (UI):** A SvelteKit-based web application for user interaction.
*   **API Gateway:** An Nginx or Traefik reverse proxy that routes requests to the appropriate microservice.
*   **Microservices:**
    *   **User Story Generator Service:** Uses Transformers to generate high-level user stories from project descriptions.
    *   **User Story Decomposition Service:** Uses Transformers to break down high-level user stories into smaller, actionable stories.
    *   **Requirements Specification Service:** Generates detailed requirement specifications from user stories, leveraging templates and NLP techniques.
    *   **Design Document Service:** Creates design documents based on requirements and architectural decisions, using templates and diagrams as code.
    *   **API Documentation Service:** Extracts API documentation from code and generates OpenAPI/Swagger specifications.
    *   **Problem Decomposition Service:** Breaks down complex software design problems into smaller, manageable tasks.
*   **Message Queue (RabbitMQ):** Facilitates asynchronous communication between services.
*   **Metadata Store (Neo4j):** Stores metadata about the project, requirements, designs, code, and tasks to maintain traceability.
*   **Data Storage (PostgreSQL):** Stores structured data related to projects, user stories, and requirements.

## 3. Technology Stack

*   **Programming Language:** Python
*   **Frameworks:**
    *   FastAPI
    *   Celery
*   **Message Queue:** RabbitMQ
*   **Databases:**
    *   PostgreSQL
    *   Neo4j
*   **AI/ML Libraries:**
    *   Transformers (Hugging Face)
	*   Langchain
*   **Deployment:** Docker containers orchestrated by Kubernetes.