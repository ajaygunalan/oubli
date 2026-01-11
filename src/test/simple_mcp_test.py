from oubli.mcp_server import memory_save, memory_list, memory_stats

# Save
result = memory_save('MCP test memory', level=0, topics=['mcp'])
print(f'Saved: {result}')

# List
print(f'All memories: {memory_list()}')

# Stats
print(f'Stats: {memory_stats()}')

from oubli.mcp_server import mcp; print(f'Server: {mcp.name}')
