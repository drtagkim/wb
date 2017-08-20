from browser.scrap import *
from bs4.element import Tag
from bs4 import BeautifulSoup as BS
import pandas as pd
from threading import Thread
import hashlib
import uuid
import re
from itertools import chain
from collections import defaultdict
from excel.excelutil import ExcelOutput

reg_number=re.compile(r"[0-9,]+")
class WbItem:
    css_item="div[action-type='feed_list_item']"
    @classmethod
    def collect(cls,selector):
        try:
            rv1=selector.select(WbItem.css_item)
            mid=[i['mid'] for i in rv1]
        except:
            rv1=[]
            mid=[]
        return (mid,rv1)
class WbFace:
    css_item_face=".face a"
    css_item_face_pic=".face img"
    def __init__(self,wbItem):
        self.item=wbItem
        face=wbItem.select_one(WbFace.css_item_face)
        self.face_url=face['href']
        self.face_title=face['title']
        face=wbItem.select_one(WbFace.css_item_face_pic)
        self.face_pic_url=face['src']
        self.face_pic_alt=face['alt']
        self.face_pic_usercard=face['usercard']
class WbContent:
    css_item_content=".content"
    css_item_content_context=".W_texta.W_fb"
    css_item_content_iconApproved=".icon_approve"
    css_item_content_commentText=".comment_txt"
    css_item_content_media=".media_box img"
    css_item_content_feed_date=".feed_from a.W_textb"
    css_item_content_taobao=".ico_taobao"
    css_item_content_verified="[href='http://verified.weibo.com/verify']"
    def __init__(self,wbItem):
        self.item=wbItem
        content=wbItem.select_one(WbContent.css_item_content)
        content_context = content.select_one(WbContent.css_item_content_context)
        if not (content_context is None):
            self.context_nickName=content_context['nick-name']
            self.context_href=content_context['href']
            self.context_usercard=content_context['usercard']
        content_iconTaobao=content.select_one(WbContent.css_item_content_taobao)
        try:
            self.icon_taobao=content_iconTaobao['title']
        except:
            self.icon_taobao="NA"
        try:
            self.comment_text=content.select_one(WbContent.css_item_content_commentText).text
        except:
            self.comment_text=""
        try:
            imgs=content.select(WbContent.css_item_content_media)
            self.img_count=len(imgs)
            self.img_urls=str([i['src'] for i in imgs])
        except:
            self.img_count=0
            self.img_urls="[]"
        content_feed=content.select_one(WbContent.css_item_content_feed_date)
        try:
            self.date_title=content_feed['title']
            self.date_num=content_feed['date']
        except:
            self.date_title="NA"
            self.date_num="NA"
        try:
            markers=content.select(WbContent.css_item_content_verified)
            self.markers=str([m['alt'] for m in markers])
        except:
            self.markers="[]"
class WbFeed:
    css_item_feedAction=".feed_action_info"
    css_item_feedAction_line="li a"
    def __init__(self,wbItem):
        self.wbItem=wbItem
        feed=wbItem.select_one(WbFeed.css_item_feedAction)
        feedlines=feed.select(WbFeed.css_item_feedAction_line)
        self.action={}
        for line in feedlines:
            try:
                self.action[line['action-type']]=reg_number.findall(line.text)[0].strip()
            except:
                self.action['feed_list_favorite']='0'
                self.action['feed_list_forward']='0'
                self.action['feed_list_comment']='0'
                self.action['feed_list_like']='0'
class Collector:
    def __init__(self,fname):
        self.df=pd.DataFrame()
        with open(fname,encoding='utf-8') as f:
            self.page=BS(f,'lxml')
    def run(self):
        page=self.page
        mid,items=WbItem.collect(page)
        faces=[WbFace(item) for item in items]
        contents=[WbContent(item) for item in items]
        feeds=[WbFeed(item) for item in items]
        assert len(mid)==len(faces)==len(contents)==len(feeds),"Data incomplete"
        face_url=[i.face_url for i in faces]
        face_title=[i.face_title for i in faces]
        face_pic_url=[i.face_pic_url for i in faces]
        face_pic_alt=[i.face_pic_alt for i in faces]
        face_pic_usercard=[i.face_pic_usercard for i in faces]
        content_nickname=[i.context_nickName for i in contents]
        content_href=[i.context_href for i in contents]
        content_usercard=[i.context_usercard for i in contents]
        content_icon_taobao=[i.icon_taobao for i in contents]
        content_comment_text=[i.comment_text for i in contents]
        content_img_count=[i.img_count for i in contents]
        content_img_urls=[i.img_urls for i in contents]
        content_date_title=[i.date_title for i in contents]
        content_date_num=[i.date_num for i in contents]
        content_markers=[i.markers for i in contents]
        feed_data=defaultdict(list)
        for feed in feeds:
            for k,v in feed.action.items():
                feed_data[k].append(v)
        self.df['face_url']=face_url
        self.df['face_title']=face_title
        self.df['face_pic_url']=face_pic_url
        self.df['face_pic_alt']=face_pic_alt
        self.df['face_pic_usercard']=face_pic_usercard
        self.df['content_nickname']=content_nickname
        self.df['content_href']=content_href
        self.df['content_usercard']=content_usercard
        self.df['content_icon_taobao']=content_icon_taobao
        self.df['content_comment_text']=content_comment_text
        self.df['content_img_count']=content_img_count
        self.df['content_img_urls']=content_img_urls
        self.df['content_date_title']=content_date_title
        self.df['content_date_num']=content_date_num
        self.df['content_markers']=content_markers
        for k in feed_data.keys():
            self.df[k]=feed_data[k]
    def toExcel(self,fname):
        ExcelOutput.export(fname,['weibo',],[self.df,])