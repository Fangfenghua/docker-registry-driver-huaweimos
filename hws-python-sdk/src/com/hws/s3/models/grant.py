#coding=UTF-8
'''
Created on 2012-10-12

@author: s00228753
'''

from grantee import Grantee

class Grant(object):
    
    #===========================================================================
    # 初始化
    # @param grantee 被授权者
    # @param permission 权限
    #===========================================================================
    def __init__(self, grantee = Grantee(), permission = None):
        self.grantee = grantee
        self.permission = permission
        

class Permission:
    
    READ = "READ"
    WRITE = "WRITE"
    READ_ACP = "READ_ACP"
    WRITE_ACP = "WRITE_ACP"
    FULL_CONTROL = "FULL_CONTROL"   
        


