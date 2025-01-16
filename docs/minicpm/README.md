## 如何将你的minicpm模型在ollama上跑起来

1. 你需要下载mincpm模型文件，可以从modelscope（国内）/ hugging face（国外）下载。
2. 将你的transformer-style模型文件转换成gguf文件。具体地，你可以通过llama.cpp转换成gguf，可以参考官网浮动教程实现，不赘述。
3. 用以下命令打包ollama文件 `ollama create -n model_name -f Modelfile`，其中的Modelfile文件参考同路径下的Modelfile。
4. 运行ollama版本的模型，`ollama run model_name`。

注意：minicpm转换时可能会出现报错，此时请考虑该版本的[llamacpp](https://github.com/zkh2016/llama.cpp/tree/fix_for_gpa)
