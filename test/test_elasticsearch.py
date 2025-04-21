import sys
import time
import asyncio
sys.path.append("..")
from ultrarag.modules.database import ESIndex

client = ESIndex("http://localhost:9200")

print(asyncio.run(client.create("test_index")))

print(asyncio.run(
    client.insert(
        "test_index",
        [
            {"content": "liming, a student in hefei high school", "age": 18}, 
            {"content": "xiaohong, a teacher in beijing", "age": 25}
        ], 
        func=lambda x: x, 
        callback=None
        )
    )
)
time.sleep(1)
print(asyncio.run(client.search("test_index", query="liming")))

print(asyncio.run(client.get_collection()))

print(asyncio.run(client.remove("test_index")))

print(asyncio.run(client.get_collection()))