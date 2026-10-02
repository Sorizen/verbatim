import asyncio

from app.exceptions import MediaToolError

STDERR_TAIL_CHARS = 800


async def run_tool(binary: str, args: list[str]) -> bytes:
    process = await asyncio.create_subprocess_exec(
        binary,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode:
        raise MediaToolError(f'{binary} failed: {stderr.decode(errors="ignore")[-STDERR_TAIL_CHARS:]}')
    return stdout
