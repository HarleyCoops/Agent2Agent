![image info](images/A2A_banner.png)

**_An open protocol enabling communication and interoperability between opaque agentic applications._**

<!-- TOC -->

- [Agent2Agent Protocol A2A](#agent2agent-protocol-a2a)
    - [Getting Started](#getting-started)
    - [Contributing](#contributing)
    - [What's next](#whats-next)
    - [About](#about)

<!-- /TOC -->

One of the biggest challenges in enterprise AI adoption is getting agents built on different frameworks and vendors to work together. That’s why we created an open *Agent2Agent (A2A) protocol*, a collaborative way to help agents across different ecosystems communicate with each other. As the first hyperscaler to drive this initiative for the industry, we believe this protocol will be **critical to support multi-agent communication by giving your agents a common language – irrespective of the framework or vendor they are built on**. 
With *A2A*, agents can show each other their capabilities and negotiate how they will interact with users (via text, forms, or bidirectional audio/video) – all while working securely together.

### **Getting Started**

* 📚 Read the [technical documentation](https://google.github.io/A2A/#/documentation) to understand the capabilities
* 📝 Review the [json specification](/specification) of the protocol structures
* 🎬 Use our [samples](/samples) to see A2A in action
    * Sample A2A Client/Server ([Python](/samples/python/common), [JS](/samples/js/src))
    * [Multi-Agent Web App](/demo/README.md)
    * CLI ([Python](/samples/python/hosts/cli/README.md), [JS](/samples/js/README.md))
* 🤖 Use our [sample agents](/samples/python/agents/README.md) to see how to bring A2A to agent frameworks
    * [Google Agent Developer Kit (ADK)](/samples/python/agents/google_adk/README.md)
    * [CrewAI](/samples/python/agents/crewai/README.md)
    * [LangGraph](/samples/python/agents/langgraph/README.md)
    * [Genkit](/samples/js/src/agents/README.md)
* 📑 Review key topics to understand protocol details 
    * [A2A and MCP](https://google.github.io/A2A/#/topics/a2a_and_mcp.md)
    * [Agent Discovery](https://google.github.io/A2A/#/topics/agent_discovery.md)
    * [Enterprise Ready](https://google.github.io/A2A/#/topics/enterprise_ready.md)
    * [Push Notifications](https://google.github.io/A2A/#/topics/push_notifications.md) 

### **Contributing**

We welcome contributions! Please see our [contributing guide](CONTRIBUTING.md) to get started.\
Have questions? Join the discussion in our community forum\
Want to provide protocol improvement feedback [google form](https://docs.google.com/forms/d/e/1FAIpQLScS23OMSKnVFmYeqS2dP7dxY3eTyT7lmtGLUa8OJZfP4RTijQ/viewform)

### **What's next**

* Agent Discovery
  * Agent Card contains an authorization scheme and, optionally, credentials.
* Agent collaboration
  * Query unanticipated skill: Determine whether we should support a QuerySkill() method to interrogate whether an agent supports an ‘unanticipated’ skill.
* Agent UX re-negotiation within a Task
  * During a conversation, the agent dynamically adds audio or video.
* Extending support to client methods, along with improvements to streaming and push notifications.
* Include additional examples of agents

### **About**
A2A Protocol is an open source project run by Google LLC, under [License](LICENSE) and open to contributions from the entire community.      
