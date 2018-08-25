from scrapy import Request
from scrapy.selector import HtmlXPathSelector

# htm = HtmlXPathSelector()
htm = Request("https://www.ijcai.org/proceedings/2018/")
print(htm)
