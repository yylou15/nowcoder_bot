# 使用people准备
## 直接使用
- 把简历放到文件夹resumes/yyyy-mm-dd下
- 准备session
编辑文件people_cookie(如果没有，需要在根目录自己创建一个)，把浏览器中cookie复制过来
注意：需要打开people网址，在network中找到request header中的cookie
> 为什么不能用document.cookie? 因为有些cookie加了HTTPonly，JS是拿不到的

- 运行测试
```bash
./start_people.sh
```

## 自定义使用
- 编辑 examples/peopleBot_test.py
  例如：监控某一目录，只要有新增文件，就上传

# 使用bossbot
## 运行
- 先参照前面准备好people session
- 启动bossbot
```bash
./start_bot.sh
```
- 使用boss扫码(只有第一次登录需要，后续都会自动登录)

> 目前boss经常能发现IP、账号异常，最后每天把脚本停了去网页版boss中的“推荐牛人”看一眼，如果封禁，需要人工解禁

## 自定义
> 注意：一定要加过滤策略，否则简历质量太差，招聘HR工作量巨大，锤死你
- 修改“目标学校、公司”， 文件```examples/filters.py```
- 其他修改就随便自己修改代码吧……如果有好的策略可以提交上来共享

# 电脑总休眠？
```bash
caffeinate -t 36000
```

# 代码提交
修改好的策略可以在examples下随意提交新文件
对bot本身的提交，需要充分测试后提交