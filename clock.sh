# 定时脚本
set +e
# 1. 计算站点当日访问量数据

cd `dirname $0`

source /root/anaconda3/bin/activate flask

# 2. 爬取 CSDN 数据
scrapy crawl csdn_spider

# 3. 爬取掘金数据
python juejin_spider.py