#coding=UTF-8
'''
Created on 2012-9-24

@author: s00228753
'''

import datetime
import httplib
import os

from src.com.hws.s3.utils.utils import Utils
from src.com.hws.s3.utils.request_format import RequestFormat
from src.com.hws.s3.utils.request_format import PathFormat
from src.com.hws.s3.utils.query_url_generator import QueryURLGenerator
from src.com.hws.s3.response.list_buckets_response import ListBucketsResponse
from src.com.hws.s3.response.list_objects_response import ListObjectsResponse
from src.com.hws.s3.response.get_response import GetResponse
from src.com.hws.s3.response.acl_response import ACLResponse
from src.com.hws.s3.models.s3object import S3Object


class HuaweiS3(object):
    
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

    #===========================================================================
    # 检查存储空间是否存在
    # @param bucket 待检查的存储空间名
    # @return boolean 已存在则返回True
    #===========================================================================   
    def check_bucket_exists(self, bucket):  
        
        conn  = self.make_request("HEAD", bucket, "", None, None, None)
        response = conn.getresponse()
        http_code = int(response.status)

        return http_code >= 200 and http_code < 300
           
    #===========================================================================
    # 创建存储空间
    # @param bucket 存储空间名.一个用户可以拥有的存储空间的数量不能超过100个。
    # @param headers HTTP头
    # headers可加入的参数：
    # x-amz-acl 创建存储空间时，可以加上此头域设置存储空间的权限控制策略，使用的策略为预定义的常用策略，包括
    # private、public-read、public-read-write、authenticated-read、bucket-owner-read、bucket-owner-full-control
    # @return Response 创建存储空间的响应，完整的原始HTTP响应对象  
    #===========================================================================
    def create_bucket(self, bucket, headers = None): 

        #验证存储空间名字是否合法
        if not Utils.validate_bucketname(bucket, self.calling_format):
            raise Exception("Invalid Bucket Name: " + bucket)       
        
        conn = self.make_request("PUT", bucket, "", None, headers, None)
        response = conn.getresponse()
  
        return response
            
    #==========================================================================
    # 删除存储空间
    # @param bucket 存储空间名
    # @param headers HTTP头
    #==========================================================================
    def delete_bucket(self, bucket, headers = None):
        
        conn = self.make_request("DELETE", bucket, "", None, headers, None)
        response = conn.getresponse()    
        return response
      
    #==========================================================================
    # 罗列用户所有存储空间
    # @param headers HTTP头 
    #==========================================================================
    def list_buckets(self, headers = None):
        
        conn = self.make_request("GET", "", "", None, headers, None)        
        result = conn.getresponse()
        
        if int(result.status) < 400:
            xml = result.read() 
            response = ListBucketsResponse.list_parse_factory(xml)
            return response
      
    #===========================================================================
    # 查看对象是否存在
    # @param bucket 桶名
    # @param key    对象名
    # @return True|False  True表示对象存在，False表示对象不存在
    #===========================================================================
    def check_object_exist(self, bucket, key):

        flag = False
        obj_list = self.list_objects(bucket, key, max_keys = 1)   #获取对象
        
        if obj_list:
            for obj in obj_list.entries:
                if obj.key == key:
                    flag = True
  
        return flag
         
    #===========================================================================
    # 罗列对象.
    # @param bucket 存储空间名
    # @param prefix 对象前缀，设置此字段，带该前缀的对象才会返回，可为空
    # @param marker 所有返回的对象名的字典序必须大于marker指定的字符串的字典序
    # @param max_keys 对象返回的最大个数
    # @param delimiter 分隔符，前缀（prefix）与分隔符（delimiter）第一次出现之
    # 间的字符串讲保存到CommonPrefix字段中，返回对象列表中包含CommonPrefix 中字
    # 符串的对象将不显示。常用的字段有“/”（用于分类文件和文件夹）
    # @param headers HTTP头字段.
    #===========================================================================
    def list_objects(self, bucket, prefix = None, marker = None, max_keys = None, delimiter = None, headers = None):

        path_args = Utils.params_for_dict_options(prefix, marker, max_keys, delimiter)        
        conn = self.make_request("GET", bucket, "", path_args, headers, None)
        result = conn.getresponse()
        
        if int(result.status) < 400:
            xml = result.read() 
            response = ListObjectsResponse.list_objects_factory(xml)      
            return response
     
    #===========================================================================
    # 获取存储空间内所有对象
    # @param bucket
    # @return List 
    #===========================================================================   
    def list_all_objects(self, bucket):
        
        lor = self.list_objects(bucket)
        objects_list = lor.keyslist  #keyslist是对象名的列表
        
        while lor.is_truncated:
            lor = self.list_objects(bucket, marker = lor.next_marker)
            objects_list.extend(lor.keyslist)
        
        return objects_list
   
    #===========================================================================
    # 上传S3对象
    # @param bucket 存储空间名
    # @param key 对象名
    # @param s3_object S3对象
    # @param headers HTTP头,可加入的附加参数集合：
    # Content-MD5：对象的128位MD5摘要经过Base64编码形成的字符序列
    # x-amz-acl：创建对象时，可以加上此头域设置对象的权限控制策略，使用的策略为预定义
    # 的常用策略，包括：private；public-read；public-read-write；authenticated-
    # Read；bucket-owner-read；bucket-owner-full-control
    # x-amz-meta-*:创建对象时，可以在HTTP请求中加入“x-amz-meta-”头域或以“x-amz-meta-”
    # 开头的头域，用来加入自定义的元数据，以便对对象进行自定义管理。当用户获取此对象或查
    # 询此对象元数据时，加入的自定义元数据将会在返回消息的头中出现。
    #===========================================================================
    def create_object(self, bucket, key, s3_object, headers = None):
          
        conn = self.make_request("PUT", bucket, Utils.urlencode(key), None, headers, s3_object) 
         
        CHUNKSIZE = 65563  
        if s3_object.file_path:          
            with open(Utils.decode_utf(s3_object.file_path), 'rb') as f:           
                while True:
                    chunk = f.read(CHUNKSIZE)
                    if not chunk:
                        break
                    conn.send(chunk)
                    
        return conn.getresponse()
    
    #===========================================================================
    # 获取S3对象
    # @param bucket 存储空间名
    # @param key 对象名
    # @param headers HTTP头，可传入的参数及其类型如下
    # Range  获取对象时获取在Range范围内的对象内容；Range从0开始，类型：字符串，bytes=byte_range 例：bytes=0-4
    # If-Modified-Since  如果对象在请求中指定的时间之后有修改，则返回对象内容；否则的话返回304--未修改（not modified）
    # 类型：字符串    GMT格式的日期 例：Sun, 26 Sep 2010 08:42:10 GMT
    # If-Unmodified-Since 如果对象在请求中指定的时间之后没有修改，则返回对象内容；否则的话返回412---前置条件不满足（precondition failed）
    # 类型：字符串，GMT格式的日期，例：Sun, 26 Sep 2010 08:42:10 GMT
    # If-Match    如果对象的ETag和请求中指定的ETag相同，则返回对象内容，否则的话返回412---前置条件不满足（precondition failed）
    # 类型：字符串    ETag值，例：0f64741bf7cb1089e988e4585d0d3434，If-None-Match    如果对象的ETag和请求中指定的ETag不相同，则返回对象内容，
    # 否则的话返回304（not modified）类型：字符串 ETag值，例：0f64741bf7cb1089e988e4585d0d3434
    #===========================================================================
    def get_object(self, bucket, key, headers = None): 
        
        conn = self.make_request("GET", bucket, Utils.urlencode(key), None, headers, None)
        result = conn.getresponse()

        if int(result.status) < 400:
            response = GetResponse.get_object_factory(result)         
            return response
        
    #===========================================================================
    # 复制S3对象，并复制它的元数据，复制后的对象默认访问权限是为“private”
    # 如果需要更改，可在headers中添加“x-amz-acl”字段
    # @param source_bucket 源存储空间名
    # @param source_key 源对象名
    # @param dest_bucket 目标存储空间名
    # @param dest_key 目标对象名
    # @param metadata 目标对象元数据
    # @param headers HTTP头，可选参数如下：
    # x-amz-acl复制对象时，可以加上此头域设置对象的权限控制策略，使用的策略为预定义的常用策略，包括：private；public-read；
    # public-read-write； authenticated-Read；bucket-owner-read；bucket-owner-full-control
    # x-amz-copy-source-if-match    只有当源对象的Etag与此参数指定的值相等时才进行复制对象操作，
    # 否则返回412（前置条件不满足），约束条件：此参数可与x-amz-copy-source-if-unmodified-since一起使用，但不能与其它条件复制参数一起使用
    # x-amz-copy-source-if-none-match    只有当源对象的Etag与此参数指定的值不相等时才进行复制对象操作，否则返回412（前置条件不满足）
    # x-amz-copy-source-if-unmodified-since    只有当源对象在此参数指定的时间之后没有修改过才进行复制对象操作，
    # 否则返回412（前置条件不满足）此参数可与x-amz-copy-source-if-match一起使用，但不能与其它条件复制参数一起使用 
    #===========================================================================
    def copy_object(self, source_bucket, source_key, dest_bucket, dest_key, metadata = None, headers = None):
           
        obj = S3Object(None, metadata)   #创建一个空的S3对象
        
        copy_headers = headers if headers else {}
        copy_headers["x-amz-copy-source"] = [source_bucket + "/" + source_key]
        
        if metadata:
            copy_headers["x-amz-metadata-directive"] = ["REPLACE"]
        else:
            copy_headers["x-amz-metadata-directive"] = ["COPY"]

        res = self.create_object(dest_bucket, dest_key, obj, copy_headers)
        return self.verify_copy(res)
 
    #=========================================================================
    # 校验拷贝是否成功
    # @param response Put请求返回的响应.
    # @return 
    #=========================================================================
    def verify_copy(self, response):
               
        if int(response.status) < 400:
            message = response.read()
            if message.find("<Error") != -1:
                raise Exception("Error response")
            elif message.find("</CopyObjectResponse>") != -1:
                pass  #It worked!
            else:
                raise Exception("Unexpected response: " + message)
        return response
    
    #===========================================================================
    # 获取对象URL，临时鉴权
    # @param bucket 存储空间名
    # @param key    对象名
    # @param expire 过期时间
    # @return String expire不为空时，返回对象的临时鉴权URL；expire为空时，返回对象的URL
    #===========================================================================
    def get_object_url(self, bucket, key, expire = None):
        
        qag = QueryURLGenerator(self.access_key_id, self.secret_access_key, self.is_secure, self.server, self.calling_format)
        
        if expire:
            qag.set_expiresin(expire)
            return qag.get(bucket, key, None)
        else:
            return qag.make_bare_url(bucket, key)

    #===========================================================================
    # 临时鉴权获取对象的元数据，得到鉴权URL，可使用head方法请求该URL获取对象元数据
    # @param bucket 存储空间名
    # @param key    对象名
    # @param expire 有效时间 
    #===========================================================================
    def get_object_metaurl(self, bucket , key, expire):
        
        qag = QueryURLGenerator(self.access_key_id, self.secret_access_key, self.is_secure, self.server, self.calling_format)      
        qag.set_expiresin(expire)
        return qag.head_meta(bucket, key, None)
              
    #===========================================================================
    # 指定S3对象写入ACL
    # @param bucket 存储空间名
    # @param key 对象名
    # @param acl_path 需要设置的ACL的文件路径
    # @param headers Http头部，一系列的键值对，可以为空
    #===========================================================================
    def set_object_acl(self, bucket, key, acl_path, headers):

        obj = S3Object(acl_path, None)
        
        path_args = {}       
        path_args["acl"] = None

        conn = self.make_request("PUT", bucket, Utils.urlencode(key), path_args, headers, obj)
        
        CHUNKSIZE = 65563
        if acl_path:
            with open(acl_path, 'rb') as f:
                while True:
                    chunk = f.read(CHUNKSIZE)
                    if not chunk:
                        break
                    conn.send(chunk)
      
        return conn.getresponse()

    #===========================================================================
    # 指定存储空间内写入ACL    
    # @param bucket 存储空间名
    # @param acl_path 需要设置的ACL的文件路径
    # @param headers Http头部，一系列的键值对，可以为空
    #===========================================================================
    def set_bukcet_acl(self, bucket, acl_path, headers):
        return self.set_object_acl(bucket, "", acl_path, headers)
    
    #===========================================================================
    # 获取对象的ACL
    # @param bucket 存储空间名
    # @param key 对象名
    # @param headers HTTP头
    #===========================================================================
    def get_object_acl(self, bucket, key, headers):
        
        if key == None:
            key = ""       
        
        path_args = {}
        path_args["acl"] = None
        
        conn = self.make_request("GET", bucket, Utils.urlencode(key), path_args, headers, None)        
        result = conn.getresponse()
        if int(result.status) < 400:             
            return result.read() 
    
    #===========================================================================
    # 获取存储空间的ACL
    # @param bucket 存储空间名
    # @param headers HTTP头
    #===========================================================================
    def get_bucket_acl(self, bucket, headers):
        return self.get_object_acl(bucket, "", headers)
   
    #===========================================================================
    # 获取对象的ACL，并解析
    # @param bucket 存储空间名
    # @param key  对象名
    # @param headers HTTP头
    # @return AclResponse 
    #===========================================================================
    def get_acl_response(self, bucket, key, headers = None):
        
        if key == None:
            key = ""
                
        path_args = {}
        path_args["acl"] = None
        
        conn = self.make_request("GET", bucket, Utils.urlencode(key), path_args, headers, None)
        result = conn.getresponse()
        
        if int(result.status) < 400:
            xml = result.read()
            response = ACLResponse.acl_factory(xml)   
            return response
    
    #===========================================================================
    # 临时鉴权获取对象的ACL
    # @param bucket 存储空间名
    # @param key    对象名
    # @param expire 有效时间
    #===========================================================================
    def get_object_authacl(self, bucket, key, expire):
        qag = QueryURLGenerator(self.access_key_id, self.secret_access_key, self.is_secure, self.server, self.calling_format)     
        qag.set_expiresin(expire)
        return qag.get_acl(bucket, key, None)       
    
    #===========================================================================
    # 删除S3对象
    # @param bucket 存储空间名
    # @param key 对象名
    # @param headers HTTP头
    #===========================================================================
    def delete_object(self, bucket, key, headers):
        
        conn = self.make_request("DELETE", bucket, Utils.urlencode(key), None, headers, None)
        return conn.getresponse()
   
    #===========================================================================
    # 获取用户ID,请求失败则为None
    #===========================================================================
    def get_canonical_userid(self):       
        return self.list_buckets().owner.owner_id      
        
    #===========================================================================
    # 获取用户Name,请求失败则为None
    #===========================================================================
    def get_canonical_username(self):       
        return self.list_buckets().owner.owner_name  
                      
    #===========================================================================
    # 生成Http请求（HttpConnection），带S3实体对象
    # @param method HTTP方法(GET, PUT, DELETE)
    # @param bucket 存储空间名
    # @param key 对象名
    # @param path_args URL参数
    # @param headers HTTP头
    # @param s3_object 将写入S3对象
    #===========================================================================
    def make_request(self, method, bucket, key, path_args, headers, s3_object):
        
        calling_format = Utils.get_callingformat_for_bucket(self.calling_format, bucket)
    
        if self.is_secure and not isinstance(calling_format, PathFormat) and bucket.find( "." ) != -1:
            raise Exception("You are making an SSL connection, however, the bucket contains periods and \
                            the wildcard certificate will not match by default. Please consider using HTTP.")
        
        path = calling_format.get_url(self.is_secure, self.server, self.port, bucket, key, path_args)
        connect_server = calling_format.get_server(self.server, bucket)  
        
        if s3_object:
            head = self.add_metadata_headers(self.add_headers(headers, ""), s3_object.metadata)     
        else:
            head = self.add_headers(headers, "")
     
        headerconfig = self.add_auth_headers(head, method, bucket, key, path_args)
        
        if s3_object:
            if s3_object.file_path:
                headerconfig["Content-Length"] = str(os.path.getsize(Utils.decode_utf(s3_object.file_path)))  #需要手动将content-length添加到头信息中
            else:
                headerconfig["Content-Length"] = str(0)
        
        return self.send_request(connect_server, method, path, headerconfig)
    
    #===========================================================================
    # 发送请求
    #===========================================================================
    def send_request(self, server, method, path, header):        
        conn = self.get_server_connection(server)
        conn.request(method, path, headers = header)
        return conn
    
    #===========================================================================
    # 获取服务器连接
    #===========================================================================
    def get_server_connection(self, server):
        conn = httplib.HTTPSConnection(server, port = self.port) if self.is_secure else httplib.HTTPConnection(server, port = self.port)
        return conn
       
    #===========================================================================
    # 为HttpConnection添加头
    # @param headers 需要在HTTP头中添加的字段，key-value格式的字典类型
    # @param prefix 在发起连接之前为每个头部字段添加前缀
    #===========================================================================
    def add_headers(self, headers, prefix):
        
        new_headers = {}
        if headers:       
                for i in headers.keys():
                    key = str(i)
                    for v in headers.get(key):
                        value = str(v)
                        new_headers[(prefix + Utils.urlencode(key))] = Utils.urlencode(value)

        return new_headers

    #===========================================================================
    # 为HttpConnection添加可信的HTTP头
    # @param headers 将可信HTTP头添加到headers头中，字典型
    # @param method HTTP方法（PUT,GET,DELETE)
    # @param bucket 存储空间名
    # @param key 对象名
    # @param path_args 请求URL中的路径参数    
    #===========================================================================
    def add_auth_headers(self, headers, method, bucket, key, path_args):
        
        #如果headers头中不存在Date和Content-Type或其值为空时，则添加
        if not headers.get("Date"):
            headers["Date"] = self.httpdate()
        
        if not headers.get("Content-Type"):
            headers["Content-Type"] = ""
                
        canonical_string = Utils.make_canonicalstring(method, bucket, key, path_args, headers, None)
        encoded_canonical = Utils.encode(self.secret_access_key, canonical_string, False)              
        auth = "AWS " + self.access_key_id + ":" + encoded_canonical  #字符串连接
        
        headers["Authorization"] = auth
        
        return headers
       
    #=========================================================================
    # HttpConnection中添加元数据(metadata)字段
    # @param metadata s3对象中的元数据
    #=========================================================================
    def add_metadata_headers(self, headers, metadata): 

        if metadata:       
            for i in metadata.keys():
                key = str(i)
                for v in metadata.get(key):
                    value = str(v)
                    headers[(Utils.METADATA_PREFIX + Utils.urlencode(key))] = Utils.urlencode(value)
             
        return headers
        
    #==========================================================================
    # 获取对象的HTTP头消息,包含元数据
    # @param bucket 存储空间名
    # @param key 对象名
    # @return dict字典类型
    #==========================================================================
    def get_object_headers(self, bucket, key):        
        return self.head(bucket, key).getheaders()
     
    #===========================================================================
    # 通用head方法执行查询对象返回的元数据
    # @param bucket 存储空间名
    # @param key    对象名
    # @return Response  HTTP响应对象
    #===========================================================================
    def head(self, bucket, key):

        conn = self.make_request("HEAD", bucket, key, None, None, None)
        return conn.getresponse()
        
    #===========================================================================
    # 获取对象大小
    # @param bucket 存储空间名
    # @param key      对象名
    #===========================================================================   
    def get_object_filesize(self, bucket, key):

        objects_list = self.list_objects(bucket, key, max_keys = 1)

        if objects_list:
            if objects_list.entries:
                obj = objects_list.entries[0]
                return obj.size
                                     
    #===========================================================================
    # 为HTTP头的Date字段生成rfc822格式的时间
    #===========================================================================
    def httpdate(self):        
        
        GMT_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
        date = datetime.datetime.utcnow().strftime(GMT_FORMAT) #用当前时间来生成datetime对象       
        return date
