from mcp.server.fastmcp import FastMCP

mcp = FastMCP("")

def main():
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()