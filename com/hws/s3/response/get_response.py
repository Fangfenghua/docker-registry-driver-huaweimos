#coding=UTF-8
'''
Created on 2012-10-11

@author: s00228753
'''
import os,sys

from com.hws.s3.utils.utils import Utils

class GetResponse(object):
    
    def __init__(self, obj):
        self.object = obj
    
    #===========================================================================
    # 静态方法，返回s3的对象
    #===========================================================================
    @staticmethod
    def get_object_factory(response):
               
        body = response
        metadata = GetResponse.parse_metadata(response)
        
        obj =(body, metadata)      
        return GetResponse(obj)
        
    #===========================================================================
    # 静态方法，获取s3对象的元数据
    #===========================================================================
    @staticmethod
    def parse_metadata(response):
        
        metamap = {}
        for item in response.getheaders():
            if item[0].startswith(Utils.METADATA_PREFIX):
                key = item[0][len(Utils.METADATA_PREFIX):]
                metamap[key] = item[1]
        return metamap
    
    #===========================================================================
    # 静态方法，获取s3对象的数据
    #===========================================================================
    @staticmethod
    def get_data(response):
        CHUNKSIZE = 65563
        while True:
            chunk = response.read(CHUNKSIZE)
            if not chunk: break
            yield chunk




