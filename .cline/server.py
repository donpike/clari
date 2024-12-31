#!/usr/bin/env python3
import sys
import json
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.tools.code_improver import CodeImproverTool

async def run_server():
    """Run the MCP server"""
    # Initialize the tool
    tool = CodeImproverTool()
    
    while True:
        try:
            # Read request from stdin
            request_str = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not request_str:
                break
                
            # Parse request
            request = json.loads(request_str)
            
            # Handle request using the tool
            response = await tool.handle_request(request)
            
            # Send response
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            # Send error response
            print(json.dumps({
                'jsonrpc': '2.0',
                'error': {'code': -32000, 'message': str(e)},
                'id': None
            }), flush=True)

if __name__ == "__main__":
    asyncio.run(run_server())
