<?php
   
class ScgiClient
{
    const TRY_CONNECT_TIMES = 3;
    
    /**
     * call 魔术方法
     *
     * 用于调用 scgi server 的某个任务, 例如调用 image 服务的 resize 服务： 
     * $client->resize('width=100&height=100', $imgData)
     *
     * 当 scgi server 只有一个任务的时候则调用 do 方法，例如：
     * $client->do('to=somebody@gmail.com&body=hello');
     *
     * @param string $fun  调用的方法名称
     * @param array  $args 参数
     *
     * @return void
     * @author Weber Liu
     */
    public static function __callStatic($fun, array $args=array())
    {

        $arguments = array(
            $args[0],
            'request' == $fun ? '' : $fun, 
            isset($args[1]) ? $args[1] : '', 
            isset($args[2]) ? $args[2] : ''
        );

        return call_user_func_array(
            array(__CLASS__, '_request'),
            $arguments
        );
    }

    /**
     * 连接到 scgi server
     *
     * @param string $host scgi server host
     *
     * @return ScgiClient
     * @author Weber Liu
     */
    private static function _connect($host)
    {
        static $times = 0;
        
        $arr = explode(',', $host);
        $hosts = array();
        
        foreach ($arr as $key => $val) {
            $tmp = parse_url($val);
            $hosts[] = array('host' => $tmp['host'], 'port' => $tmp['port']);
        }
        
        $server = $hosts[array_rand($hosts)];

        try {
            $fp = fsockopen($server['host'], $server['port'], $errno, $errstr, 3);
        } catch (ErrorException $e) {
            if ($times < self::TRY_CONNECT_TIMES) {
                $times ++;
                self::connect();
            } else {
                $times = 0;
                throw new Exception('Connect to SCGI Server ' . implode(':', $server) . ' is failed');
            }
        }

        if (false == $fp) {
            throw new Exception('Cannot connect to scgi server.');
        }
        
        $times = 0;
        
        return $fp;
    }

    /**
     * 向 scgi server 发送一个请求
     *
     * @param string $host        scgi server host
     * @param string $job         任务名称
     * @param string $queryString 参数, 如 pid=1&spec=2
     * @param string $data        数据
     *
     * @return void
     * @author Weber Liu
     */
    private static function _request($host, $job='', $queryString='', $data='')
    {
        $fp = self::_connect($host);
        
        $format   = "%s\x00%s\x00";
        $headers  = sprintf($format, 'CONTENT_LENGTH', strlen($data));
        $headers .= sprintf($format, 'SCRIPT_NAME', $job);
        $headers .= sprintf($format, 'QUERY_STRING', $queryString);
        $packet   = strlen($headers) . ':' . $headers . ',' . $data;

        try {
            fwrite($fp, $packet);
            $data = stream_get_contents($fp);
            if (empty($data)) {
                throw new Exception("empty response");
            }

            list($statusCode, $response) = explode("\x00", $data, 2);
        } catch (Exception $e) {
            fclose($fp);
            throw new Exception('Occured IO exception: ' . $e);
        }

        fclose($fp);
                
        if (0 == $statusCode) {
            throw new Exception('[SCGI] ' . $response);
        }
        
        return $response;
    }
} // END class ScgiClient   


    
$scgi = ScgiClient::captcha('scgi://10.211.55.5:4302', http_build_query(['imageFormat' => 'PNG', 'width' => 100, 'height' => 80, 'text' => 'zhan']));
echo ($scgi);
