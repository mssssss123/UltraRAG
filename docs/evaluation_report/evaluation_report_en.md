## Overall Overview

UltraRAG is equipped with a series of model tuning methods and evaluation metrics. To validate the effectiveness of these methods, we used data from specific vertical domains to conduct a series of validations on UltraRAG, and finally provided corresponding analysis metrics. These metrics confirmed the feasibility of UltraRAG.

## Evaluation Description

The list of models used in our experiments is shown below. Besides supporting the following models, UltraRAG is continually improving support for other models.

| **Scenario**                  | **Model**               | **Value**             | **Model Access Path**                                                                                      |
| ----------------------------- | ----------------------- | --------------------- | ----------------------------------------------------------------------------------------------------------- |
| VanilaRAG, Adaptive-Note, KBalign | Text Embedding Model    | MiniCPM-Embedding-Light    | [ModelScope](https://modelscope.cn/models/OpenBMB/MiniCPM-Embedding-Light)｜[HuggingFace](https://huggingface.co/OpenBMB/MiniCPM-Embedding-Light)                                                                                       |
| VanilaRAG, Adaptive-Note, KBalign | Reranker Model         | bge-large-reranker    | [ModelScope](https://modelscope.cn/models/OpenBMB/MiniCPM-Reranker-Light)｜[HuggingFace](https://huggingface.co/OpenBMB/MiniCPM-Reranker-Light) |
| VanilaRAG, Adaptive-Note, KBalign | Text LLM                | MiniCPM3-4B           | [ModelScope](https://modelscope.cn/models/OpenBMB/MiniCPM3-4B)｜[HuggingFace](https://huggingface.co/openbmb/MiniCPM3-4B)        |
| VisRAG                          | Image-Text Embedding Model | VisRAG-Ret            | [HuggingFace](https://huggingface.co/openbmb/VisRAG-Ret)                                                        |
| VisRAG                          | Multimodal LLM Model   | MiniCPM-V-2_6        | [ModelScope](https://modelscope.cn/models/OpenBMB/MiniCPM-V-2_6)｜[HuggingFace](https://huggingface.co/openbmb/MiniCPM-V-2_6)    |

The datasets and evaluation sets used in our evaluation process that can be disclosed are as follows:

| **Parameter** | **Value**                                                | **Remarks**                             |
| -------------- | -------------------------------------------------------- | --------------------------------------- |
| Knowledge Base | Compilation of electronic textbooks in the legal field, see **Appendix** for details | Slice length 512, approximately 880,000 slices |
| Evaluation Set | Partial evaluation set from [LawBench](https://github.com/open-compass/LawBench) | Selected zero-shot test sets 3-2 and 3-8 |

We evaluated all methods involved in the UltraRAG framework, detailed as follows:

| **Method**                  | **Description**                                 |
| --------------------------- | ------------------------------------------------ |
| **VanillaRAG**              | Conduct experiments using pre-tuned embedding+reranker+LLM |
| **UltraRAG-DDR**            | Conduct experiments using pre-tuned embedding model and pre-tuned LLM |
| **UltraRAG-KBAlign**        | Conduct experiments after fine-tuning the model with the KBAlign method |
| **VanillaRAG-finetune**     | Conduct experiments using fine-tuned embedding model and fine-tuned LLM |
| **UltraRAG-Adaptive-Note**  | Conduct experiments using pre-tuned embedding+LLM |

## Evaluation Results

The overall evaluation results are as follows.

| **End-to-End Performance** | **Article Prediction (3-2) ROUGE-L** |
| -------------------------- | ------------------------------------ |
| **VanillaRAG**             | 40.75                               |
| **UltraRAG-DDR**           | 53.14                               |
| **UltraRAG-KBAlign**       | 48.72                               |

| **End-to-End Performance**     | **Consultation (3-8) ROUGE-L** |
| ------------------------------ | ------------------------------- |
| **VanillaRAG**                 | 23.65                          |
| **UltraRAG-Adaptive-Note**     | 24.62                          |
| **VanillaRAG-Finetune**        | 25.85                          |

| **Retrieval Performance**                                          | **Test Set of 200 Items by gpt4o MRR@10** | **Test Set of 200 Items by gpt4o NDCG@10** | **Test Set of 200 Items by gpt4o Recall@10** |
| ------------------------------------------------------------------ | ----------------------------------------- | ------------------------------------------ | -------------------------------------------- |
| MiniCPM-Embedding-Light               | 36.46                                     | 40.05                                      | 54.50                                        |
|MiniCPM-Embedding-Light-Finetune (2800 Items Created by Qwen2.5-14B)   | 37.57                                     | 42.12                                      | 56.50                                        |

### Case Analysis of VanillaRAG

Compared to before fine-tuning, the fine-tuned VanillaRAG exhibits higher accuracy in responses and more consistent output style.

##### After Fine-tuning:

```JSON
{
    "instruction": "请根据具体场景与问题给出法律依据，只需要给出具体法条内容，每个场景仅涉及一个法条。",
    "query": "场景:小明在一家外商投资企业上班，因为工作环境不安全发生了工伤。根据哪条法律，外商投资企业应该遵守劳动保护的规定？",
    "answer": "根据外商投资法的第32条规定，外商投资企业开展生产经营活动，应当遵守法律、行政法规有关劳动保护的规定。因此，外商投资企业应该确保员工的工作环境安全，遵守国家劳动保护相关的法律法规。当员工因为工作原因受伤时，企业还应该提供相应的医疗救治，同时积极协助员工申请工伤保险福利。",
    "prediction": "根据《外商投资企业投资管理条例》第三十二条，外商投资企业应当遵守法律、行政法规有关劳动保护、社会保险的规定。因此，外商投资企业应该遵守劳动保护的规定，确保工作环境安全，防止工伤事故的发生。",
    "rouge_score": 54.13533785403358
},
{
    "instruction": "请根据具体场景与问题给出法律依据，只需要给出具体法条内容，每个场景仅涉及一个法条。",
    "query": "场景:在一场拍卖会上，一位竞拍者以高价竞拍了一幅画，最终拍卖师以落槌的方式确认了竞拍者的最高应价。根据法律规定，竞买人的最高应价被确认后，拍卖的状态是什么？",
    "answer": "根据拍卖法的第五十一条规定，竞买人的最高应价经拍卖师落槌或者以其他公开表示买定的方式确认后，拍卖成交。因此，在这个场景中，经过拍卖师的确认后，竞拍者的最高应价确定且公示，拍卖达成成交状态。",
    "prediction": "根据《拍卖法》第五十一条的规定，竞买人的最高应价经拍卖师落槌或者以其他公开表示卖定的方式确认后，拍卖的状态是“拍卖成交”。",
    "rouge_score": 80.76923027089498
}
```

##### Before Fine-tuning:

```JSON
{
    "instruction": "请根据具体场景与问题给出法律依据，只需要给出具体法条内容，每个场景仅涉及一个法条。",
    "query": "场景:小明在一家外商投资企业上班，因为工作环境不安全发生了工伤。根据哪条法律，外商投资企业应该遵守劳动保护的规定？",
    "answer": "根据外商投资法的第32条规定，外商投资企业开展生产经营活动，应当遵守法律、行政法规有关劳动保护的规定。因此，外商投资企业应该确保员工的工作环境安全，遵守国家劳动保护相关的法律法规。当员工因为工作原因受伤时，企业还应该提供相应的医疗救治，同时积极协助员工申请工伤保险福利。",
    "prediction": "根据《中华人民共和国劳动法》第三十八条，劳动者享有社会保险和福利的权利。劳动者在患病或者非因工负伤时，享受医疗期；在工伤治疗期间，原工资待遇不变，由企业按照因公负伤的原则支付各项相关待遇。此外，根据《中华人民共和国劳动合同法》第九条，用人单位招用劳动者，不得要求劳动者提供单身证明、性别证明、年龄证明等与应聘职位无关的个人信息，不得以民族、种族、性别、宗教信仰、残疾、感染艾滋病病毒等为由拒绝录用，不得歧视或者变相歧视。同时，用人单位应当依法为劳动者缴纳社会保险费，并为劳动者创造安全、健康的工作环境，预防职业病，防止事故发生。如果发生工伤事故，劳动者有权获得医疗救治和经济补偿。根据《中华人民共和国安全生产法》第二十七条，矿山、建筑施工企业和危险品、烟花爆竹、民用爆破器材生产企业，应当建立应急救援体系，制定应急预案，并定期进行演练。其他生产经营单位从事有关易燃、易爆、毒性、放射性、有腐蚀性、有致癌、致畸、致变的原料、产品、设备、工艺、包装、储存或者运输的活动，以及从事高空、高压、高速、深潜、地下、水上、水下等高风险活动的，应当建立应急救援体系，制定应急预案，并定期进行演练。生产经营单位必须保险综合保险。此外，根据《中华人民共和国职业病防治法》第五条，国务院和县级以上地方人民政府卫生行政部门分别负责全国和具体行政区域内的职业病防治及其监督管理工作。根据《中华人民共和国职业病防治法》第二十六条，对可能发生职业病危害的作业岗位，应当向其工作人员发放个人使用的职业病防护设备和用品，并定期进行职业健康检查。发生或者可能发生急性职业病危害事故时，用人单位应当立即采取应急救援措施；接到职业病危害事故伤害的职工，有权要求及时救治、进行健康检查和职业病诊疗、安置备用岗位、对承担责任给予补偿，并有权向有关部门提出对违法行为的投诉。",
    "rouge_score": 17.869415424947753
},
{
    "instruction": "请根据具体场景与问题给出法律依据，只需要给出具体法条内容，每个场景仅涉及一个法条。",
    "query": "场景:在一场拍卖会上，一位竞拍者以高价竞拍了一幅画，最终拍卖师以落槌的方式确认了竞拍者的最高应价。根据法律规定，竞买人的最高应价被确认后，拍卖的状态是什么？",
    "answer": "根据拍卖法的第五十一条规定，竞买人的最高应价经拍卖师落槌或者以其他公开表示买定的方式确认后，拍卖成交。因此，在这个场景中，经过拍卖师的确认后，竞拍者的最高应价确定且公示，拍卖达成成交状态。",
    "prediction": "拍卖成交",
    "rouge_score": 13.559321907497846
}
```

### Case Analysis of UltraRAG-Adaptive-Note

Compared to VanillaRAG, the overall responses of Adaptive-Note are more structured and well-reasoned.

##### Adaptive-Note Results

```JSON
  {
    "instruction": "请回答下列问题，首先给出回答，然后给出对应的法律依据: ",
    "query": "我想抵押车去借钱，但是车我还得用，那边机构讲可以办理，但是需要先过户到他们公司名下请问这有什么风险吗？",
    "answer": "回答:购买抵押车有下列风险：抵押权人仍享有对车的优先受偿权；该车辆上可能设有多重担保或者债权；车辆不能过户；以及办理保险、机动车年审等手续时可能会缺少相关的材料，办理比较困难。法律依据:《民法典》第四百零五条抵押权设立前，抵押财产已经出租并转移占有的，原租赁关系不受该抵押权的影响。第四百零六条抵押期间，抵押人可以转让抵押财产。当事人另有约定的，按照其约定。抵押财产转让的，抵押权不受影响。抵押人转让抵押财产的，应当及时通知抵押权人。抵押权人能够证明抵押财产转让可能损害抵押权的，可以请求抵押人将转让所得的价款向抵押权人提前清偿债务或者提存。转让的价款超过债权数额的部分归抵押人所有，不足部分由债务人清偿。",
    "prediction": "回答：将车辆过户到贷款机构名下确实存在一定的风险。首先，根据《民法典》第406条的规定，即使你已经办理了过户登记，贷款机构仍可主张抵押物所有权变动对其不发生效力，这意味着如果贷款机构未能按时收回贷款，你仍然拥有车辆的所有权。然而，一旦车辆被贷款机构强行扣押，可能会对你造成不便。\n\n此外，贷款机构要求将车辆过户到其名下，可能意味着他们希望对车辆拥有一定的控制权，这可能会影响到你对车辆的使用和处置。尽管贷款机构可以就车辆的使用进行限制，但你作为车主，有权拒绝不合理的使用要求。如果你认为贷款机构的要求不合理，可以与他们进行沟通，或者寻求法律咨询，以保护自己的权益。\n\n综上所述，将车辆过户到贷款机构名下存在一定的风险，包括贷款机构可能对你的车辆使用进行限制，以及在贷款未能偿还的情况下，贷款机构可能对你的车辆采取措施。在考虑是否同意过户之前，建议仔细评估自身的经济状况和与贷款机构之间的合同条款，确保自己的权益得到充分保护。",
    "rouge_score": 22.077921583319288
  },
  {
    "instruction": "请回答下列问题，首先给出回答，然后给出对应的法律依据: ",
    "query": "我与公司解除劳动合同前，公司承诺我的绩效奖金3.10日发放，但今天说公司的账户冻结了请问我该怎么办？",
    "answer": "回答:可以起诉后强制执行律师解答公司以各种理由克扣绩效奖金，劳动者可以到劳动合同履行地或用人单位所在地的劳动仲裁委员会申请仲裁；也可以向劳动行政部门投诉，责令其支付劳动者工资，并可责令其支付赔偿金。法律依据:《工资支付暂行规定》第十八条各级劳动行政部门有权监察用人单位工资支付的情况。用人单位有下列侵害劳动者合法权益行为的，由劳动行政部门责令其支付劳动者工资和经济补偿，并可责令其支付赔偿金:（一）克扣或者无故拖欠劳动者工资的；（二）拒不支付劳动者延长工作时间工资的；（三）低于当地最低工资标准支付劳动者工资的。经济补偿和赔偿金的标准，按国家有关规定执行。第十九条劳动者与用人单位因工资支付发生劳动争议的，当事人可依法向劳动争议仲裁机关申请仲裁。对仲裁裁决不服的，可以向人民法院提起诉讼。律师解答公司账户被冻结的，无法付款，因此需要向法院申请解封。一般来说，账户中有员工工资的，公司以此为理由请求解封的，法院一般都会同意解封，之后可以依法支付工资。",
    "prediction": "面对公司账户冻结导致绩效奖金未能按时发放的情况，您首先应当要求公司提供其与法院的沟通记录，以及法院是否已受理破产申请的通知，以便确认公司的财务状况和可能的解决方案。根据《企业破产法》第19条的规定，如果公司确实存在破产风险，您可以要求公司采取措施解决账户冻结问题，或者依法申请个人工资和奖金的支付。\n\n同时，您应了解银行账户冻结的法律后果，以及公司是否有责任承担因账户冻结给您带来的损失。如果公司未能在合理期限内解决账户冻结问题，您有权要求公司赔偿相应的经济损失，包括但不限于利息损失和诉讼费用。在这种情况下，您可以考虑寻求法律援助，以维护自己的合法权益。\n\n此外，根据《劳动合同法》第50条的规定，公司在解除或终止劳动合同时，应出具书面证明并在15日内为劳动者办理档案和社会保险关系转移手续。如果您尚未找到新的接收单位，可以将档案和社会保险关系暂存入职业介绍服务中心或人才管理中心。因此，在解除劳动合同后，您应要求公司及时办理档案和社会保险关系转移手续，以保障自己的合法权益。\n\n最后，对于个人存款账户实名制，个人在开设银行账户时需提供真实有效的身份证明，银行将核实无误后办理开户手续。在取款时，需持存折或银行卡到银行柜台进行操作。因此，您应确保自己的银行账户信息真实有效，以避免因账户信息错误导致的损失。\n\n总之，在面对公司账户冻结导致绩效奖金未能按时发放的情况时，您应要求公司提供解决措施，了解银行账户冻结的法律后果，并寻求法律援助以维护自己的合法权益。同时，您还应关注档案和社会保险关系转移手续的办理，以保障自己的合法权益。",
    "rouge_score": 19.199999512376902
  }
```

##### VanillaRAG Result

```JSON
  {
    "instruction": "请回答下列问题，首先给出回答，然后给出对应的法律依据: ",
    "query": "我想抵押车去借钱，但是车我还得用，那边机构讲可以办理，但是需要先过户到他们公司名下请问这有什么风险吗？",
    "answer": "回答:购买抵押车有下列风险：抵押权人仍享有对车的优先受偿权；该车辆上可能设有多重担保或者债权；车辆不能过户；以及办理保险、机动车年审等手续时可能会缺少相关的材料，办理比较困难。法律依据:《民法典》第四百零五条抵押权设立前，抵押财产已经出租并转移占有的，原租赁关系不受该抵押权的影响。第四百零六条抵押期间，抵押人可以转让抵押财产。当事人另有约定的，按照其约定。抵押财产转让的，抵押权不受影响。抵押人转让抵押财产的，应当及时通知抵押权人。抵押权人能够证明抵押财产转让可能损害抵押权的，可以请求抵押人将转让所得的价款向抵押权人提前清偿债务或者提存。转让的价款超过债权数额的部分归抵押人所有，不足部分由债务人清偿。",
    "prediction": "风险在于，将车辆过户到贷款机构名下后，您将失去对车辆的控制权，并且如果贷款不能按时偿还，贷款机构可能依法采取强制执行措施，如托管、拍卖等，从而导致您失去车辆所有权。此外，这种操作也可能影响您今后的车辆抵押能力。建议在做出决策前，详细了解相关法规政策并咨询专业法律人士的意见。",
    "rouge_score": 15.38461490072322
  },
  {
    "instruction": "请回答下列问题，首先给出回答，然后给出对应的法律依据: ",
    "query": "我与公司解除劳动合同前，公司承诺我的绩效奖金3.10日发放，但今天说公司的账户冻结了请问我该怎么办？",
    "answer": "回答:可以起诉后强制执行律师解答公司以各种理由克扣绩效奖金，劳动者可以到劳动合同履行地或用人单位所在地的劳动仲裁委员会申请仲裁；也可以向劳动行政部门投诉，责令其支付劳动者工资，并可责令其支付赔偿金。法律依据:《工资支付暂行规定》第十八条各级劳动行政部门有权监察用人单位工资支付的情况。用人单位有下列侵害劳动者合法权益行为的，由劳动行政部门责令其支付劳动者工资和经济补偿，并可责令其支付赔偿金:（一）克扣或者无故拖欠劳动者工资的；（二）拒不支付劳动者延长工作时间工资的；（三）低于当地最低工资标准支付劳动者工资的。经济补偿和赔偿金的标准，按国家有关规定执行。第十九条劳动者与用人单位因工资支付发生劳动争议的，当事人可依法向劳动争议仲裁机关申请仲裁。对仲裁裁决不服的，可以向人民法院提起诉讼。律师解答公司账户被冻结的，无法付款，因此需要向法院申请解封。一般来说，账户中有员工工资的，公司以此为理由请求解封的，法院一般都会同意解封，之后可以依法支付工资。",
    "prediction": "建议您首先向公司了解账户冻结的具体原因，以及公司是否已经履行了承诺，并尝试与公司进行沟通。如果无法解决问题，您可以向当地劳动监察部门举报，维护自己的合法权益。同时，您还可以咨询专业的法律人士以获取更具体的帮助和建议。",
    "rouge_score": 12.658227403656838
  }
```

### **UltraRAG-KBAlign Case Study**

```JSON
  {
    "instruction": "请根据具体场景与问题给出法律依据，只需要给出具体法条内容，每个场景仅涉及一个法条。",
    "query": "场景:某市的工业园区内有两家工厂——A工厂和B工厂，二者相邻且在生产中存在潜在安全隐患。然而，这两家工厂并没有签订安全生产管理协议，也没有指定专职安全生产管理人员进行安全检查与协调。根据相关法律规定，这两家工厂会受到什么样的处罚？",
    "answer": "根据《安全生产法》的第一百零四条规定，两个以上生产经营单位在同一作业区域内进行可能危及对方安全生产的生产经营活动，未签订安全生产管理协议或者未指定专职安全生产管理人员进行安全检查与协调的，责令限期改正，处五万元以下的罚款，对其直接负责的主管人员和其他直接责任人员处一万元以下的罚款；逾期未改正的，责令停产停业。因此，A工厂和B工厂需要被责令限期改正并处以罚款，同时相关的主管人员和责任人员也将被处罚。",
    "prediction": "根据《中华人民共和国安全生产法》第一百零一条规定，两个以上生产经营单位在同一作业区域内进行可能危及对方安全生产的生产经营活动，未签订安全生产管理协议或者未指定专职安全生产管理人员进行安全检查与协调的，责令限期改正，可以处五万元以下的罚款，对其直接负责的主管人员和其他直接责任人员可以处一万元以下的罚款；逾期未改正的，责令停产停业。因此，A工厂和B工厂将受到罚款和停产停业的处罚。",
    "rouge_score": 91.08910841094011
  },
  {
    "instruction": "请根据具体场景与问题给出法律依据，只需要给出具体法条内容，每个场景仅涉及一个法条。",
    "query": "场景:农村土地承包经营纠纷调解仲裁案件中，申请人想要放弃之前提出的仲裁请求，被申请人想要提出反请求。根据哪条法律，申请人可以放弃或变更仲裁请求？被申请人有哪些权利？",
    "answer": "根据《农村土地承包经营纠纷调解仲裁法》第三十三条，申请人可以放弃或者变更仲裁请求。被申请人可以承认或者反驳仲裁请求，同时有权提出反请求。",
    "prediction": "《农村土地承包经营纠纷调解仲裁法》第三十三条：申请人可以放弃或者变更仲裁请求。被申请人可以承认或者反驳仲裁请求，有权提出反请求。",
    "rouge_score": 94.50549400603792
  },
```

### **UltraRAG-VisRAG Case Study**

![](../assets/en/visrag1.jpg)

![](../assets/en/visrag2.png)

We can see that, for the query "How can I charge my Tesla Model X?", VisRAG successfully retrieved the page in the car manual that explains how to charge the vehicle and correctly answered the question. Compared to VanillaRAG, it eliminates the cumbersome document parsing process, including OCR, and avoids information loss that can occur when parsing text-and-image mixed pages. This significantly improves end-to-end performance.

## Appendix：List of Knowledge Base Books

[List of Knowledge Base Books](../law_book_list.txt)
