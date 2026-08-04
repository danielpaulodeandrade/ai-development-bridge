import os
import asyncio
import pytest
from src.workflow_engine.skills import ReadFileSkill, WriteFileSkill

def test_read_and_write_file_skill(tmp_path):
    read_skill = ReadFileSkill()
    write_skill = WriteFileSkill()
    
    test_file = tmp_path / "test_file.txt"
    
    async def run():
        # Test read missing file
        res = await read_skill.execute(file_path=str(test_file))
        assert res.success is False
        assert "não encontrado" in res.error
        
        # Test write file
        res_write = await write_skill.execute(file_path=str(test_file), content="Hello AI!")
        assert res_write.success is True
        
        # Test read existing file
        res_read = await read_skill.execute(file_path=str(test_file))
        assert res_read.success is True
        assert res_read.data == "Hello AI!"
        
    asyncio.run(run())
