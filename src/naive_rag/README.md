## Naive RAG

One simple round of QA (i.e. no conversation memory); no external tools

* Data: single pdf file
* Basic indexing: customized size + overlap
* Simple top-k embedding retrieval
* Qdrant vector DB
* Customized embedding (using HuggingFace)
* Customized LLM (OpenAI API - GPT 3.5 with small temperature)
* Customized prompt