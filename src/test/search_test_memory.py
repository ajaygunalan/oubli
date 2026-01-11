from oubli.storage import MemoryStore

store = MemoryStore()
results = store.search('test')
print(f'Found {len(results)} memories')
for r in results:
  print(f'  - {r.summary}')
