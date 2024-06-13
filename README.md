# lang-or-llama
Write the same use case in two different frameworks: LangChain and LlamaIndex


## Pre-requisite

Prepare OpenAI API key
```bash
export OPENAI_API_KEY="sk-......"
```

In some cases, instrumentation keys are required.  See README.md under each case


## Data

`./get_data.sh` to download files to retrieve into `data/`


## Use Case
For details, see the README.md of each use case respectively

1. src/naive_rag - Basic RAG with some non-framework-default settings
2. src/chat_rag - RAG with multiple rounds of chat
3. src/simple_react - ReAct prompting + tools
4. src/leetcode_agent - LeetCode solver via LangChain / LangGraph agent
5. src/super_step - Some confusing examples for LangGraph fan-out and fan-in branching
6. src/hitl - Some commonn examples of Human-in-the-Loop
