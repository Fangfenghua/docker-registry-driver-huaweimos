#coding=UTF-8
'''
Created on 2012-10-10

@author: s00228753
'''

#===============================================================================
# 代表S3 逻辑对象（不包含其真实内容,只包含属性），在ListObjectResponse中使用
#===============================================================================
class ObjectEntry(object):
    
    def __init__(self, key, lastmodified, etag, size, owner):
        
        self.key = key                    #对象的名称
        self.lastmodified = lastmodified  #对象最后修改的时间
        self.etag = etag                  #对象的eTag属性
        self.size = size                  #对象大小（单位byte）
        self.owner = owner                #对象的拥有者
 
 
    def __str__(self):
        return self.key
    
    
    
    
    