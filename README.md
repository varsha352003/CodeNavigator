# CodeNavigator

AI-powered semantic code search using natural language queries. Search your codebase using questions like "error handling" or "database connection" instead of keywords.

## About

CodeNavigator is a semantic code search engine that understands the meaning and context of your code. Unlike traditional keyword-based search tools, it uses AI embeddings to find code based on what it does rather than what it's named.

The system analyzes your codebase at three levels:
- **Files**: Complete modules and their overall purpose
- **Classes**: Structural components and their relationships
- **Methods**: Individual functions and their implementations

This multi-level indexing allows you to search at any granularity - whether you're exploring architecture, finding design patterns, or locating specific implementations. Natural language queries like "validate user input" will find relevant code even if those exact words don't appear in the code.

## Features

- Natural language code search
- Searches files, classes, and methods
- Supports Python, C#, TypeScript, JavaScript, Java, C++
- AI-powered code parsing (GPT-4)
- Vector embeddings for semantic similarity
- Fast incremental indexing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Add OpenAI API key to `.env`:
```
OPENAI_API_KEY=your-key-here
```

## Usage

### Web Interface (Recommended)
```bash
streamlit run streamlit_app.py
```

### Command Line
```bash
python interactive_search.py
```

## How It Works

1. Indexes your project files
2. Extracts classes and methods using AI
3. Generates embeddings for semantic search
4. Searches using natural language queries
5. Returns relevant code with similarity scores

## Configuration

Edit `config/app_config.json`:
```json
{
  "vector_store_path": "./vectordb_workspace",
  "similarity_threshold": 0.25,
  "supported_extensions": [".py", ".cs", ".ts", ".js"]
}
```

## Architecture

```
src/code_search/
├── domain/          - Models and interfaces
├── application/     - Services (indexing, search)
├── infrastructure/  - AI, storage, parsing
└── presentation/    - CLI, web interfaces
```

## Requirements

- Python 3.11+
- OpenAI API key
- Dependencies in requirements.txt
