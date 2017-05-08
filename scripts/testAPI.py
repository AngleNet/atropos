
import Spider.utils
import requests
import re
if __name__ == '__main__':
    content = '{"code":"100000","msg":"","data":{"html":" <a target=\"_blank\" render=\"ext\" suda-uatrack=\"key=topic_click&value=click_topic\" class=\"a_topic\" extra-data=\"type=topic\" href=\"http:\/\/huati.weibo.com\/k\/%E6%9D%8E%E6%98%93%E5%B3%B0?from=501\">#\u674e\u6613\u5cf0#<\/a><a target=\"_blank\" render=\"ext\" suda-uatrack=\"key=topic_click&value=click_topic\" class=\"a_topic\" extra-data=\"type=topic\" href=\"http:\/\/huati.weibo.com\/k\/%E7%A5%9D%E6%9D%8E%E6%98%93%E5%B3%B00504%E7%94%9F%E6%97%A5%E5%BF%AB%E4%B9%90?from=501\">#\u795d\u674e\u6613\u5cf00504\u751f\u65e5\u5feb\u4e50#<\/a> <br>\u8bb0\u5fc6\u7684\u7a97\u666f&nbsp;&nbsp;\u65f6\u95f4\u505c\u5728\u54ea\u91cc\r\u5fd8\u4e86\u90a3\u4e9b\u61a7\u61ac \u8bb0\u5f97\u6211\u7231\u4f60\r\u9065\u8fdc\u7684\u56de\u5fc6\u90a3\u4e48\u8fd1\r\u4e89\u5435\u7684\u60c5\u7eea\u592a\u5b89\u9759\r\u4f60\u8fd8\u662f\u6211\u6700\u820d\u4e0d\u5f97\u7684\u66fe\u7ecf\r\u4f24\u5fc3\u662f\u4e00\u5c01\u5bc4\u7ed9\u9752\u6625\u7684\u4fe1<br><img render=\"ext\" src=\"http:\/\/img.t.sinajs.cn\/t4\/appstyle\/expression\/ext\/normal\/df\/lxhxiudada_org.gif\" title=\"[\u7f9e\u55d2\u55d2]\" alt=    \"[\u7f9e\u55d2\u55d2]\" type=\"face\" \/><img render=\"ext\" src=\"http:\/\/img.t.sinajs.cn\/t4\/appstyle\/expression\/ext\/normal\/df\/lxhxiudada_org.gif\" title=\"[\u7f9e\u55d2\u55d2]\" alt=    \"[\u7f9e\u55d2\u55d2]\" type=\"face\" \/>\u54e5\u54e5\u751f\u65e5\u5feb\u4e50<a target=\"_blank\" render=\"ext\" extra-data=\"type=atname\" href=\"http:\/\/weibo.com\/n\/%E6%9D%8E%E6%98%93%E5%B3%B0?from=feed&loc=at\" usercard=\"name=\u674e\u6613\u5cf0\">@\u674e\u6613\u5cf0<\/a> <br><a target=\"_blank\" render=\"ext\" suda-uatrack=\"key=topic_click&value=click_topic\" class=\"a_topic\" extra-data=\"type=topic\" href=\"http:\/\/huati.weibo.com\/k\/%E9%99%AA%E6%9D%8E%E6%98%93%E5%B3%B0%E7%BB%A7%E7%BB%AD%E4%B8%80%E8%B5%B7%E8%B5%B0?from=501\">#\u966a\u674e\u6613\u5cf0\u7ee7\u7eed\u4e00\u8d77\u8d70#<\/a> <br>\u3010ps\uff1a\u7a81\u7136\u8fd4\u573a\u7684\u54e5\u54e5\u592a\u6696\u4e86 \u592a\u7a81\u7136\u6240\u4ee5\u524d\u9762\u6ca1\u6709\u5f55\u5168 \u89c6\u9891\u7981\u4e00\u5207<img render=\"ext\" src=\"http:\/\/img.t.sinajs.cn\/t4\/appstyle\/expression\/ext\/normal\/4a\/mm_org.gif\" title=\"[\u55b5\u55b5]\" alt=    \"[\u55b5\u55b5]\" type=\"face\" \/>\u3011<br><a  suda-uatrack=\"key=tblog_card&value=click_title:4103001491331907:2017607-video:2017607%3A4302e96cff83a09f81a2157ffa216a73:weibodetail:5263604497:4103001491331907:5263604497\" title=\"\u6276\u82cf\u53ef\u5165\u836f\u7684\u79d2\u62cd\u89c6\u9891\" href=\"http:\/\/t.cn\/RavHCpK\" alt=\"http:\/\/t.cn\/RavHCpK\" action-type=\"feed_list_url\" target=\"_blank\" ><i class=\"W_ficon ficon_cd_video\">L<\/i>\u6276\u82cf\u53ef\u5165\u836f\u7684\u79d2\u62cd\u89c6\u9891<\/a>"}}'
    content = Spider.utils.strip(content)

    Spider.utils.loadSUB('../data/.sub')
    link = 'http://www.weibo.com/p/aj/mblog/getlongtext?ajwvr=6&mid=4103001491331907'
    ret = requests.get(link, headers = Spider.utils.Config.HTML_HEADERS)
    text = ret.text
    text = re.sub(r'\\n', '', text)
    text = re.sub(r'\\r', '', text)
    text = re.sub(r'\\t', '', text)
    text  = text[5:-13]


