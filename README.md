# 准备
编辑文件people_cookie，把浏览器中cookie复制过来
注意：需要打开people网址，在network中找到request header中的cookie
> 为什么不能用document.cookie? 因为有些cookie加了HTTPonly，JS是拿不到的

# 运行
```bash
./start_people.sh
```

# 电脑总休眠？

```bash
caffeinate -t 36000
```