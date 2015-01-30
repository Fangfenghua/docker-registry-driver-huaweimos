#coding=UTF-8
'''
Created on 2012-10-15

@author: s00228753
'''

import xml.etree.ElementTree as ET

from src.com.hws.s3.models.owner import Owner
from src.com.hws.s3.models.grant import Grant
from src.com.hws.s3.models.grantee import Grantee

class ACLResponse(object):
    
    def __init__(self, owner, entries):
        
        self.owner = owner
        self.entries = entries
    
    #===========================================================================
    # 定义静态方法，用来解析xml，最后返回ACLResponse对象
    #===========================================================================
    @staticmethod    
    def acl_factory(xml):
        
        if xml is not None:
            owner = ListACL.parse_owner(xml)
            entries = ListACL.parse_grant(xml)
            return ACLResponse(owner, entries)   #返回ACLResponse的对象
   

class ListACL:
    
    NS = '{http://s3.amazonaws.com/doc/2006-03-01/}'  #xml的命名空间
    ns = '{http://www.w3.org/2001/XMLSchema-instance}'
    
    #===========================================================================
    # 获取Owner相关信息
    #===========================================================================
    @staticmethod
    def parse_owner(xml):       
        root = ET.fromstring(xml)
        owner_id = root.find('.//{0}ID'.format(ListACL.NS)).text      
        owner_name = root.find('.//{0}DisplayName'.format(ListACL.NS)).text    
        owner = Owner(owner_id, owner_name)  #创建Owner对象
        return owner 

    #===========================================================================
    # 获取Grant相关信息
    #===========================================================================
    @staticmethod
    def parse_grant(xml):

        root = ET.fromstring(xml)
        grants = root.findall('./{0}AccessControlList/{0}Grant'.format(ListACL.NS))
        grant_list = []
        
        for grant in grants:
            if grant.find('./{0}Grantee'.format(ListACL.NS)).attrib.get('{0}type'.format(ListACL.ns)) == "Group":
                group1 = grant.find('./{0}Grantee/{0}URI'.format(ListACL.NS)).text[len("http://acs.amazonaws.com/groups/global/"):]
                grantee = Grantee(group = group1)                                          
            elif grant.find('./{0}Grantee'.format(ListACL.NS)).attrib.get('{0}type'.format(ListACL.ns)) == "CanonicalUser":
                owner_id = grant.find('./{0}Grantee/{0}ID'.format(ListACL.NS)).text
                owner_name = grant.find('./{0}Grantee/{0}DisplayName'.format(ListACL.NS)).text
                grantee = Grantee(owner_id, owner_name)
            
            permission = grant.find('{0}Permission'.format(ListACL.NS)).text
            
            cur_grant = Grant(grantee, permission)
            grant_list.append(cur_grant)
            
        return grant_list
                
   

