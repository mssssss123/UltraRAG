## VisRAG部署demo

1. 模型准备，需要下载以下模型：

```
modelscope download --model tcy006/VisRAG-Ret --local_dir ./resource/models/VisRAG-Ret 

modelscope download --model OpenBMB/MiniCPM-V-2_6 --local_dir ./resource/models/MiniCPM-V-2_6
```

2. 搭建 UltraARG 环境并运行
