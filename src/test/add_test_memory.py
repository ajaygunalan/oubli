from oubli.storage import MemoryStore

store = MemoryStore()
id = store.add(summary='Test memory', full_text='Details here', level=0, topics=['test'])
print(f'Created: {id}')
mem = store.get(id)
print(f'Retrieved: {mem.summary}')
