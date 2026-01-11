from oubli.core_memory import save_core_memory, load_core_memory

save_core_memory('# My Core Memory\n\nI am a test user.')
print(load_core_memory())
