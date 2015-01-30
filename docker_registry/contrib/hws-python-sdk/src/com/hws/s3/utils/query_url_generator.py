#coding=UTF-8
'''
Created on 2012-10-12

@author: s00228753
'''

import time

from src.com.hws.s3.utils.utils import Utils
from src.com.hws.s3.utils.request_format import RequestFormat
from src.com.hws.s3.utils.request_format import PathFormat

class QueryURLGenerator:
    
    DEFAULT_EXPIRES_IN = long(60 * 1000)
    
    #===========================================================================
    # __init__ 初始化
    # @param access_key_id 连接华为S3的AK
    # @param secret_access_key 鉴权使用的SK，可用于字符串的签名
    # @param is_secure 连接是否使用SSL
    # @param server 连接的服务器
    # @param format 连接请求的格式，子域名或者路径方式
    #===========================================================================        
    def __init__(self, access_key_id, secret_access_key, is_secure = True, server = Utils.DEFAULT_HOST, 
            calling_format = RequestFormat.get_subdomainformat()):    
        
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.is_secure = is_secure
        self.server = server
        self.port = Utils.SECURE_PORT if is_secure else Utils.INSECURE_PORT
        self.calling_format = calling_format  
        
        self.expiresin = QueryURLGenerator.DEFAULT_EXPIRES_IN
        self.expires = None  
     
       
    def set_expires(self, millis_since_epoch): 
        self.expires = long(millis_since_epoch)
        self.expiresin = None
   

    def set_expiresin(self, millis):
        self.expiresin = long(millis)
        self.expires = None
    
    
    #===========================================================================
    # 获取对象的URL
    #===========================================================================
    def get(self, bucket, key, headers):

        urlstr = self.generate_url("GET", bucket, Utils.urlencode(key), None, headers)
        return urlstr

    #===========================================================================
    # 使用head方法请求该URL获取对象元数据
    #===========================================================================
    def head_meta(self, bucket, key, headers):       
        return self.generate_url("HEAD", bucket, key, None, headers)
    
    #===========================================================================
    # 临时鉴权获取对象的ACL
    #===========================================================================
    def get_acl(self, bucket, key, headers):
        path_args = {}
        path_args["acl"] = None
        return self.generate_url("GET", bucket, Utils.urlencode(key), path_args, headers)
    
    
    #===========================================================================
    # 生成临时URL
    #===========================================================================
    def make_bare_url(self, bucket, key):
        
        buf = ["https://" if self.is_secure else "http://"]
        buf.append(self.server + ":" + str(self.port) + "/" + bucket)        
        buf.append("/" + Utils.urlencode(key))
        
        return ''.join(item for item in buf)
    
    #===========================================================================
    # 生成完整URL路径 
    #===========================================================================
    def generate_url(self, method, bucket, key, path_args, headers):
        
        expires = long(0)
        
        if self.expiresin:
            expires = long(round(time.time() * 1000)) + long(self.expiresin)  #time.time()*1000获取当前时间的毫秒数
        elif self.expires:
            expires = long(self.expires)
        else:
            raise Exception("Illegal expires state")
       
        #单位转换为秒
        expires /= 1000
        canonical_string = Utils.make_canonicalstring(method, bucket, key, path_args, headers, str(expires))
        encoded_canonical = Utils.encode(self.secret_access_key, canonical_string, True)
        
        path_args = path_args if path_args else {}
        path_args["Signature"] = encoded_canonical
        path_args["Expires"] = str(expires)  #将long型转换为string型
        path_args["AWSAccessKeyId"] = self.access_key_id
               
        calling_format = Utils.get_callingformat_for_bucket(self.calling_format, bucket)
        
        if self.is_secure and not isinstance(calling_format, PathFormat) and bucket.find( "." ) != -1:
            raise Exception("You are making an SSL connection, however, the bucket contains periods and \
                             the wildcard certificate will not match by default.  Please consider using HTTP.") 
        
        #需要进行异常检查
        try:
            return_string = calling_format.get_full_url(self.is_secure, self.server, self.port, bucket, key, path_args)
        except Exception as e:
            return_string = "Exception generating url " + e.strerror
               
        return return_string
        
        
        
        
        