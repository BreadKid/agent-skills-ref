# Agent Skills Validation Tool

[![English](https://img.shields.io/badge/lang-English-blue.svg)](README.md) [![中文](https://img.shields.io/badge/lang-中文-red.svg)](README_ZH.md)

## Introduction

**Agent Skills Ref** is a local web tool based on the open-source [Agent Skills Ref](https://github.com/agentskills/agentskills/tree/main/skills-ref), designed to validate, parse, and generate Agent Skills definition files.

It localizes the official Skills Ref commands, providing API interfaces and a web-based visualization.

## Key Features

* **Validate Skill**: `skills-ref validate`
* **Extract Skill Properties**: `skills-ref read-properties`
* **Generate AI Agent Compatible XML**: `skills-ref to-prompt`

## Usage Instructions

### 1. Install Dependencies

Before starting the application, please install the project dependencies:

```bash
pip install -r requirements.txt
```

### 2. Start the Service

Run the following command in the project root directory to start the API server:

```bash
uvicorn main:app --host 0.0.0.0 --port 9900 --reload
```

The server will start at `http://0.0.0.0:9900`.

### 3. Access the Editor

Open your browser and visit the following address to use the visual editor:

```
http://localhost:9900
```

Alternatively, you can directly open the `page.html` file (ensure the API service is running in the background and listening on port 9900).

### 4. Core Interfaces

* `POST /validate/text`: Validate the legitimacy of Skill Markdown text content.
* `POST /properties/text`: Extract properties (e.g., name, description) from the text.
* `POST /prompt/text`: Convert Skill text into Agent XML Prompt format.

## Screenshots

### Initial Page

![init](images/init.png)

### Valid Skill

![200](images/200.png)

### Invalid Skill

![500](images/500.png)
