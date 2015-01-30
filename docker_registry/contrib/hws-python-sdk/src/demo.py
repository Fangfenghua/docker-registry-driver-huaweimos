#coding=UTF-8
'''
Created on 2012-9-24

@author: s00228753
'''

import os


from com.hws.s3.client.huawei_s3 import HuaweiS3
from com.hws.s3.models.owner import Owner
from com.hws.s3.models.s3object import S3Object
from com.hws.s3.models.grantee import Grantee
from com.hws.s3.models.grantee import Group
from com.hws.s3.models.grant import Grant
from com.hws.s3.models.grant import Permission
from com.hws.s3.models.acl import ACL

def demo():   

    #指定用户自己的AK，SK
    AK = ""
    SK = ""

    #初始化  定义一个HuaweiS3对象    
    s3 = HuaweiS3(AK, SK, False)  
    bucket_name = "test2012" + AK.lower() #字符串转换成小写

    #===========================================================================
    # 检查存储空间是否存在
    #===========================================================================
    print "检查是否存在存储空间"
    print s3.check_bucket_exists(bucket_name), "\n"              

    #===========================================================================
    # 创建存储空间
    #===========================================================================
    print "新建存储空间：", bucket_name
    bucket = s3.create_bucket(bucket_name)
    print bucket.reason, "\n"      

    #===========================================================================
    # 罗列存储空间
    #===========================================================================
    print "罗列存储空间："
    lmb = s3.list_buckets()   
    bucket_list = lmb.entries
    
    print "the bucket list owner is:", s3.get_canonical_username(), "and ID is:", s3.get_canonical_userid()
    owner = Owner(lmb.owner.owner_id, lmb.owner.owner_name)  
    
    print "the bucket list:"
    for bk in bucket_list:
        print bk.name, "  ", bk.create_date, "\n"

    #===========================================================================
    # 罗列对象
    #===========================================================================
    print "罗列对象："
    list_obj = s3.list_objects(bucket_name)
    if list_obj:
        for key in list_obj.keyslist:
            print key
        
    lor = s3.list_objects(bucket_name, "t", None, 1, "key", None)  #lor为ListObjectsResponse的对象           
    print "对象超过1000个时，可采用isTruncated标记，继续向后查询"    
    if lor:
        if lor.is_truncated and lor.next_marker:
            print s3.list_objects(bucket_name, "", lor.next_marker, None, "", None).keyslist
            
        print "罗列对象返回的额外信息："
        print "prefix:", lor.prefix
        print "delimiter:", lor.delimiter
        print "isTruncated:", lor.is_truncated
        print "marker:", lor.marker
        print "maxKeys:", lor.max_keys
        print "nextMarker:", lor.next_marker
        print "CommonPrefix:"
        for it in lor.commonprefix_entries:
            pf = it.prefix
            print pf
    
        print "Keys lastmodified:"
        for k in lor.entries:
            key = k.key
            lastmodified = k.lastmodified
            print key, "  ", lastmodified           
        
    #===========================================================================
    # 上传对象
    #===========================================================================   
    print "采用put方法上传对象" 
    file_path = r"D:\test.txt"  #待上传对象所在的路径
    objkey = os.path.split(file_path)[1]   #以上传文件的文件名作为对象名
        
    metadata = {}  #元数据用字典表示，其中的value必须使用列表类型 
    metadata["blah"] = ["foo"]
    metadata["testmeta"] = ["hhee"]
    metadata["测试元数据"] = ["元数据"]

    s3b = S3Object(file_path, metadata)           
    obj = s3.create_object(bucket_name, objkey, s3b)
    print obj.status, obj.reason, "\n"
                
    #===========================================================================
    # 检查对象是否存在
    #===========================================================================
    print "检查对象是否存在"
    print s3.check_object_exist(bucket_name, objkey)
  
    #===========================================================================
    # 获取对象大小
    #===========================================================================
    print "获取对象大小：", s3.get_object_filesize(bucket_name, objkey)
    
    #===========================================================================
    # 获取对象内容
    #===========================================================================
    print "获取对象内容："
    obj = s3.get_object(bucket_name, objkey)
    if obj:
        data = str(obj.object[0])
        print data  #从元组tuple中获取对象内容
       
    #===========================================================================
    # 获取对象元数据
    #===========================================================================
    print "获取对象元数据："
    if obj:
        meta = obj.object[1]  #从元组中获取对象的元数据
        print meta, "\n"

    #===========================================================================
    # 生成临时URL
    #===========================================================================
    print "获取临时的URL：" 
    print s3.get_object_url(bucket_name, objkey) 
        
    #===========================================================================
    # 获取对象URL
    #===========================================================================
    print "获取URL"
    expire = 120*1000
    print s3.get_object_url(bucket_name, objkey, expire)
    
    #===========================================================================
    # 临时鉴权获取对象的元数据，得到鉴权URL            
    #===========================================================================
    print "临时鉴权获取对象元数据的URL"
    print s3.get_object_metaurl(bucket_name, objkey, expire)
    
    #===========================================================================
    # 获取对象的请求头
    #===========================================================================       
    print "获取S3对象响应的HTTP头消息"
    temp = s3.get_object_headers(bucket_name, objkey)  #获得对象的headers 列表形式
    for item in temp:
        key = item[0]
        if key:
            value = item[1]
            print key, ":", value
    print ""        
        
    #===========================================================================
    # 复制对象
    #===========================================================================
    copymeta = {}  #元数据用字典表示，其中的value必须使用列表类型 
    copymeta["www"] = ["qqq"]
    
    print "复制对象"
    copy = s3.copy_object(bucket_name, objkey, bucket_name, "copy" + objkey, copymeta)
    print copy.reason
    
    print "获取复制的对象元数据："
    obj = s3.get_object(bucket_name, "copy" + objkey)
    if obj:
        meta = obj.object[1]  #从元组中获取对象的元数据
        print meta, "\n"
        
    #===========================================================================
    # 设置对象的ACL
    #===========================================================================      
    grantee = Grantee(group = Group.AllUsers)
    grantee1 = Grantee(owner.owner_id, owner.owner_name)
    
    grant1 = Grant(grantee1, Permission.FULL_CONTROL)
    grant = Grant(grantee, Permission.READ)
    
    grants = []
    grants.append(grant)  
    grants.append(grant1)  
        
    acl = ACL(owner, grants)
    print "设置对象的ACL："
    obj_acl = s3.set_object_acl(bucket_name, objkey, acl.to_xml(), None)  
    print obj_acl.reason, "\n"            
    
    #===========================================================================
    # 设置存储空间的ACL
    #===========================================================================
    print "设置存储空间的ACL："
    bucket_acl = s3.set_bukcet_acl(bucket_name, acl.to_xml(), None) 
    print bucket_acl.reason, "\n"    
    
    #===========================================================================
    # 查看对象的ACL    
    #===========================================================================
    print "查看对象的ACL："
    acl = s3.get_object_acl(bucket_name, objkey, None)
    if acl:
        print acl
    
    acl_res = s3.get_acl_response(bucket_name, objkey)
    if acl_res:
        print acl_res.owner.owner_id, acl_res.owner.owner_name
 
        for item in acl_res.entries:
            if item.grantee.group:
                print item.grantee.group
            else:
                print item.grantee.grantee_name
 
    #===========================================================================
    # 查看存储空间的ACL    
    #===========================================================================
    print "查看存储空间的ACL："
    acl = s3.get_bucket_acl(bucket_name, None)
    if acl:
        print acl
     
    raw_input()       
    #===========================================================================
    # 删除对象
    #===========================================================================
    print "删除对象："
    del_list = s3.list_objects(bucket_name)
    if del_list:   
        for it in del_list.entries:
            delobject = s3.delete_object(bucket_name, it.key, None)
            print delobject.reason, "\n"
                
    #===========================================================================
    # 删除存储空间
    #===========================================================================
    print "删除存储空间："
    delbucket = s3.delete_bucket(bucket_name)
    print delbucket.reason,"\n"    


#指定用户自己的AK，SK
AK = "F7AA08A4356B188CF37C"
SK = "3/99tIlcis5HzmRUKo6ZmVd3klgAAAFLNWsYjKhD"

#初始化  定义一个HuaweiS3对象
s3 = HuaweiS3(AK, SK, False)
bucket_name = "ffh-bucket" #字符串转换成小写
print "检查是否存在存储空间"
print s3.check_bucket_exists(bucket_name), "\n"
objkey="test.txt"
#=========================================================================== # 检查对象是否存在
 #==========================================================================
print "检查对象是否存在"
print s3.check_object_exist(bucket_name, objkey)

#===========================================================================
# 获取对象大小
#===========================================================================
print "获取对象大小：", s3.get_object_filesize(bucket_name, objkey)
