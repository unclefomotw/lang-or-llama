# lang-or-llama
Write the same use case in two different frameworks: LangChain and LlamaIndex


## Pre-requisite

Prepare OpenAI API key
```bash
export OPENAI_API_KEY="sk-......"
```


## Data

`./get_data.sh` to download files to retrieve into `data/`


## Use Case
For details, see the README.md of each use case respectively

1. src/naive_rag - Basic RAG with some non-framework-default settings
2. src/chat_rag - RAG with multiple rounds of chat