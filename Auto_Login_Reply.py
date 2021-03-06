#!/usr/bin/env python
#-*- coding:utf-8 -*-

__author__ = 'Sophie2805'

import re
import os.path

import requests
from bs4 import BeautifulSoup

import time
import os
import sys

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if log.txt does not exist under current executing path, create it.
write log, if the log file is larger than 100 lines, delete all then write from beginning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

file = os.path.abspath('.')+'/log.txt'#get the absolute path of .py executing
if not os.path.isfile(file):#not exist, create a new one
    f = open(file,'w')
    f.close()

if os.path.getsize(file)/1024 > 1024:#larger than 1MB
    f = open(file,'w')
    try:
        f.write('')
    finally:
        f.close()

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python Auto_Login_Reply.py user/pwd
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

args = sys.argv[1]
#print args
username = args[0:args.find('/')]
pwd = args[args.find('/')+1:len(args)]
#print username , pwd

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
using log_list[] to log the whole process
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

#print os.path.abspath('.')
log_list = []
log_list.append('+++++++++++++++++++++++++++++++++++++++++++++\n')
log_list.append('++++挖财签到有礼'+(time.strftime("%m.%d %T"))+' 每天签到得铜钱++++\n')
log_list.append('+++++++++++++++++++++++++++++++++++++++++++++\n')

s = requests.Session()

agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:38.0) Gecko/20100101 Firefox/38.0'
connection = 'keep-alive'

s.headers. update({'User-Agent':agent,
                   'Connection':connection})

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
post login request to this URL, observed in Firebug
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

login_url = 'https://www.wacai.com/user/user!login.action?cmd=null'

login_post_data ={
    'user.account':username,
    'user.pwd':pwd
}

try:
    login_r = s.post(login_url,login_post_data)
except Exception,e:
    log_list.append(time.strftime("%m.%d %T") + '--Login Exception: '+ e + '.\n')

f = open(file,'a')#append
try:
    f.writelines(log_list)
finally:
    f.close()
log_list=[]

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
these two get() are very import!!!
login_r.content return these 2 api URLs.
Without getting these 2 URLs, the BBS will not take our session as already login.
I assume, getting these 2 URLs, some critical cookie will be returned.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''

src1 = login_r.content[login_r.content.find('src')+5:login_r.content.find('"></script>')]
src2 = login_r.content[login_r.content.rfind('src')+5:login_r.content.rfind('"></script><script>')]
#print src1
#print src2
s.get(src1)
s.get(src2)

base_url = 'http://bbs.wacai.com/'
homepage_r = s.get(base_url)
if '我的挖财' in homepage_r.content:
    log_list.append(time.strftime("%m.%d %T") + '--Successfully login.\n')
#print homepage_r.content
'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
find the checkin forum URL and ID, which is used as fid parameter in the reply post URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
pattern = '<.+>签到有礼<.+>'
p = re.compile(pattern)
soup = BeautifulSoup(p.findall(homepage_r.content)[0])
checkin_postfix = soup.a['href']
checkin_forum_url = checkin_postfix
#print checkin_postfix
forum_id = checkin_postfix[checkin_postfix.find('-')+1:checkin_postfix.rfind('-')]
#print forum_id
if forum_id != '':
    log_list.append(time.strftime("%m.%d %T") + '--Successfully find the checkin forum ID.\n')
    print '--Successfully find the checkin forum ID'
    f = open(file,'a')#append
    try:
        f.writelines(log_list)
    finally:
        f.close()
    log_list=[]

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
get the checkin forum portal page and find today's thread URL and ID, which is used as tid parameter in the reply post URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
checkin_forum_page=s.get(checkin_forum_url)
#print checkin_forum_page.content
#print checkin_forum_page.status_code
title = '签到有礼'+(time.strftime("%m.%d")).lstrip('0')+'每天签到得铜钱，每人限回一次'
print title;
pattern_1 = '<.+>'+title + '<.+>'
p_1 = re.compile(pattern_1)
soup = BeautifulSoup(p_1.findall(checkin_forum_page.content)[0])
thread_postfix = soup.a['href']
thread_url = base_url + thread_postfix
thread_id= thread_postfix[thread_postfix.find('-')+1:thread_postfix.rfind('-')-2]
#print thread_id

