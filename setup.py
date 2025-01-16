from setuptools import setup, find_namespace_packages

setup(
    name="ultrarag",
    version="0.1.0",
    description="UltraRAG: A RAG System for developing LLM applications",
    author="",
    author_email="",
    # 只包含 ultrarag 目录下的 Python 文件
    packages=find_namespace_packages(include=["ultrarag", "ultrarag.*"]),
    # 排除测试文件和缓存文件
    exclude=["tests*", "*.tests.*", "*.tests", "*.pyc"],
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0", 
        "numpy>=1.24.0",
        "aiohttp>=3.8.0",
        "loguru>=0.7.0",
        "PyMuPDF>=1.22.0",  # fitz
        "Pillow>=10.0.0",   # PIL
        "llama-index-core>=0.10.0",
        "stanza>=1.5.0",    # 可选的中文分词
        "python-docx>=0.8.11",  # docx文件支持
        "python-pptx>=0.6.21",  # pptx文件支持
        "markdown>=3.4.0",      # markdown文件支持
        "qdrant-client>=1.7.0", # 向量数据库
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'black>=23.0.0',
            'isort>=5.12.0',
            'flake8>=6.0.0',
        ]
    },
    python_requires=">=3.8",
    # 不包含任何包数据文件
    include_package_data=False,
    zip_safe=False,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ]
)


