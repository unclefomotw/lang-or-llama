## RAG in multiple rounds of chat

Dialogue with memory. No external tools, and force RAG in every round.

This uses the strategy "condense + context":
1. History + the latest question ---LLM---> The standalone question
2. The standalone question ---Retriever---> Knowledge
3. Knowledge + history + the latest question ---LLM---> Final answer


The other setups are identical with `naive_rag` except that the prompts
are not customized.

This comparison focuses on the "default" solution they give,
together with their styles and the mindset/philosophy.
It does NOT push the limit of two frameworks on
* How good they can parse a PDF
* How good the index data structure is


### Run

```bash
### ETL (once)
# LangChain
$ PYTHONPATH=$(pwd) python src/chat_rag/la_etl.py
# LlamaIndex
$ PYTHONPATH=$(pwd) python src/chat_rag/ll_etl.py

### Inference
# LangChain
$ PYTHONPATH=$(pwd) python src/chat_rag/la_rag.py
# LlamaIndex
$ PYTHONPATH=$(pwd) python src/chat_rag/ll_rag.py
```