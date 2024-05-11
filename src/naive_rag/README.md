## Naive RAG

One simple round of QA (i.e. no conversation memory); no external tools

* Data: single pdf file
* Basic indexing: customized size + overlap
* Simple top-k embedding retrieval
* Qdrant vector DB
* Customized embedding (using HuggingFace)
* Customized LLM (OpenAI API - GPT 3.5 with small temperature)
* Customized prompt

This comparison focuses on their styles and the mindset/philosophy.
It does NOT push the limit of two frameworks on
* How good they can parse a PDF
* How good the index data structure is

`constants.py` contains common things that the both frameworks can leverage

### Run

```bash
### ETL (once)
# LangChain
$ PYTHONPATH=$(pwd) python src/naive_rag/la_etl.py 
# LlamaIndex
$ PYTHONPATH=$(pwd) python src/naive_rag/ll_etl.py

### Inference
# LangChain
$ PYTHONPATH=$(pwd) python src/naive_rag/la_rag.py 
# LlamaIndex
$ PYTHONPATH=$(pwd) python src/naive_rag/ll_rag.py
```