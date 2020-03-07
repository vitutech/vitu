Intro
=========

vitu开源策略框架初版已经发布，请访问官网了解和查询相关信息！https://vitu.ai

Vitu.AI是实现数字资产科学投资从数据采集，清洗加工到量化研究，策略回测乃至实盘交易的一个专业科学投资服务平台，满足对区块链在数据获取，量化研究和交易方面的需求，特点是数据覆盖范围广，量化策略与交易框架专业且易懂，使用简洁方便

欢迎关注扫描Vitu的微信公众号“Vitu”,更多原创文章与信息与您分享，敬请期待

Dependencies
=========
python 3.x

pandas

numpy

Installation
====
-方式1：pip install vitu

-方式2：访问 https://github.com/vitutech/vitu 下载安装

Quick Start
======
1 策略教程：在https://vitu.ai 上注册，《等你来学》栏目中查找教程[策略框架【Vitu开源给你看】](https://vitu.ai/course/105231114968286336)，其中包含数据下载和策略编辑方法

2 如何回测：

(1)若按照方式1中直接安装vitu的,则可按照策略教程直接编辑策略进行回测;
	
(2)若按照方式2 下载安装，则可选择下面两种方式之一进行策略回测：

-在cmd（或Anaconda PowerShell Prompt）中，cd 文件目录地址（即setup.py所在的文件夹目录），enter, 再运行python setup.py install 完成vitu的安装，则可按照策略教程直接编辑策略进行回测。

-或者直接设置系统的环境变量，将文件目录地址（即setup.py所在的文件夹目录）加入到PYTHONPATH中，然后在此文件目录中直接按照教程编辑策略进行回测。

3 策略编辑：参照vitu策略教程，以demo.py为策略操作样本，可按照demo中的模板输入相关信息（账户信息，回测品种，数量，时间，交易条件，交易费用等），完成策略的回测 