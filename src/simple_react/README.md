## ReAct prompting + tools

Use my python functions as tools to do very simple arithmetic operations.
This is inspired by the example from LlamaIndex:
https://docs.llamaindex.ai/en/stable/examples/agent/react_agent/


### Files
Basic comparison
* ll_agent.py - ReAct on LlamaIndex; use prompt engineering rather than "tool use" from LLM
* ll_agent_with_tool_llm.py - ReAct on LlamaIndex; achieved via OpenAI GPT model's "tool use"
* la_agent_with_tool_llm.py - ReAct on LangChain/LangGraph; achieved via "tool use" (not necessarily OpenAI's)

Real (?) ReAct implementation
* ll_agent_with_custom_prompt.py - Few-shot learning similar to the original paper (in LlamaIndex)

As a "workflow" engine
* llamaindex_try.py - Toy example of building a workflow in LlamaIndex
* langgraph_try.py - Toy example of building a workflow in LangGraph

Just some dumb use case
* story_teller.py - A more interesting example using LangChain's ReAct agent


### Instrumentation

To observe LLM calls, I also do instrumentation here.
For LlamaIndex I use Langtrace, and you need to register and request an API key:
* https://www.langtrace.ai/
* https://docs.llamaindex.ai/en/stable/module_guides/observability/#langtrace

```bash
$ export LANGTRACE_API_KEY="xxxxxxxx"
```

For LangChain I use their ecosystem LangSmith
* https://docs.smith.langchain.com/
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY="xxxxxxxxxx"
```


### How do they handle "workflow"?
* LangGraph treat the flow as a (Pregel-like) graph.  The "edge" determines what to do next.
* LlamaIndex treat the flow as a TODO queue.  The worker itself determines what to do next.

It's better to be armed with different mindsets.  For example if you force a diamond-shape graph thinking
(which is natural in LangGraph) into LlamaIndex, it's not elegant to know when to finish the steps.
See llamaindex_try.py and langgraph_try.py for details.

Also IMO in LlamaIndex, the BaseAgentRunner is too basic (no implementation at all on basic
operations of steps and task), and AgentRunner makes a more restrictive assumption (e.g. only
one single LLM).  Having said that, maybe in real world applications it's not that complex.
"It just works"