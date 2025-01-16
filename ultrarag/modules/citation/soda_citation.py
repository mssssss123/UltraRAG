import re
import json
import asyncio
import requests
from loguru import logger
from .base import BaseCite
from typing import Any, List, Dict
from enum import Enum
from dataclasses import dataclass
from functools import cache

@dataclass
class SodaCitationOuput:
    class OutputType(Enum):
        steams = 0
        result = 1
        sensitive = 2

    types: OutputType
    content: List[Any]


class SodaCitation(BaseCite):
    def __init__(self, url: str, params: Any) -> None:
        super().__init__()
        self.url = url
        self.citation_param = params
        logger.info(f"{self.__class__.__name__} use url: {url} with param {params}")


    async def arun(self, reponse_generator: Any, reference: List[Any]):
        ans_paragraph_cache: str = ""
        citation_infos: list = []
        retrieved_nodes = reference

        len_last_sse_str_without_newline = 0
        citation_idx = 1

        sse_times = 1
        async for sse_data in reponse_generator:
            if sse_data.status == "sensitive":
                # TODO：如果敏感，结束，不再进行生成和引用操作
                yield SodaCitationOuput(types=SodaCitationOuput.OutputType.sensitive, content=None)
                return

            sse_times += 1
            ans_paragraph_cache += sse_data.content
            if "\n\n" in sse_data.content:
                citation_idx, new_sse_data, more_citation_info, ans_paragraph_cache = self.cite(
                    citation_idx,
                    len_last_sse_str_without_newline,
                    ans_paragraph_cache,
                    retrieved_nodes)
                len_last_sse_str_without_newline = len(ans_paragraph_cache)
                citation_infos.extend(more_citation_info)
            else:
                new_sse_data = sse_data.content
                len_last_sse_str_without_newline += len(sse_data.content)
            yield SodaCitationOuput(types=SodaCitationOuput.OutputType.steams, content=new_sse_data)

        if ans_paragraph_cache is not None:
            citation_idx, new_sse_data, more_citation_info, _ = self.cite(
                citation_idx,
                len_last_sse_str_without_newline,
                ans_paragraph_cache,
                retrieved_nodes,
                is_last=True)
            citation_infos.extend(more_citation_info)
            yield SodaCitationOuput(types=SodaCitationOuput.OutputType.steams, content=new_sse_data)
        yield SodaCitationOuput(types=SodaCitationOuput.OutputType.result, content=citation_infos) 


    def cite(self, citation_idx, len_last_sse_str_without_newline, ans_paragraph_cache, retrieval_info, is_last=False):
        citation_info = []

        paragraphs, ans_paragraph_cache = self.get_true_paragraphs(ans_paragraph_cache, self.citation_param, is_last)
        new_sse_data_str = ""
        for i, paragraph in enumerate(paragraphs):
            paragraph_str = paragraph["text"]

            if paragraph["need_citation"]:
                citation_idx, more_sse_data_str, citations = self.get_citation_info(citation_idx, paragraph_str, retrieval_info, self.citation_param)
                citation_info.append(citations)
                new_sse_data_str += more_sse_data_str if i != 0 else more_sse_data_str[len_last_sse_str_without_newline:]

            else:
                new_sse_data_str += paragraph_str if i != 0 else paragraph_str[len_last_sse_str_without_newline:]

            new_sse_data_str += "\n"
        if not is_last:
            new_sse_data_str += "\n" + ans_paragraph_cache
        return citation_idx, new_sse_data_str, citation_info, ans_paragraph_cache


    def get_true_paragraphs(self, ans_paragraph_cache, citation_param, is_last):
        paragraphs              = ans_paragraph_cache.split("\n\n")
        paragraphs_info         = []
        new_ans_paragraph_cache = paragraphs[-1]
        paragraphs_to_deal      = paragraphs if is_last else paragraphs[:-1]
        for paragraph in paragraphs_to_deal:
            if paragraph == "":
                continue
            need_citation = True
            if len(paragraph) < getattr(self.citation_param, "min_paragraph_len", 20):
                need_citation = False
            if paragraph[-1] in getattr(self.citation_param, "skipped_punctuation_list", [":", "："]):
                need_citation = False
            paragraphs_info.append({"text": paragraph, "need_citation": need_citation})
        return paragraphs_info, new_ans_paragraph_cache


    def get_citation_info(self, citation_idx, one_ans_paragraph, retrieval_info, citation_param):
        cited_chunks      = self._spilt_cited_chunks(retrieval_info, self.citation_param)
        citation_score    = self._get_citation_score(one_ans_paragraph, cited_chunks, self.citation_param)
        citation_idx, citations = self._get_citations_by_param(citation_idx, citation_score, cited_chunks, self.citation_param)

        data = {}
        file_num = 0
        for c in citations:
            if c["file_id"] in data:
                data[c["file_id"]].append(c["citation_idx"])
            else:
                data[c["file_id"]] = [c["citation_idx"]]
                file_num += 1
                if file_num == 3:
                    break

        more_sse_data_str = one_ans_paragraph + "".join(["[" + str(fid) + "!" + "".join([cid + "^" for cid in cids]) + "@#SODA]" for fid, cids in data.items()])

        return citation_idx, more_sse_data_str, citations

    def _spilt_cited_chunks(self, retrieval_info, citation_param):
        chunk_size      = getattr(self.citation_param, "chunk_size", 128)
        chunk_overlap   = getattr(self.citation_param, "chunk_overlap", 64)
        cited_chunks    = []

        for ref in retrieval_info:
            for citation in self._segment(
                segment=ref.content["content"],
                segment_start_index=ref.content["start_index"],
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            ):
                cited_chunks.append({
                    "text": citation["text"], 
                    "span": citation["span"],
                    "segment_id": ref.content["segment_id"],
                    "file_id": ref.content["file_id"],
                })
        return cited_chunks


    def _get_citation_score(self, one_ans_paragraph, cited_chunks, citation_param):
        HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}
        if len(cited_chunks) == 0:
            return []
  
        r = requests.post(
            self.url,
            json={"query": one_ans_paragraph, "texts": [c["text"] for c in cited_chunks]},
            headers=HEADERS,
            timeout=5000,
        )
        assert r.status_code == 200
        return r.json()


    def _get_citations_by_param(self, citation_idx, citation_score, cited_chunks, citation_param):
        budget = getattr(self.citation_param, "budget_for_one_minus_rerank_score", -1)
        threshold = getattr(self.citation_param, "citation_rerank_threshold", 0.4)
        rerank_index = sorted(
            range(len(citation_score)), key=lambda k: citation_score[k], reverse=True)
        if budget > 0:
            citations = []
            for i in range(len(cited_chunks)):
                if citation_score[i] > threshold:
                    if budget > 0:
                        citations.append(
                            {
                                "text" : cited_chunks[rerank_index[i]]["text"],
                                "span" : cited_chunks[rerank_index[i]]["span"],
                                "score": citation_score[i],
                                "segment_id": cited_chunks[rerank_index[i]]["segment_id"],
                                "file_id": cited_chunks[rerank_index[i]]["file_id"],
                                "citation_idx": str(citation_idx),
                            }
                        )
                        citation_idx += 1
                        budget -= 1 - citation_score[i]
        else:
            max_citation_num_per_paragraph = getattr(self.citation_param, "max_citation_num_per_paragraph", 5)
            for i in range(min(max_citation_num_per_paragraph, len(cited_chunks))):
                if citation_score[i] > threshold:
                    citations.append({
                        "text" : cited_chunks[rerank_index[i]]["text"],
                        "span" : cited_chunks[rerank_index[i]]["span"],
                        "score": citation_score[i],
                        "segment_id": cited_chunks[rerank_index[i]]["segment_id"],
                        "file_id": cited_chunks[rerank_index[i]]["file_id"],
                        "citation_idx": citation_idx,
                    })
                    citation_idx += 1
        return citation_idx, citations


    @cache
    def _segment(self, segment, segment_start_index, chunk_size, chunk_overlap):
        index = segment_start_index
        sub_segments, true_overap = [], 0
        for sub_segment, next_overap in self._split_text(segment, chunk_size, chunk_overlap):
            index -= true_overap
            citation = {"text": sub_segment, "span": [index, index + len(sub_segment) - 1]}
            sub_segments.append(citation)
            index += len(sub_segment)
            true_overap = next_overap
        return sub_segments


    def _split_text(self, segment, chunk_size, chunk_overlap):
        chunks, chunk_now, size_now, true_overlap_size = [], [], 0, 0
        no_left = False
        for s in self._zng(segment):
            no_left = False
            chunk_now.append(s)
            size_now += len(s)
            if size_now > chunk_size:
                chunk = "".join(chunk_now)
                chunk_now, size_now = self._get_overlap(chunk_now, chunk_overlap)
                true_overlap_size = len("".join(chunk_now))
                chunks.append([chunk, true_overlap_size])
                no_left = True

        if no_left == False:
            chunks.append(["".join(chunk_now), true_overlap_size])
        return chunks


    def _zng(self, paragraph):
        new_zngs = []
        sub_chunk = ''
        for sent in re.split(u'(！|？|。|\\n)', paragraph, flags=re.U):
            if sent in (u'！', u'？', u'。', ''):
                sub_chunk += sent
            else:
                if sub_chunk != '':
                    new_zngs.append(sub_chunk)
                sub_chunk = sent
        if sub_chunk != '':
            new_zngs.append(sub_chunk)
        return new_zngs


    def _get_overlap(self, chunk, chunk_overlap):
        rchunk = chunk[:]
        rchunk.reverse()
        size_now, overlap = 0, []
        for s in rchunk[:-1]:
            overlap.append(s)
            size_now += len(s)
            if size_now > chunk_overlap:
                break
        overlap.reverse()
        return overlap, size_now