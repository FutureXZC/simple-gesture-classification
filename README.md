# 简单手势识别（图形三分类）Simple Gesture Recognition (Graph three classification)

本项目训练一个用于支持手势识别的三分类模型，模型将用于地平线的开发板上，为下游任务服务。具体的，利用草图图形数据训练一个三分类模型（识别圆形、方形和三角形），三种不同的图形分别代表三种不同的手势。利用摄像机获取的位点数据将拼接为连续的曲线，每个曲线组成一个图形，将该图形输入本项目所得的模型，即可得到识别结果。根据识别结果，对应系统的不同指令。  

This project trains a four-classification model to support gesture recognition, which will be used on the Horizon development board for downstream tasks. Specifically, a four-category model (recognizing rectangles, squares, circles and triangles) was trained using sketch graph data, and four different shapes represented four different gestures respectively. The site data obtained by the camera will be spliced into continuous curves, and each curve will form a graph. The graph will be input into the model obtained by this project to obtain the recognition result. According to the identification results, corresponding to the different instructions of the system.

## 数据集 Dataset

数据集使用自构建的草图图形数据，包含1995个圆形、1969个方形和1978个三角形，训练集和测试集的划分比例为7 : 3。  

若您对本项目所使用的数据集感兴趣，可在issue中留下您的联系方式。  

The dataset used self-constructed sketch graph data, including 201 circles, 200 triangles, 200 squares and 799 triangles, and the partition ratio of training set and test set was 7:3.  

If you are interested in the data set used in this project, you can leave your contact information in the issue.

## 训练环境 Environment

- GPU: Tesla V100
- CUDA Version: 10.2
- PyTorch 1.9.0, torchvision 0.10.0

## 单文件测试 Single image test

```
sh test.sh
```

## 模型训练 Model training

```
python trainner.py
```

## 开发指南

- [+] : 添加一个新功能 (Add a new feature)

- [!] : 修复bug (Bug fix)

- [*] : 常规修改 (General adjustments and changes)

