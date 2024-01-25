AUTO_snap

该文件夹中包含autosnap.py的根据相应sdk进行自动拍摄配对数据集以及进行参数计算校正的程序

同时有基本的qt图形界面框架，以及对图片噪声分析的analyse程序



PMN-TPAMI

SNA的参数采样使用 在```data_process/process.py```中的   `SNA_torch`函数实现
完整的SNA的 GPU 版本在 ```trainer_SID.py```的  `preprocess` 函数中

```merge_GT.py```用于对齐后图片的多帧融合，获取干净图片

```noise_estimation.py``` 用于评估计算图片的噪声参数和噪声情况

图片原始数据采用dwg的raw图格式，参数存储方式采用序列化pkl

暗影校正和噪声校正都需要大量的暗场图像。这里直接提供了校正结果。暗影校正的结果存储在 `resources` 文件夹中。每个 ISO 下的原始噪声参数存储在 `process.py` 中的 `get_camera_noisy_params_max` 函数里，可以根据噪声模型（P-G 或 ELD）来校正噪声参数。具体的数据集组成和使用方法见其内作者提供的说明。

