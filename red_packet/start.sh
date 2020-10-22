SHELL_FOLDER=$(dirname "$0")
echo "run in $SHELL_FOLDER" 
cookie=`cat $SHELL_FOLDER/../people_cookie`

for data in `grep 'https://people.bytedance.net/atsx/activity/redEnvelope'  $SHELL_FOLDER/messages | awk -F 'redEnvelope' '{print $2}' | awk -F '/' '{print "{\"red_packet_id\":\"" $2 "\",\"sign\":\"" $3 "\"}" }'`
do
  echo "${data}"

  curl 'https://people.bytedance.net/atsx/api/referral/redpacket/obtain' \
    -H 'authority: people.bytedance.net' \
    -H 'pragma: no-cache' \
    -H 'cache-control: no-cache' \
    -H 'accept: application/json, text/plain, */*' \
    -H 'x-csrf-token: 1C8zdSh-ziQ9qSg3Hwcz1k_ilGEOKKIPLNBQw3O2hiQ' \
    -H 'accept-language: zh-CN' \
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36' \
    -H 'content-type: application/json' \
    -H 'origin: https://people.bytedance.net' \
    -H 'sec-fetch-site: same-origin' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-dest: empty' \
    -H 'referer: https://people.bytedance.net/hire/activity/redEnvelope/6883118723311569166/2b48628684520c83a46591958ae2d92b5f1b0c28' \
    -H "cookie: ${cookie}" \
    --data-binary "${data}" \
    --compressed
    #--data-binary '{"red_packet_id":"6883720000348588296","sign":"ba50e5daeadb0eb72774c39345bd913e896fbed1"}' \
  sleep 2s
done 
