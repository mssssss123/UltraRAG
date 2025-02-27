from openai import AsyncOpenAI
import os
import json
from tqdm import tqdm
import asyncio
from typing import Set
import argparse
import uvloop
from asyncio import Lock
import aiofiles
import jsonlines
import traceback

file_lock = Lock()

client = AsyncOpenAI(
    api_key=os.environ.get("VLLM_API_KEY"),
    base_url="http://localhost:6000/v1/"
)

async def arun(messages, pbar, output_file):
    try:
        resp = await client.chat.completions.create(
            model='DeepSeek-R1-Distill-Qwen-32B',
            messages=messages,
            stream=False
        )
        result = resp.choices[0].message.content

        # Write to file with lock
        async with file_lock:
            async with aiofiles.open(output_file, mode="a") as f:
                await f.write(json.dumps(dict(input=messages, output=result), ensure_ascii=False) + "\n")
                await f.flush()

        pbar.set_postfix(active=len(pbar.active_tasks), refresh=False)
        pbar.update(1)
    except:
        pbar.update(1)

    return None


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str, help='input file is a jsonl, and each line is a \
                        messages follow openai format', required=True)
    parser.add_argument("--output_file", type=str, required=True)
    parser.add_argument("--max_concurrent", type=int, default=50)
    args = parser.parse_args()

    # '/home/guodewen/dataset/soda_bgem3/dataset/sodatest2/segment_all.jsonl'
    with jsonlines.open(args.input_file, 'r') as fr:
        lines = list(fr)

    active_tasks: Set[asyncio.Task] = set()
    pbar = tqdm(
        total=len(lines),
        desc="Generating Responses",
        unit="row",
        mininterval=2,
        smoothing=0.0001,
    )
    pbar.active_tasks = active_tasks
    for messages in lines:
        # Wait if we've hit the concurrency limit
        while len(active_tasks) >= args.max_concurrent:
            done, active_tasks = await asyncio.wait(active_tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                try:
                    await task
                except Exception as e:
                    print(f"Task failed: {e}")

        task = asyncio.create_task(arun(messages, pbar, args.output_file))
        active_tasks.add(task)
        task.add_done_callback(active_tasks.discard)

        pbar.set_postfix(active=len(active_tasks), refresh=True)

    # Wait for remaining tasks
    if active_tasks:
        await asyncio.gather(*active_tasks, return_exceptions=True)

    pbar.close()


if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())