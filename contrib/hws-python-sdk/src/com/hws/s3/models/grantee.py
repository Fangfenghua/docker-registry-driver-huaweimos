#coding=UTF-8
'''
Created on 2012-10-12

@author: s00228753
'''

class Grantee(object):
    
    def __init__(self, grantee_id = None, grantee_name = None, group = None):
        self.grantee_id = grantee_id
        self.grantee_name = grantee_name
        self.group = group
    
 
    #===========================================================================
    # 转换为xml字符串
    # @return String 
    #===========================================================================
    def to_xml(self):
        
        str_list = []
        
        if self.group:
            str_list.append("<Grantee xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:type=\"Group\">")
            if self.group == Group.AllUsers:
                str_list.append("<URI>http://acs.amazonaws.com/groups/global/AllUsers</URI>")
            elif self.group == Group.AuthenticatedUsers:        
                str_list.append("<URI>http://acs.amazonaws.com/groups/global/AuthenticatedUsers</URI>")
            str_list.append("</Grantee>")
        
        else:
            str_list.append("<Grantee xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:type=\"CanonicalUser\">")
            str_list.append("<ID>" + self.grantee_id + "</ID>")
            str_list.append("<DisplayName>" + self.grantee_name + "</DisplayName>")
            str_list.append("</Grantee>")
                       
        return ''.join(item for item in str_list)



class Group:   
    
    AllUsers = "AllUsers"
    AuthenticatedUsers = "AuthenticatedUsers"

     
    
    
    
    