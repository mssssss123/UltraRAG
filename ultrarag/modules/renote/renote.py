''' The work is based on https://github.com/thunlp/Adaptive-Note.git, 
    but some detail and prompts maybe change to adapte our project.
'''
import re
import os, json
from pathlib import Path
from typing import Callable, List
from dataclasses import dataclass, asdict
from ultrarag.common.utils import format_view

from .prompts import RENOTE_PROMPTS

@dataclass
class ReNoteState:
    curr_query: str
    curr_refs: List[str]
    curr_note: str
    best_note: str

    def to_json(self):
        infos = asdict(self)
        return json.dumps(infos, ensure_ascii=False)
    
    def to_dict(self):
        return asdict(self)


def load_prompt(dir_path, prompt_file):
    prompt_path = os.path.join(dir_path, prompt_file)
    if not Path(prompt_path).is_file():
        raise ValueError(f"prompt {prompt_path} is not exist!")
    with open(prompt_path, "r", encoding='utf8') as fr:
        data = fr.read()
        return data


class ReNote:
    def __init__(self, 
        retriever: Callable, 
        generator: Callable, 
        prompt_file: str="", 
        max_step=2,
        max_topn=10,
        stream=True,
        system_prompt: str=None
    ) -> None:
        ''' args:
                system_prompt: string type and if not none, will add system_prompt at
                the head of answer phase.
        '''
        self._max_step = max_step
        self._max_topn = max_topn
        self._stream = stream
        if not callable(retriever):
            raise ValueError("retriever is not a function")

        if not callable(generator):
            raise ValueError("generator is not a function")

        self.retriever = retriever
        self.generator = generator

        if prompt_file:
            self.define_notes_prompt = load_prompt(prompt_file, 'define_notes.pmt')
            self.refine_notes_prompt = load_prompt(prompt_file, 'refine_notes.pmt')
            self.update_notes_prompt = load_prompt(prompt_file, 'update_notes.pmt')
            self.gen_new_query_prompt = load_prompt(prompt_file, 'gen_new_query.pmt')
            self.answer_by_notes_prompt = load_prompt(prompt_file, 'answer_by_notes.pmt')
            self._system_prompt = system_prompt
        else:
            self.define_notes_prompt = RENOTE_PROMPTS["define_notes"]
            self.refine_notes_prompt = RENOTE_PROMPTS["refine_notes"]
            self.update_notes_prompt = RENOTE_PROMPTS["update_notes"]

            self.gen_new_query_prompt = RENOTE_PROMPTS["gen_new_query"]
            self.answer_by_notes_prompt = RENOTE_PROMPTS["answer_by_notes"]
            self._system_prompt = system_prompt



    async def arun(self, query: str, collection, topn: str=5):
        if query == "": 
            raise ValueError("query is empty")
        
        query_list, refs_list = [], []
        state_list: List[ReNoteState] = []
        curr_note, best_note = '', ''

        # init note
        recalls = await self.retriever(query=query, topn=topn, collection=collection)
        recalls = [item.content for item in recalls]
        curr_note = best_note = await self.define_notes(query, recalls)
        state_list.append(ReNoteState(curr_query=query, curr_refs=recalls, 
                                        curr_note=curr_note, best_note=best_note))
        refs_list.extend(recalls)
        yield dict(state=f"renote: {query}", value=dict(recalls=recalls, best_note=best_note))

        for step in range(self._max_step):
            if len(refs_list) > self._max_topn: break
            
            curr_query = await self.gen_new_query(query, best_note, query_list)
            query_list.append(curr_query)
            curr_query = curr_query.replace("\n", "")

            query_str = f"{curr_query}\n{query}"
            curr_refs = await self.retriever(query=query_str, topn=topn, collection=collection)
            curr_refs = [item.content for item in curr_refs]
            
            refs_filter = list(filter(lambda x: x not in refs_list, curr_refs))
            refs_list.extend(refs_filter)
            if not refs_filter: break
            
            curr_note = await self.refine_notes(query, refs_filter, best_note)
            best_note = await self.update_notes(query, curr_note, best_note)
            state_list.append(ReNoteState(curr_query=curr_query, curr_refs=curr_refs, 
                                            curr_note=curr_note, best_note=best_note))
            new_query_str = curr_query.replace("\n", "")
            yield dict(state=f"thinking {step+1}: {new_query_str}", 
                       value=dict(recalls=refs_filter, curr_note=curr_note, best_note=best_note))
        
        yield dict(state="allnote", value=best_note)
        final_answer = await self.answer_by_notes(query=query, notes=best_note)
        if self._stream:
            async for item in format_view(final_answer):
                yield dict(state="data", value=item)
        else:
            yield dict(state="data", value=final_answer)
            
        yield dict(state="extra", value=state_list)
    

    async def define_notes(self, query: str, recalls: List[str]):
        content = self.define_notes_prompt.format(query=query, refs="\n".join(recalls))
        message = {"role": 'user', 'content': content}
        response = await self.generator(message)
        # Replace the incomplete line:
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        return response


    async def refine_notes(self, query: str, recalls: List[str], notes: str):
        content = self.refine_notes_prompt.format(query=query, refs="\n".join(recalls), note=notes)
        message = {"role": 'user', 'content': content}
        response = await self.generator(message)
        # Replace the incomplete line:
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        return response


    async def update_notes(self, query: str, curr_notes: str, best_notes: str):
        content = self.update_notes_prompt.format(query=query, new_note=curr_notes, best_note=best_notes)
        message = {"role": 'user', 'content': content}
        response = await self.generator(message)
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        is_swap = "true" in response.lower()
        
        return curr_notes if is_swap else best_notes


    async def gen_new_query(self, query: str, notes: str, history_query: List[str]):
        content = self.gen_new_query_prompt.format(query=query, note=notes, query_log="\n".join(history_query))
        message = {"role": 'user', 'content': content}
        response = await self.generator(message)
        response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        return response


    async def answer_by_notes(self, query: str, notes: str):
        content = self.answer_by_notes_prompt.format(query=query, note=notes)
        message = []
        if self._system_prompt:
            message.append({"role": "system", "content": self._system_prompt})
        message.append({"role": 'user', 'content': content})
        return await self.generator(message, stream=self._stream)
