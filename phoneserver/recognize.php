<?php
    // function curl_file_create($filename, $mimetype = '', $postname = '') {
        // return "@$filename;filename="
            // . ($postname ?: basename($filename))
            // . ($mimetype ? ";type=$mimetype" : '');
    // }
    
$key = "b3a7cba8-c45d-465b-8e9a-adaccff0a70c";
$file = $argv[0];
$min = 0;
$max = 30;
$count = 64;
$result=array();
if($min>$max) return $result;
$count=min(max($count,0),$max-$min+1);
while(count($result)<$count) {
    $value=rand($min,$max-count($result));
    foreach($result as $used) if($used<=$value) $value++; else break;
    $result[]=dechex($value);
    sort($result);
}
shuffle($result);
$uuid = $result;
$uuid=implode($uuid);    $uuid=substr($uuid,1,32);
$curl = curl_init();
$url = 'https://asr.yandex.net/asr_xml?'.http_build_query(array(
    'key'=>$key,
    'uuid' => $uuid,
    'topic' => 'notes',
    'lang'=>'ru-RU'
));
curl_setopt($curl, CURLOPT_URL, $url);
$data=file_get_contents(realpath($file));
curl_setopt($curl, CURLOPT_POST, true);
curl_setopt($curl, CURLOPT_POSTFIELDS, $data);
curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($curl, CURLOPT_SSL_VERIFYPEER, 0);
curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($curl, CURLOPT_HTTPHEADER, array('Content-Type: audio/x-wav'));
curl_setopt($curl, CURLOPT_VERBOSE, true);
$response = curl_exec($curl);
$err = curl_errno($curl);
curl_close($curl);
if ($err)
    throw new exception("curl err $err");
echo $response;