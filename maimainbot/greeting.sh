
$cookie= `cat .maimai_cookie`
greet(){
  curl "https://maimai.cn/api/ent/right/direct/contact/enable?channel=www&fr=talentDiscover&jid=2949982&to_uid=$1&version=1.0.0" \
  -H 'authority: maimai.cn' \
  -H 'pragma: no-cache' \
  -H 'cache-control: no-cache' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36' \
  -H 'x-csrf-token: mIzZ3AMr-PEaNT5O4Fo3qjA6imGb_gMn2Wos' \
  -H 'accept: */*' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-mode: same-origin' \
  -H 'sec-fetch-dest: empty' \
  -H 'referer: https://maimai.cn/ent/talents/discover/search_v2/' \
  -H 'accept-language: zh,zh-CN;q=0.9,en;q=0.8' \
  -H "cookie: $cookie" \
  --compressed
}

for id in `cat test | python3 -mjson.tool | grep -E '"id"|direct_contact_st|recent_dc_chat' | paste  - - - | grep '"direct_contact_st": 1' | grep '"recent_dc_chat": 0' | awk -F ':|,' '{print $2}'`
do 
  echo "====== $id ======="
  greet "$id"
  sleep 10s
done