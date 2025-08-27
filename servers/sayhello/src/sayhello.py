from typing import Dict

from ultrarag.server import UltraRAG_MCP_Server

app = UltraRAG_MCP_Server("sayhello")


@app.tool(output="name->msg")
def greet(name: str) -> Dict[str, str]:
    ret = f"Hello, {name}!"
    app.logger.info(ret)
    return {"msg": ret}


if __name__ == "__main__":
    # Start the sayhello server using stdio transport
    app.run(transport="stdio")
