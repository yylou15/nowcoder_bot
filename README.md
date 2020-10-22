# 直接使用
- 把简历放到文件夹resumes/yyyy-mm-dd下
- 准备session
编辑文件people_cookie，把浏览器中cookie复制过来
注意：需要打开people网址，在network中找到request header中的cookie
> 为什么不能用document.cookie? 因为有些cookie加了HTTPonly，JS是拿不到的

- 运行
```bash
./start_people.sh
```

# 自定义使用
- 编辑 examples/peopleBot_test.py
  例如：监控某一目录，只要有新增文件，就上传


# 电脑总休眠？
```bash
caffeinate -t 36000
```

# 代码提交
修改好的策略可以在examples下随意提交新文件
对bot本身的提交，需要充分测试后提交