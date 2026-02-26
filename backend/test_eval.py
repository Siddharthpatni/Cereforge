import asyncio
from app.services.task_evaluator import evaluate_submission

async def main():
    print("Testing evaluator directly:")
    res = await evaluate_submission("def my_func(): pass", "Test Task", "Beginner")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
