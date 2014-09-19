#!/usr/bin/python
#-*- coding:utf-8 -*-
#author:chen-123
#抓取九江搜房网成交数据

import time
import urllib2
import StringIO
import gzip
import string
import sys,os
import chardet
from bs4 import BeautifulSoup
import re
#from BeautifulSoup import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')

def getlist(html):
        #soup = BeautifulSoup(html,fromEncoding="utf-8")
	soup = BeautifulSoup(html)
	#print type(soup)
        #print soup.originalEncoding
        #print soup.prettify()
        divs = soup.find_all('div',{'class':'searchListNoraml'})

        for div_html in divs:
                company_li=div_html.findAll("li",{'class':'s2'})
                price_div=div_html.findAll("div",{'class':'price'})
                img_tmp=div_html.findAll("img",width='122')
                name_div=div_html.findAll("div",{'class':'name'})
                type_div=div_html.findAll("div",{'class':'dot6'})
		if (company_li):
			print "===============分割线========================"
                	print "["+img_tmp[0].get("alt")+"]-----["+img_tmp[0].get("src")+"]----["+price_div[0].get_text().strip()+"]"+type_div[0].get_text().strip()
                	print "[http://newhouse.jiujiang.soufun.com"+company_li[0].a.get('href')+"]----["+company_li[1].font.string+']'
                	print "["+name_div[0].a.string+"]的网址："+name_div[0].a.get('href')

def getHtml(url):
	headers={'User-Agent':'Opera/8.0 (Macintosh; PPC Mac OS X; U; en)'}
	opener = urllib2.build_opener()
	request = urllib2.Request(url,headers=headers)
	request.add_header('Accept-encodeing','gzip')
	page = opener.open(request)
	predata = page.read()
	pdata = StringIO.StringIO(predata)
	gzipper = gzip.GzipFile(fileobj = pdata)
	try:
		data = gzipper.read()
	except(IOError):
		print 'unused gzip'
		data = predata

	mychar=chardet.detect(data)
	#print mychar
	bianma = mychar['encoding']
	if bianma == 'utf-8' or bianma == 'UTF-8':
		html = data
	else :
		html = data.decode('gb2312','ignore').encode('utf-8')
	return html

def getSouFun_NewHouseList():
	for i in range(1,19,1):
		url_tmp="http://newhouse.jiujiang.soufun.com/house/%BE%C5%BD%AD_________________"+str(i)+"__.htm"
		#print url_tmp
		tags_html=getHtml(url_tmp)
		time.sleep(2)
		getlist(tags_html)

def getSouFun_everydayTrace():
	print '<html xmlns=\"http://www.w3.org/1999/xhtml\">'
	print '<head>'
	print '<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\" />'
	print '<title>九江城区--成交情况统计</title>'
	print '<body>'
	for i in range(1,13):
		list_url="http://newhouse.jiujiang.soufun.com/house/web/newhouse_news_more.php?type=12193&page="+str(i)
		list_html=getHtml(list_url)

		soup = BeautifulSoup(list_html,from_encoding="utf-8")
        	divs = soup.find_all('div',{'class':'lnews'})

		#print divs	
        	for div_html in divs:
			#print div_html
			li_tracelist=div_html.findAll("li",{'class':''})
		for lit in li_tracelist:
			pattern_href=re.compile(r'10933990|10338408|10141539|10228006|10132539')
			match_href=pattern_href.findall(lit.a.get('href'))
			if (not match_href):
				print "<p>[<a href='http://newhouse.jiujiang.soufun.com"+lit.a.get('href').replace('.','_all.')+"' >"+lit.a.string+"平方米</a>]的链接:http://newhouse.jiujiang.soufun.com"+lit.a.get('href').replace('.','_all.')+"</p>"
				print "<br/>"
				getSouFun_trace_Data("http://newhouse.jiujiang.soufun.com"+lit.a.get('href').replace('.','_all.'))
				time.sleep(5)
	print "</body></html>"

def getSouFun_trace_Data(url):
	data_html = getHtml(url)
	#re_iframe = re.compile(r'<iframe[^>]*>[^<]*</iframe>')
	#new_data_html = re_iframe.sub('',data_html)
	#new_data_html = filter_tags(data_html)
	#print new_data_html
	soup = BeautifulSoup(data_html,from_encoding="utf-8")

	#print soup
	divs = soup.find_all('div',{'name':'news_content'})
	if (not divs):
		divs = soup.find_all('div',{'id':'news_body'})

	#print divs
	for div_html in divs:
		table_list=div_html.findAll('table',{'class':''})
		#table_list=div_html.find('table')
		if(table_list):
			for table_html in table_list:
				print table_html
				print "<br/>"
		print "<br/>"

		img_list=div_html.find_all('img')
		#print div_html.img
		#img_list=""
		#img_list=div_html.findAll(name='img',attrs={'src',re.compile(r"(.*)news(.*).jpg")})
		if(img_list):
			for img_html in img_list:
				pattern = re.compile(r'viewimage|qrcode')
                        	match = pattern.findall(img_html.get('src'))
				if (not match):
					print img_html
					print "<br/>"
		print "<br/>"

def filter_tags(htmlstr):
	#先过滤CDATA
    	re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    	re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
	re_iframe=re.compile('<\s*iframe[^>]*>[^<]*<\s*/\s*iframe\s*>',re.I)#iframe
    	re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    	#re_h=re.compile('</?\w+[^>]*>')#HTML标签
    	re_comment=re.compile('<!--[^>]*-->')#HTML注释
    	s=re_cdata.sub('',htmlstr)#去掉CDATA
    	s=re_script.sub('',s) #去掉SCRIPT
	s=re_iframe.sub('',s) #去掉iframe
    	s=re_style.sub('',s)#去掉style
    	#s=re_h.sub('',s) #去掉HTML 标签
    	s=re_comment.sub('',s)#去掉HTML注释
    	#去掉多余的空行
    	return s

getSouFun_everydayTrace()
