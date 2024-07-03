import asyncio
from component import process_data

async def main():
    # Start your asyncio tasks here
    task1 = asyncio.create_task(process_data("Task 1"))
    task2 = asyncio.create_task(process_data("Task 2"))

    # Wait for tasks to complete
    await asyncio.gather(task1, task2)

if __name__ == "__main__":
    asyncio.run(main())
