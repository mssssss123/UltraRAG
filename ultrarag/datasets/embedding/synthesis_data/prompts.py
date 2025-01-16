FEW_SHOT_NEG_ZH_PROMPT="""你是一位专注于从文档中提炼关键信息的专家。在本次任务中，你需要基于提供的两份文档，创建一个与第一份文档（文档A）紧密相关，同时确保与第二份文档（文档B）无直接关联的查询语句。生成的查询语句需保持风格、用语接近例子。尽量不要出现文档中包含的语句，且必须使用中文表达。

下面是一些例子（您的查询需要与这些例子接近！）：

{shot}
下面是提供的文档：

文档A（您的查询需要与该文档**相关**）：
<doc>
{doc_a}
</doc>

文档B（您的查询需要与该文档**无关**）：
<doc>
{doc_b}
</doc>

假设您已经仔细阅读并理解了上述两份文档的内容。请进行思考，如何给出查询使得其语言风格、用词、**标点符号**、结构、长度接近例子，并与文档A紧密相关，尽量不要出现文档A中包含的语句,以"思考："开始。
最后，请输出查询，可以是陈述句，并保持简洁，以"查询："开始，自由发挥创意。"""

FEW_SHOT_NEG_EN_PROMPT="""You are a query generation expert focused on distilling key information from documents. Given two documents, you need to create A query that is closely related to the first document (document A) but not directly related to the second document (document B). The generated query should be concise, do not appear in the statement contained in the document, the length should be less than 50 words, and must be expressed in English.

Here are some examples of queries:

{shot}

Here's the provided documentation:

Document A (your query needs to be ** relevant ** to this document) :
<doc>
{doc_a}
</doc>

Document B (your query needs to be ** independent ** of this document) :
<doc>
{doc_b}
</doc>

Suppose you are a professor who has carefully read and understood the contents of these two documents. 
First, output the thought about how to formulate the query so that its language style, word use, punctuation, structure, length are close to the examples, and closely related to document A. Try not to include statements contained in document A, starting with "Thought:".
Then, please generate a standard query according to the above requirements. Please start your answer with "Query:". Be creative!"""

ZERO_SHOT_NEG_ZH_PROMPT="""你是一位专注于从文档中提炼关键信息的专家。在本次任务中，你需要基于提供的两份文档，创建一个与第一份文档（文档A）紧密相关，同时确保与第二份文档（文档B）无直接关联的查询语句。尽量不要出现文档中包含的语句，且必须使用中文表达。

下面是提供的文档：

文档A（您的查询需要与该文档**相关**）：
<doc>
{doc_a}
</doc>

文档B（您的查询需要与该文档**无关**）：
<doc>
{doc_b}
</doc>

假设您已经仔细阅读并理解了上述两份文档的内容。请进行思考，如何给出查询使得其与文档A紧密相关，尽量不要出现文档A中包含的语句,以"思考："开始。
最后，请输出查询，可以是陈述句，并保持简洁，以"查询："开始，自由发挥创意。"""

ZERO_SHOT_NEG_EN_PROMPT = """You are a query generation expert focused on distilling key information from documents. Given two documents, you need to create A query that is closely related to the first document (document A) but not directly related to the second document (document B). The generated query should be concise, do not appear in the statement contained in the document, the length should be less than 50 words, and must be expressed in English.

Here's the provided documentation:

Document A (your query needs to be ** relevant ** to this document) :
<doc>
{doc_a}
</doc>

Document B (your query needs to be ** independent ** of this document) :
<doc>
{doc_b}
</doc>

Suppose you are a professor who has carefully read and understood the contents of these two documents. 
First, output the thought about how to make it closely related to document A. Try not to include statements contained in document A, starting with "Thought:".
Then, please generate a standard query according to the above requirements. Please start your answer with "Query:". Be creative!"""

SHOT_ZH_PROMPT = """\
例子{i}：{query}\
"""

SHOT_EN_PROMPT = """\
Shot {i}: {query}\
"""

# ZERO_SHOT_NEG_ZH_PROMPT 
# ZERO_SHOT_NEG_EN_PROMPT
# FEW_SHOT_ZH_PROMPT
# FEW_SHOT_EN_PROMPT
# ZERO_SHOT_ZH_PROMPT
# ZERO_SHOT_EN_PROMPT