if thread_id != '':
    log_list.append(time.strftime("%m.%d %T") + '--Successfully find the thread ID.\n')
    f = open(file,'a')#append
    try:
        f.writelines(log_list)
    finally:
        f.close()
    log_list=[]
t = s.get(thread_url)

'''~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
formhash is a must in the post data, observed in Firebug.
So get the formhash from the html of the page
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'''
pattern_2 = '<input type="hidden" name="formhash" .+/>'
p_2 = re.compile(pattern_2)
soup = BeautifulSoup(p_2.findall(t.content)[0])
formhash = soup.input['value']

pattern_3 = '回帖内容必须为'+'.+'+'</font>非此内容将收回铜钱奖励'
result_3 = re.compile(pattern_3).findall(t.content)
#print result_3
key = result_3[0][result_3[0].find('>')+1:result_3[0].rfind('<')-1]
if key != '':
    log_list.append(time.strftime("%m.%d %T") + '--Successfully find the key word.\n')
    f = open(file,'a')#append
    try:
        f.writelines(log_list)
    finally:
        f.close()
    log_list=[]

'''~~~~~~~
auto reply
~~~~~~~~~~'''

host='bbs.wacai.com'
s.headers.update({'Referer':thread_url})
s.headers.update({'Host':host})
reply_data={
    'formhash':formhash,
    'message':key,
    'subject':'',
    'usesig':''
}
reply_post_url = 'http://bbs.wacai.com/forum.php?mod=post&action=reply&fid='+forum_id+'&tid='+thread_id+'&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
try:
    reply_r = s.post(reply_post_url,data=reply_data)
except Exception,e:
    log_list.append(time.strftime("%m.%d %T") + '--Reply exception: '+ e +'.\n' )
if '非常感谢，回复发布成功，现在将转入主题页，请稍候……' in reply_r.content:#success
    log_list.append(time.strftime("%m.%d %T") + '--Successfully auto reply.\n')
else:
    log_list.append(time.strftime("%m.%d %T") + '--Fail to reply: '+ reply_r.content + '.\n')
f = open(file,'a')#append
try:
    f.writelines(log_list)
finally:
    f.close()
log_list=[]
'''~~~~~~~~~~~~~~
find my WaCai URL
~~~~~~~~~~~~~~~~~'''
pattern_4 = '<.+访问我的空间.+</a>'
p_4 = re.compile(pattern_4)
soup = BeautifulSoup(p_4.findall(t.content)[0])
if soup.a['href'] != '':
    log_list.append(time.strftime("%m.%d %T") + '--Successfully find my WaCai link.\n' )
    f = open(file,'a')#append
    try:
        f.writelines(log_list)
    finally:
        f.close()
    log_list=[]
mywacai_url = soup.a['href']
mywacai_page = s.get(mywacai_url)

'''~~~~~~~~~~~~~
find my info URL
~~~~~~~~~~~~~~~~'''
pattern_5 = '<.+个人资料</a>'
p_5 = re.compile(pattern_5)
soup = BeautifulSoup(p_5.findall(mywacai_page.content)[0])
if soup.a['href'] != '':
    log_list.append(time.strftime("%m.%d %T") + '--Successfully find my info link.\n' )
    f = open(file,'a')#append
    try:
        f.writelines(log_list)
    finally:
        f.close()
    log_list=[]
myinfo_url = base_url+ soup.a['href']
myinfo_page = s.get(myinfo_url)

'''~~~~~~~~~~~~~~
find my coin info
~~~~~~~~~~~~~~~~~'''
pattern_6 = '<em>铜钱.+\n.+\n'
p_6 = re.compile(pattern_6)
coin = p_6.findall(myinfo_page.content)[0]
coin = coin[coin.find('</em>')+5:coin.find('</li>')]
if int(coin.strip()) != 0:
    log_list.append(time.strftime("%m.%d %T") + '--Successfully get my coin amount: %s.\n'% int(coin.strip()))
    f = open(file,'a')#append
    try:
        f.writelines(log_list)
    finally:
        f.close()
    log_list=[]
