import urllib.request
re=urllib.request.Request("http://www.weibo.com")
dd=urllib.request.urlopen(re)
print(dd.read().decode("utf-8"))