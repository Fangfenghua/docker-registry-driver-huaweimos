#coding=UTF-8
'''
Created on 2012-9-26

@author: s00228753
'''

import abc
import utils

#===============================================================================
# 请求格式，发送HTTP请求时，URL是路径模式或者子域名格式
#===============================================================================
class RequestFormat(object):
    
    @staticmethod       
    def get_pathformat():
        return PathFormat()
    
    @staticmethod
    def get_subdomainformat():
        return SubdomainFormat()
    
    @staticmethod
    def get_vanityformat():
        return VanityFormat()

    @abc.abstractmethod
    def supports_locatedbuckets(self):
        '''
        '''
        return

    @abc.abstractmethod
    def get_endpoint(self, server, port, bucket):
        '''
        '''
        return
    
    @abc.abstractmethod
    def get_pathbase(self, bucket, key):
        '''
        '''
        return
    
    @abc.abstractmethod
    def get_url(self, is_secure, server, port, bucket, key, path_args):
        '''
        '''
        return
    
#==========================================================================
# 请求方式类，路径请求方式。
# 带对象和存储空间的请求为：s3.hwclouds.com/bucketname/key
# 不带对象，带存储空间的请求为：s3.hwclouds.com/bucketname/
# 不带存储空间和对象的的请求为：s3.hwlcouds.com/
#==========================================================================  
class PathFormat(RequestFormat):
       
    def supports_locatedbuckets(self):
        return True 
    
    def get_server(self, server, bucket):
        return server
       
    def get_pathbase(self, bucket, key):        
        if key:                  
            return "/" + bucket + "/" + key if self.is_bucket_specified(bucket) else "/"
        else:
            return "/" + bucket +"/" if self.is_bucket_specified(bucket) else "/"  
    
    def get_endpoint(self, server, port, bucket):
            return server + ":" + str(port)

    #===========================================================================
    # 获得相对url
    #===========================================================================
    def get_url(self, is_secure, server, port, bucket, key, path_args):
        path_base = self.get_pathbase(bucket, key)
        path_arguments = utils.Utils.convert_path_string(path_args)
        url = path_base + path_arguments
        return url
    
    #===========================================================================
    # 获得绝对url  完整路径
    #===========================================================================
    def get_full_url(self, is_secure, server, port, bucket, key, path_args):    
        url = "https://" if is_secure else "http://" 
        url += self.get_endpoint(server, port, bucket)
        url += self.get_url(is_secure, server, port, bucket, key, path_args)        
        return url

          
    def is_bucket_specified(self, bucket):      
        return True if bucket else False
            
#===============================================================================
# 请求方式类，子域请求方式。
# 带对象和存储空间的请求为：bucketname.s3.hwclouds.com/key
# 不带对象，带存储空间的请求为：bucketname.s3.hwclouds.com/
# 不带存储空间和对象的的请求为：s3.hwlcouds.com/
#===============================================================================
class SubdomainFormat(RequestFormat):
       
    def supports_locatedbuckets(self):
        return True 

    def get_server(self, server, bucket):
        return bucket + '.' + server if bucket else server

    def get_pathbase(self, bucket, key):  
        return "/" + key if key else "/"

    def get_endpoint(self, server, port, bucket):
        return self.get_server(server, bucket) + ':' + str(port)
    
    #===========================================================================
    # 获得相对url
    #===========================================================================
    def get_url(self, is_secure, server, port, bucket, key, path_args):
        
        if bucket:
            path_base = self.get_pathbase(bucket, key)
            path_arguments = utils.Utils.convert_path_string(path_args)
            return path_base + path_arguments
        else:
            return utils.Utils.convert_path_string(path_args)
        
    #===========================================================================
    # 获得绝对url 完整路径
    #===========================================================================
    def get_full_url(self, is_secure, server, port, bucket, key, path_args):
        url = 'https://' if is_secure else 'http://'
        url += self.get_endpoint(server, port, bucket)
        url += self.get_url(is_secure, server, port, bucket, key, path_args)
        return url

   
           
class VanityFormat(SubdomainFormat):
           
    def get_server(self, server, bucket):
        return bucket

