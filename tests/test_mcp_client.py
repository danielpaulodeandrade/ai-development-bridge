import pytest
import asyncio
from src.mcp.client import MCPClient

def test_mcp_client_connection_and_execution():
    client = MCPClient("mock://local")
    
    async def run():
        # Antes de conectar, deve falhar
        with pytest.raises(RuntimeError):
            await client.list_tools()
            
        with pytest.raises(RuntimeError):
            await client.call_tool("mcp_dummy_tool", {})
            
        # Conectar
        await client.connect()
        assert client.connected is True
        
        # Testar list_tools
        tools = await client.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "mcp_dummy_tool"
        
        # Testar call_tool com erro
        with pytest.raises(ValueError):
            await client.call_tool("invalid_tool", {})
            
        # Testar call_tool sucesso
        res = await client.call_tool("mcp_dummy_tool", {"param": 1})
        assert res["status"] == "success"
        assert res["args"]["param"] == 1
        
        # Desconectar
        await client.disconnect()
        assert client.connected is False
        
    asyncio.run(run())
