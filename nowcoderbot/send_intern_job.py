import markdown
from login.NCPasswordLogin import NCPasswordLogin


captcha_headers = {
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,zh;q=0.8,zh-CN;q=0.7",
    "Connection": "keep-alive",
    "Host": "hr.nowcoder.com",
    "Referer": "https://hr.nowcoder.com/login-more",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

login_headers = {
    "Accept": "text/plain, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,zh;q=0.8,zh-CN;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "hr.nowcoder.com",
    "Origin": "https://hr.nowcoder.com",
    "Referer": "https://hr.nowcoder.com/login-more",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

post_header = {
    "Accept": "text/plain, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,zh;q=0.8,zh-CN;q=0.7",
    "Connection": "keep-alive",
    "Content-Length": "98",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.nowcoder.com",
    "Origin": "https://www.nowcoder.com",
    "Referer": "https://www.nowcoder.com/discuss/v2/post?type=0",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

def process_post(session):
    with open(r'post/intern.md', 'r') as f:
        print(session.post("https://www.nowcoder.com/discuss/create?token=", headers=post_header, data={
            "title": "字节跳动实习生内推",
            "content": markdown.markdown(f.read()),
            "mdContent": "",
            "contentType": "1",
            "type": "7",
            "tags": "861, 827",
            "timed": "NaN",
            "subjectIds": "265",
            "hasSubject": "true",
        }).text)



if __name__ == '__main__':
    session = NCPasswordLogin("15257114998", "lou743851").do()
    process_post(session)