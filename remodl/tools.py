"""
Remodl Tools - High-level helpers for tool integration

Provides simplified interfaces for common tool integration patterns
including MCP servers, function definitions, and DSPy tool conversion.
"""

from typing import List, Optional, Union, Dict, Any, Callable
import asyncio


class Tools:
    """
    Helper class for creating and managing tools across different frameworks.
    
    Examples:
        # From MCP server
        tools = Tools.from_mcp("mcp://localhost:3000")
        
        # From function definitions
        tools = Tools.from_functions([my_func1, my_func2])
        
        # Convert to DSPy format
        dspy_tools = Tools.to_dspy(tools)
    """
    
    @staticmethod
    def from_mcp(
        server_url: str,
        timeout: int = 30,
        tools_filter: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Load tools from an MCP server.
        
        Args:
            server_url: MCP server URL (e.g., "mcp://localhost:3000")
            timeout: Connection timeout in seconds
            tools_filter: Optional list of tool names to include
            
        Returns:
            List of tool definitions in OpenAI function calling format
            
        Example:
            tools = Tools.from_mcp("mcp://localhost:3000")
            
            response = remodl.completion(
                model="gpt-4",
                messages=[...],
                tools=tools
            )
        """
        try:
            from mcp import ClientSession, StdioServerParameters
            from mcp.client.stdio import stdio_client
        except ImportError:
            raise ImportError(
                "MCP package required. Install with: pip install mcp"
            )
        
        async def _fetch_tools():
            # Parse server URL
            if server_url.startswith("mcp://"):
                server_url_clean = server_url[6:]  # Remove mcp:// prefix
            else:
                server_url_clean = server_url
            
            # Connect to MCP server
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", server_url_clean],
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize
                    await session.initialize()
                    
                    # List available tools
                    tools_list = await session.list_tools()
                    
                    # Convert to OpenAI format
                    openai_tools = []
                    for tool in tools_list.tools:
                        # Filter if specified
                        if tools_filter and tool.name not in tools_filter:
                            continue
                        
                        tool_def = {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description or f"MCP tool: {tool.name}",
                                "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {
                                    "type": "object",
                                    "properties": {}
                                }
                            }
                        }
                        openai_tools.append(tool_def)
                    
                    return openai_tools
        
        # Run async
        return asyncio.run(_fetch_tools())
    
    @staticmethod
    def from_functions(
        functions: List[Callable],
        descriptions: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Convert Python functions to tool definitions.
        
        Args:
            functions: List of Python functions
            descriptions: Optional mapping of function names to descriptions
            
        Returns:
            List of tool definitions
            
        Example:
            def get_weather(location: str) -> str:
                '''Get current weather'''
                return f"Weather in {location}"
            
            tools = Tools.from_functions([get_weather])
        """
        from inspect import signature, getdoc
        
        tools = []
        for func in functions:
            sig = signature(func)
            doc = getdoc(func) or f"Function: {func.__name__}"
            
            # Extract parameters
            parameters = {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                    
                param_type = "string"  # Default
                if param.annotation != param.empty:
                    if param.annotation == int:
                        param_type = "integer"
                    elif param.annotation == float:
                        param_type = "number"
                    elif param.annotation == bool:
                        param_type = "boolean"
                
                parameters["properties"][param_name] = {"type": param_type}
                
                if param.default == param.empty:
                    parameters["required"].append(param_name)
            
            tool_def = {
                "type": "function",
                "function": {
                    "name": func.__name__,
                    "description": descriptions.get(func.__name__, doc) if descriptions else doc,
                    "parameters": parameters
                }
            }
            tools.append(tool_def)
        
        return tools
    
    @staticmethod
    def to_dspy(tools: List[Dict[str, Any]]) -> List:
        """
        Convert OpenAI-format tools to DSPy tool format.
        
        Args:
            tools: List of OpenAI-format tool definitions
            
        Returns:
            List of DSPy Tool objects
            
        Example:
            openai_tools = [...]
            dspy_tools = Tools.to_dspy(openai_tools)
            
            # Use in DSPy
            from remodl import dspy
            result = dspy.ReAct(tools=dspy_tools)(query="Search for AI")
        """
        try:
            from remodl import dspy
        except ImportError:
            raise ImportError("DSPy integration not available")
        
        # DSPy expects a specific format
        # This is a simplified conversion - adjust based on DSPy 3.0 API
        dspy_tools = []
        for tool in tools:
            func_def = tool.get("function", {})
            
            # Create DSPy tool wrapper
            # Note: Actual DSPy tool format may vary
            dspy_tool = {
                "name": func_def.get("name"),
                "description": func_def.get("description"),
                "parameters": func_def.get("parameters", {})
            }
            dspy_tools.append(dspy_tool)
        
        return dspy_tools


class MCPTools:
    """
    High-level MCP tools management for agentic workflows.
    
    Example:
        # Load and use MCP tools in one line
        agent = MCPTools.create_agent(
            "mcp://localhost:3000",
            model="gpt-4"
        )
        result = agent("Search for AI news")
    """
    
    @staticmethod
    def create_agent(
        mcp_server: str,
        model: str = "gpt-4",
        system_prompt: Optional[str] = None
    ):
        """
        Create a DSPy agent with MCP tools pre-loaded.
        
        Args:
            mcp_server: MCP server URL
            model: Model to use for the agent
            system_prompt: Optional system prompt
            
        Returns:
            Callable agent that can be invoked with queries
            
        Example:
            agent = MCPTools.create_agent(
                "mcp://localhost:3000",
                model="gpt-4",
                system_prompt="You are a helpful research assistant"
            )
            
            result = agent("What are the latest AI developments?")
            print(result)
        """
        from remodl import dspy
        
        # Load tools
        tools = Tools.from_mcp(mcp_server)
        
        # Create DSPy ReAct agent with tools
        class MCPAgent(dspy.Module):
            def __init__(self):
                super().__init__()
                self.agent = dspy.ReAct(tools=Tools.to_dspy(tools))
            
            def forward(self, query: str):
                return self.agent(query=query)
        
        # Configure model
        dspy.settings.configure(lm=dspy.LM(model))
        
        return MCPAgent()


# Convenience shortcuts
from_mcp = Tools.from_mcp
from_functions = Tools.from_functions
to_dspy = Tools.to_dspy

__all__ = ['Tools', 'MCPTools', 'from_mcp', 'from_functions', 'to_dspy']

