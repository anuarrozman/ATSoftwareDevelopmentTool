import asyncio

async def process_data(task_name):
    print(f"Starting {task_name}")
    await asyncio.sleep(2)  # Simulate some asynchronous operation
    print(f"Finished {task_name}")

# Optionally, add more functions or classes that use asyncio in component.py
