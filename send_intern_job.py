import markdown

from nowcoderbot import post_header
from nowcoderbot.login.NCPasswordLogin import NCPasswordLogin


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
    session = NCPasswordLogin("******", "******").do()
    process_post(session)
