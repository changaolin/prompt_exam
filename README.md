# 环境准备
![环境准备](res/image.png)
## 创建python虚拟环境
```bash
python -m venv venv
```
## 激活虚拟环境
```bash
source venv/bin/activate
```
## 安装依赖
```bash
pip install -r requirements.txt
```
# 使用
## 启动服务
```bash
python run.py
```
![启动服务](res/image1.png)
## 访问服务
```bash
http://localhost:5001/
```
![访问服务](res/image2.png)
### 上传题库
![上传题库](res/image3.png)
![保存题库](res/image4.png)
### 生成试卷
![生成试卷](res/image5.png)
### 开始考试
![开始考试](res/image6.png)
### 查看成绩
![查看成绩](res/image7.png)
- 单选题每题 2分
- 多选题每题 4分
- 简答题每题 0分