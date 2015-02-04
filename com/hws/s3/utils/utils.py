#coding=UTF-8
'''
Created on 2012-9-25

@author: s00228753
'''

import hashlib, hmac
import binascii
import re
import time
import urllib   

import request_format

import sys

reload(sys)

sys.setdefaultencoding('UTF-8')


class Utils(object):
    
    METADATA_PREFIX = "x-amz-meta-"
    AMAZON_HEADER_PREFIX = "x-amz-"
    ALTERNATIVE_DATE_HEADER = "x-amz-date"
    DEFAULT_HOST = "s3-hd1.hwclouds.com"
    
    SECURE_PORT = 443
    INSECURE_PORT = 80   
    
    #==========================================================================
    # 构造待签名的串，如果过期时间（expires）为空，则使用HTTP头中的Date字段
    #==========================================================================
    @staticmethod
    def make_canonicalstring(method, bucket_name, key, path_args, headers, expires = None):
        
        str_list = [] 
        str_list.append(method + "\n")
        
        #添加所有相关的头部字段（Content-MD5, Content-Type, Date和以x-amz开头的），并排序
        interesting_headers = {}  #使用字典表示
        content_list = ["content-type", "content-md5", "date"]
        if headers:
            for hash_key in headers.keys():
                lk = hash_key.lower()  #headers的key值的小写
                
                #忽略不相关的HTTP头字段
                if lk in content_list or lk.startswith(Utils.AMAZON_HEADER_PREFIX):                
                    s = headers.get(hash_key)  #获得headers中的值列表
                    interesting_headers[lk] = ''.join(s)
                                                         
        #如果有amz的时间标记就无需加入原有的date标记
        if Utils.ALTERNATIVE_DATE_HEADER in interesting_headers.keys():
            interesting_headers.setdefault("date", "")
        
        #如果过期时间不为空，则将过期时间填入date字段中
        if expires:
            interesting_headers["date"] = expires
       
        #这些字段必须要加入，故即使没有设置也要加入
        if not "content-type" in interesting_headers.keys():
            interesting_headers["content-type"] = ""

        if not "content-md5" in interesting_headers.keys():
            interesting_headers["content-md5"] = ""
        
        #取出字典中的key并进行排序
        keylist = interesting_headers.keys()
        keylist.sort()
        
        #最后加入所有相关的HTTP头部字段 (例如: 所有以x-amz-开头的)
        for k in keylist:
            header_key = str(k)
            if header_key.startswith(Utils.AMAZON_HEADER_PREFIX):
                str_list.append(header_key + ":" + interesting_headers[header_key])
            else:
                str_list.append(interesting_headers[header_key])
            str_list.append("\n")

        #使用存储空间名和对象名构建路径
        if bucket_name:          
            str_list.append("/" + bucket_name)
             
        #再加入一个反斜杠
        str_list.append("/")
        
        #对象名不为空，则添加对象名到待签名的字符串中
        if key: 
            str_list.append(key)
        
        #最后检查路径参数里是否有ACL，有则加入
        if path_args and "acl" in path_args.keys():
            str_list.append("?acl")

        return ''.join(item for item in str_list) #返回待签名的字符串      
    
    #===========================================================================
    # 计算字符串的hash值，采用HMAC/SHA1算法
    # @param secret_access_key 鉴权使用的SK
    # @param canonicalstring   待签名的字符串
    # @param urlencode         是否进行URL签名
    # @return String 签名（带SK的哈希值）
    #===========================================================================
    @staticmethod
    def encode(secret_access_key, canonicalstring, urlencode):    
        
        hashed = hmac.new(secret_access_key, canonicalstring, hashlib.sha1) #使用sha1算法创建hmac的对象
        encode_canonical = binascii.b2a_base64(hashed.digest())[:-1] #获得加密后的字符串，即hash值
        
        if urlencode:
            return Utils.urlencode(encode_canonical)
        else:
            return encode_canonical
        
    #===========================================================================
    # 校验路径方式的存储空间名
    # @return bool型值： True或False
    #===========================================================================
    @staticmethod
    def validate_bucketname(bucket_name, calling_format):

        if isinstance(calling_format, request_format.PathFormat):
            MIN_BUCKET_LENGTH = 3
            MAX_BUCKET_LENGTH = 63
            BUCKET_NAME_REGEX = "^[0-9A-Za-z\\.\\-_]*$"
            
            flag = bucket_name and Utils.length_in_range(bucket_name, MIN_BUCKET_LENGTH, MAX_BUCKET_LENGTH) and \
                   re.match(BUCKET_NAME_REGEX, bucket_name) #\用于连接下一行字符            
            return flag
        
        else:
            return Utils.valid_subdomain_bucketname(bucket_name)
    
    
    #===========================================================================
    # 校验子域名的存储空间
    #===========================================================================    
    @staticmethod
    def valid_subdomain_bucketname(bucket_name):
        
        MIN_BUCKET_LENGTH = 3
        MAX_BUCKET_LENGTH = 63
        
        #存储空间名不能是IP格式
        IPv4_REGEX = "^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+$"
        #DNS子域名格式限制
        BUCKET_NAME_REGEX = "^[a-z0-9]([a-z0-9\\-]*[a-z0-9])?(\\.[a-z0-9]([a-z0-9\\-]*[a-z0-9])?)*$"       
        
        #最后执行存储空间名检查
        flag = bucket_name and Utils.length_in_range(bucket_name, MIN_BUCKET_LENGTH, MAX_BUCKET_LENGTH) and \
                not re.match(IPv4_REGEX, bucket_name) and re.match(BUCKET_NAME_REGEX, bucket_name)
        
        return flag
    
    #===========================================================================
    # 检查存储空间的长度
    #===========================================================================
    @staticmethod
    def length_in_range(bucket_name, min_len, max_len):
        return len(bucket_name) >= min_len and len(bucket_name) <= max_len
       
    #===========================================================================
    # 获取存储空间的调用方式  
    #===========================================================================
    @staticmethod
    def get_callingformat_for_bucket(desired_format, bucket_name):  
         
        calling_format = desired_format
        if isinstance(calling_format, request_format.SubdomainFormat) and not Utils.valid_subdomain_bucketname(bucket_name):
            calling_format = request_format.RequestFormat.get_pathformat()
    
        return calling_format
     
         
    #===========================================================================
    # 将路径参数从map类型转换为字符串
    # @param path_args 参数hash表
    # @return String  转换后的路径参数字符串     
    #===========================================================================
    @staticmethod
    def convert_path_string(path_args): 
        
        path_list =[]
        first_run = True
        
        if path_args:
            for i in path_args.keys():
                arg = str(i)
                
                if first_run:
                    first_run = False
                    path_list.append("?")
                else:
                    path_list.append("&")
                
                arg_value = path_args.get(arg)
                path_list.append(arg)

                if arg_value:
                    path_list.append("=")
                    path_list.append(str(arg_value))
      
        return ''.join(item for item in path_list)    
         
    #===========================================================================
    # 时间格式的转换，将xml文件中的GMT时间转换为当地时间CST格式
    #===========================================================================
    @staticmethod
    def transfer_date(date):
        
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"    #xml文件中的时间格式
        CST_FORMAT = "%a %b %d %H:%M:%S CST %Y"  #转换为CST格式的时间
    
        gmt_time = time.strptime(date, date_format)  #date是GMT格式的时间
        
        cst_time = time.localtime(time.mktime(gmt_time) - time.timezone) #time.timezone是当前时区和0时区相差的描述，值为-28800=-8*3600，即为东八区
        dt = time.strftime(CST_FORMAT, cst_time)

        return dt     
    
    #===========================================================================
    # 将参数转换为字典dictionary类型
    # @param prefix
    # @param marker
    # @param max_keys
    # @param delimiter
    # @return
    #===========================================================================
    @staticmethod
    def params_for_dict_options(prefix, marker, max_keys, delimiter = None):
        
        args = {}
        
        #这些参数必须使用url编码
        if prefix:
            args["prefix"] = Utils.urlencode(prefix)
        if marker:
            args["marker"] = Utils.urlencode(marker)
        if delimiter:
            args["delimiter"] = Utils.urlencode(delimiter)      
        if max_keys:
            args["max-keys"] = str(max_keys)
        
        return args

         
    #==========================================================================
    # URL编码字符串
    # @param unencoded    待编码的字符串
    # @return URL编码后的字符串    
    #==========================================================================
    @staticmethod
    def urlencode(unencoded):
        #return urllib.quote(unencoded.decode(sys.stdin.encoding).encode('utf8'))  
        params = {"q": unencoded.encode('UTF-8')}
        return urllib.urlencode(params).replace("q=", "")
    
    @staticmethod
    def decode_utf(undecoded):
        return undecoded.decode("UTF-8")

    @staticmethod
    def unencode(encode_str):
        return urllib.unquote(encode_str)  

