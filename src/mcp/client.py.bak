import asyncio
import json
from typing import Dict, Any
import subprocess
from pathlib import Path

class Client:
    """Client for communicating with MCP servers"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent.parent.parent / '.cline' / 'mcp_config.json'
        self.servers = {}
        self._load_config()
        
    def _load_config(self) -> None:
        """Load MCP server configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                self.servers = config.get('mcpServers', {})
        except Exception as e:
            print(f"Error loading MCP config: {e}")
            self.servers = {}
            
    async def use_tool(self, server_name: str, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Use a tool provided by an MCP server"""
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")
            
        server_config = self.servers[server_name]
        command = [server_config['command']] + server_config['args']
        env = {**server_config.get('env', {})}
        
        # Prepare request
        request = {
            'jsonrpc': '2.0',
            'method': tool_name,
            'params': args,
            'id': 1
        }
        
        # Start server process
        process = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        try:
            # Send request
            if process.stdin:
                request_str = json.dumps(request) + '\n'
                process.stdin.write(request_str.encode())
                await process.stdin.drain()
                
            # Read response
            if process.stdout:
                response_str = await process.stdout.readline()
                response = json.loads(response_str)
                
                if 'error' in response:
                    raise Exception(response['error'])
                    
                return response.get('result', {})
                
        finally:
            # Cleanup
            if process.stdin:
                process.stdin.close()
            await process.wait()
            
        raise Exception("Failed to get response from MCP server")
