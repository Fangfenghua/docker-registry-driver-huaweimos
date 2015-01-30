#coding=UTF-8
'''
Created on 2012-9-29

@author: s00228753
'''

import xml.etree.ElementTree as ET

from src.com.hws.s3.models.bucket import Bucket
from src.com.hws.s3.models.owner import Owner
from src.com.hws.s3.utils.utils import Utils


#罗列存储空间方法返回对象，可解析返回的XML为S3存储空间
class ListBucketsResponse(object):
    
    def __init__(self, entries, owner):       
    
        self.entries = entries
        self.owner = owner
            
    #===========================================================================
    # 定义静态方法，用来解析xml，最后返回ListBucketResponse对象
    #===========================================================================
    @staticmethod
    def list_parse_factory(xml):
        
        if xml is not None: 
            entries = ListAllMyBuckets.parse_buckets(xml)
            owner = ListAllMyBuckets.parse_owner(xml)
 
            return ListBucketsResponse(entries, owner)   #返回ListBucketsResponse的对象
   

#===============================================================================
# 该类用于封装解析xml文件，生成Owner和Entries
#===============================================================================
class ListAllMyBuckets:

    NS = '{http://s3.amazonaws.com/doc/2006-03-01/}'  #xml的命名空间
            
    #===========================================================================
    # 获取owner对象
    #===========================================================================
    @staticmethod
    def parse_owner(xml):
        
        root = ET.fromstring(xml) #获取xml文件的根节点root
        owner_id = root.find('.//{0}ID'.format(ListAllMyBuckets.NS)).text      
        owner_name = root.find('.//{0}DisplayName'.format(ListAllMyBuckets.NS)).text   
        owner = Owner(owner_id, owner_name)  #创建Owner对象
        
        return owner
     
    #===========================================================================
    # 获取bucket的列表
    #===========================================================================
    @staticmethod
    def parse_buckets(xml):
        
        root = ET.fromstring(xml)
        buckets = root.find('{0}Buckets'.format(ListAllMyBuckets.NS)).findall('{0}Bucket'.format(ListAllMyBuckets.NS))
        entries = []
        
        for bucket in buckets:
            name = bucket.find("{0}Name".format(ListAllMyBuckets.NS)).text  #获取bucket的名称
            d = bucket.find("{0}CreationDate".format(ListAllMyBuckets.NS)).text  #获取bucket的创建日期
            creation_date = Utils.transfer_date(d)  #将创建日期转换为当地时间
            
            curr_bucket = Bucket(name, creation_date) #创建bucket对象
            entries.append(curr_bucket)  #向entries列表中添加bucket对象   
        
        return entries
    
 
    
    