## ReAct prompting + tools

Use my python functions as tools to do very simple arithmetic operations.
This is inspired by the example from LlamaIndex:
https://docs.llamaindex.ai/en/stable/examples/agent/react_agent/


### Instrumentation

To observe LLM calls, I also do instrumentation here.
For LlamaIndex I use Langtrace, and you need to register and request an API key:
* https://www.langtrace.ai/
* https://docs.llamaindex.ai/en/stable/module_guides/observability/#langtrace