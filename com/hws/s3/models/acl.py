#coding=UTF-8
'''
Created on 2012-10-12

@author: s00228753
'''
import os,sys

#===============================================================================
# 访问控制列表
#===============================================================================
class ACL(object):
    
    def __init__(self, owner, grants):
        self.owner = owner     #资源拥有者
        self.entries = grants  #访问控制列表
    
    #===========================================================================
    # 添加授权对象    
    #===========================================================================
    def add_grant(self, grant):
        self.entries.append(grant)
    
    #===========================================================================
    # 将访问控制列表转换为xml字符串  保存到文件中
    # @return String 返回文件的路径
    #===========================================================================
    def to_xml(self):
        
        if not self.owner: 
            raise Exception("Invalid AccessControlList: missing an S3 Owner")

        str_list = []
        str_list.append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
        str_list.append("<AccessControlPolicy xmlns=\"http://s3.amazonaws.com/doc/2006-03-01/\"><Owner><ID>")
        str_list.append(self.owner.owner_id + "</ID><DisplayName>" + self.owner.owner_name + "</DisplayName>")
        str_list.append("</Owner><AccessControlList>")
        
        for acl in self.entries:
            grantee = acl.grantee
            permission = acl.permission
            str_list.append("<Grant>" + grantee.to_xml() + "<Permission>" + str(permission) + "</Permission></Grant>")
        
        str_list.append("</AccessControlList></AccessControlPolicy>")
        
        s = ''.join(item for item in str_list)
       
        path = os.path.abspath(os.path.dirname(sys.argv[0]))
        with open(path + "\\acl.xml", 'wb') as f:
            f.write(s)
    
        return path + "\\acl.xml"  #返回文件的路径名

    
    