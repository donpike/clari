from typing import Dict, Any, Optional

class Tool:
    """Base class for MCP tools"""
    name: str = ""
    description: str = ""
    
    def __init__(self):
        self.mcp = None  # Will be set by server
        
    def set_mcp(self, mcp: Any) -> None:
        """Set the MCP server instance"""
        self.mcp = mcp
        
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool request"""
        raise NotImplementedError("Tool must implement handle_request")
        
    def get_tool(self, name: str) -> Optional['Tool']:
        """Get another tool by name"""
        if self.mcp:
            return self.mcp.get_tool(name)
        return None
