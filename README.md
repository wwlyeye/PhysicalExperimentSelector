# 北京航空航天大学基物实验抢课辅助软件
#### Robbing machine for Physical Experiment Course of Beihang University
#### v2.1.1

## 该代码仅供学习交流，请勿真实使用 :warning:

## 特性
1. 自动定时抢课，可于睡觉前打开让电脑在12点自动抢课
2. 高频发包抢课，快人一步
3. 采用多次登录的方法，绕过网站排队限制，获得绝对优势

## 准备工作
在项目根目录下用`终端`/`cmd`下运行以下命令安装依赖

    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
    

## 使用说明：
1. 第一次运行`main.py`会生成一个配置文件`config.toml`。
2. 打开配置文件，配置账号信息，填写抢课目标。
3. 注册百度人工智能ocr，填写密钥。
4. 再次运行`main.py`。
5. 等到23:58:00程序会自动刷新账户状态保证登录有效。时间可以通过更改`main.py`的代码自定义。
6. 在23:59:59主程序运行开始抢课。
7. 若抢课成功或出现不可继续抢课的错误或超时则抢课进程会停止。

## OCR 说明
在 [BaiduAI](https://ai.baidu.com/tech/ocr) 注册账号，申请免费的通用文字识别。

**创建应用**后点击**管理应用**可以看到表头为AppID, API Key, Secret Key的表格，将这三个值填入配置文件的对应的位置。

## 其他
toml是一种新的方便阅读，方便编辑的配置文件类型，相对于json复杂的结构和严苛的格式，toml允许注释，更能够表达配置文件的层次。

虽然现在的配置文件还没有发挥toml的威力，但是对于以后的扩展性功能，相信它会发挥出威力的。
