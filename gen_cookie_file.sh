echo '# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

'

cookie_item='.bytedance.net  TRUE	/ FALSE	3748933332'

cat people_cookie | awk 'BEGIN{RS="; "} {print}'| grep -v 'people-fe'| awk -F '=' '{print ".bytedance.net	TRUE	/	FALSE	3748933332	" $1 "	" $2}'