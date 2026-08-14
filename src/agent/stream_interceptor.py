import logging
from typing import AsyncGenerator
from src.agent.parser import AACPParser
from src.agent.models import FileAction, RunAction
from src.agent.file_executor import FileExecutor
from src.agent.shell_executor import ShellExecutor

logger = logging.getLogger(__name__)

async def intercept_aacp_stream(async_gen: AsyncGenerator[str, None]) -> AsyncGenerator[str, None]:
    """
    Intercepts a stream of markdown text.
    If it detects AACP tags (<<<FILE_CREATE:...>>> or <<<RUN:...>>>),
    it buffers the content until the tag is closed (<<<END_FILE>>> or <<<END_RUN>>>),
    executes the action on the server, and yields only a visual badge instead of the raw tags.
    """
    buffer = ""
    
    async for delta in async_gen:
        if not delta:
            continue
            
        buffer += delta
        
        while True:
            idx = buffer.find("<<<")
            if idx == -1:
                # No tags. Yield all except the last 2 chars just in case we are in the middle of writing "<<<"
                if len(buffer) > 2:
                    yield buffer[:-2]
                    buffer = buffer[-2:]
                break
            else:
                # We found a "<<<". Yield everything before it.
                if idx > 0:
                    yield buffer[:idx]
                    buffer = buffer[idx:]
                
                # Now buffer starts exactly with "<<<"
                valid_prefixes = ["<<<FILE_CREATE:", "<<<RUN:"]
                
                is_potential_tag = False
                is_definite_tag = False
                
                for prefix in valid_prefixes:
                    if buffer.startswith(prefix):
                        is_definite_tag = True
                        break
                    elif prefix.startswith(buffer):
                        is_potential_tag = True
                        break
                        
                if is_definite_tag:
                    # It is a valid tag. Must wait until we see the closing tag.
                    if buffer.startswith("<<<FILE_CREATE:"):
                        closing_tag = "<<<END_FILE>>>"
                    else:
                        closing_tag = "<<<END_RUN>>>"
                        
                    close_idx = buffer.find(closing_tag)
                    if close_idx != -1:
                        # We have the full tag!
                        end_of_tag = close_idx + len(closing_tag)
                        full_tag_text = buffer[:end_of_tag]
                        
                        # Parse and execute
                        try:
                            actions = AACPParser.parse(full_tag_text)
                            for action in actions:
                                if isinstance(action, FileAction):
                                    logger.info(f"Executando FileAction (interceptor): {action.action_type.value}")
                                    res = FileExecutor.execute(action)
                                elif isinstance(action, RunAction):
                                    logger.info("Executando RunAction (interceptor)...")
                                    res = ShellExecutor.execute(action)
                                else:
                                    res = "Executed."
                                    
                                badge = f"\n> **Agent Execution:**\n> ```text\n> {res}\n> ```\n"
                                yield badge
                        except Exception as e:
                            logger.error(f"Erro no interceptor AACP: {e}")
                            yield full_tag_text
                            
                        buffer = buffer[end_of_tag:]
                        continue # Re-evaluate the rest of the buffer
                    else:
                        # We don't have the closing tag yet. Need more chunks.
                        break
                elif is_potential_tag:
                    # It's "<" or "<<<F" etc. Need more chunks to be sure.
                    break
                else:
                    # It starts with "<<<" but it's NOT a valid tag (e.g. "<<< Hello").
                    # Yield the first char and continue.
                    yield buffer[0]
                    buffer = buffer[1:]
                    continue
                    
    # Flush remaining
    if buffer:
        yield buffer
