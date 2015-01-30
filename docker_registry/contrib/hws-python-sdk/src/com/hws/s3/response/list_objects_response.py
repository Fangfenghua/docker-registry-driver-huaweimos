#coding=UTF-8
'''
Created on 2012-10-10

@author: s00228753
'''

import xml.etree.ElementTree as ET

from com.hws.s3.utils.utils import Utils
from com.hws.s3.models.owner import Owner
from com.hws.s3.models.object_entry import ObjectEntry
from com.hws.s3.models.common_prefix import CommonPrefix

class ListObjectsResponse(object):
    
    def __init__(self, name, prefix, marker, delimiter, max_keys, 
                 is_truncated, next_marker, entries, keyslist, commonprefix_entries):
        #=======================================================================
        # S3存储空间名
        #=======================================================================
        self.name = name
            
        #=======================================================================
        # 请求中使用的前缀（prefix），如果请求失败则为空，如果设置了
        # 返回对象列表结果中将只包含以前缀（prefix)开始的对象。
        #=======================================================================
        self.prefix = prefix

        #=======================================================================
        # marker---标记，如果设置了值，则返回的字符串必须比该值的字典序大，
        # 请求中如果带有该字段，则返回也将带有该字段.请求失败时为None
        #=======================================================================
        self.marker = marker

        #=======================================================================
        # 分隔符，请求中如果带该字段，则返回也将带有该字段。字符串delimiter的第一个字符
        # 和字符串prefix之间的字符序列如果相同，则这部分字符序列合并在一起，在返回信息的
        # CommonPrefixes节点显示
        #=======================================================================    
        self.delimiter = delimiter

        #=======================================================================
        # 请求中指定返回对象个数的最大值，请求失败则为0.
        # 返回的对象列表将是按照字典顺序的最多前max_keys个对象
        # 最大为1000，请求中不设置，返回也为1000
        #=======================================================================     
        self.max_keys = max_keys

        #=======================================================================
        # 标记还有更多的内容需要展示，True表示当前的罗列的结果被删减了，请求失败则为False
        # 与next_marker字段配合使用可获取对象个数超过1000的结果集。
        #=======================================================================
        self.is_truncated = is_truncated
    
        #=======================================================================
        # 指出下次请求使用的marker标记字符串，当结果集超过max_keys时，需要使用该参数。
        #=======================================================================
        self.next_marker = next_marker
        
        #=======================================================================
        # 返回的对象列表
        #=======================================================================
        self.entries = entries
        
        #=======================================================================
        # 返回的对象名列表
        #=======================================================================
        self.keyslist = keyslist
   
        #=======================================================================
        # 分隔符，前缀（prefix）与分隔符（delimiter）第一次出现之间的字符串将保存到CommonPrefix列表中，
        # 返回对象列表中包含CommonPrefix 中字符串的对象将不显示。常用的字段有“/”（用于分类文件和文件夹）
        # 可实现对象的分类显示
        #=======================================================================
        self.commonprefix_entries = commonprefix_entries


    #===========================================================================
    # 定义静态方法，用来解析xml，最后返回ListBucketResponse对象
    #===========================================================================
    @staticmethod
    def list_objects_factory(xml):
        
        if xml is not None: 
            lb = ListObjects()     #创建解析罗列对象的xml文件的对象
            lb.load_xml_file(xml)  #对xml文件进行解析
        
            #获取需要的一些参数
            name = lb.get_name()
            prefix = lb.get_prefix()
            marker = lb.get_marker()
            delimiter = lb.get_delimiter()
            max_keys = lb.get_max_keys()
            is_truncated = lb.get_is_truncated()
            next_marker = lb.get_next_marker()
            entries = lb.get_key_entries()
            keyslist = lb.get_keyslist()
            commonprefix_entries = lb.get_commonprefix_entries()

            #返回ListObjectsResponse的对象
            return ListObjectsResponse(name, prefix, marker, delimiter, max_keys, 
                                       is_truncated, next_marker, entries, keyslist, commonprefix_entries)   



#===============================================================================
# 该类用于封装解析xml文件，生成创建ListObjectsResponse对象的参数
#===============================================================================
class ListObjects:
    
    NS = '{http://s3.amazonaws.com/doc/2006-03-01/}'  #xml的命名空间
    
    def __init__(self):
        
        self.name = None
        self.prefix = None
        self.marker = None
        self.delimiter = None
        self.max_keys = 0
        self.is_truncated = False
        self.next_marker = None

        self.key_entries = []
        self.keyslist = []  #存储对象名的列表
        self.commonprefix_entries = []


    #===========================================================================
    # 解析xml文件
    #===========================================================================
    def load_xml_file(self, xml):
        
        root = ET.fromstring(xml)  #获取xml文件的根节点root       

        self.name = self.find_item(root, '{0}Name'.format(ListObjects.NS))
        self.prefix = self.find_item(root, '{0}Prefix'.format(ListObjects.NS))      
        self.marker = self.find_item(root, '{0}Marker'.format(ListObjects.NS))
        self.delimiter = self.find_item(root, '{0}Delimiter'.format(ListObjects.NS))
        self.max_keys = self.find_item(root, '{0}MaxKeys'.format(ListObjects.NS))
        is_truncated = self.find_item(root, '{0}IsTruncated'.format(ListObjects.NS))
        self.is_truncated = self.convert_bool_value(is_truncated)
        self.next_marker = self.find_item(root, '{0}NextMarker'.format(ListObjects.NS))
        
        #获取对象key的相关信息，在Contents节点中
        contents = root.findall('{0}Contents'.format(ListObjects.NS))
        if contents is not None:
            for node in contents:
                key = self.find_item(node, '{0}Key'.format(ListObjects.NS))
                t = self.find_item(node, '{0}LastModified'.format(ListObjects.NS))
                lastmodified = Utils.transfer_date(t)
                etag = self.find_item(node, '{0}ETag'.format(ListObjects.NS))
                size  = long(self.find_item(node, '{0}Size'.format(ListObjects.NS)))
            
                #获取Owner相关信息                
                owner_id = self.find_item(node, './/{0}ID'.format(ListObjects.NS))
                owner_name = self.find_item(node, './/{0}DisplayName'.format(ListObjects.NS))
                owner = Owner(owner_id, owner_name)  #创建Owner对象
        
                key_entry = ObjectEntry(key, lastmodified, etag, size, owner)
                self.key_entries.append(key_entry)  #将对象添加到对象列表中
                self.keyslist.append(key_entry.key) #将对象名添加到列表中

        #获取CommonPrefixes的相关信息
        prefixes = root.findall('{0}CommonPrefixes'.format(ListObjects.NS))
        if prefixes is not None: 
            for p in prefixes:
                pre = self.find_item(p, '{0}Prefix'.format(ListObjects.NS))
                commonprefix = CommonPrefix(pre)                
                self.commonprefix_entries.append(commonprefix)
 

    #===========================================================================
    # 获得相关的xml文件的节点
    #===========================================================================
    def find_item(self, root, itemname):
        result = root.find(itemname)
        if result is not None:
            if result.text:
                return result.text
            else:
                return ""
        else:
            return ""
        
        
    #===========================================================================
    # 布尔型字符串的转换  将小写转换成python中的大写
    #===========================================================================
    def convert_bool_value(self, string):
        if string:
            if string == "false":
                return False
            else:
                return True
        else:
            return False
        
    #===========================================================================
    # 获取创建对象时需要的一些参数
    #===========================================================================
    def get_name(self):
        return self.name

    def get_prefix(self):
        return self.prefix
    
    def get_marker(self):
        return self.marker
    
    def get_delimiter(self):
        return self.delimiter
    
    def get_max_keys(self):
        return self.max_keys
    
    def get_is_truncated(self):
        return self.is_truncated
    
    def get_next_marker(self):
        return self.next_marker
     
    def get_key_entries(self):
        return self.key_entries
    
    def get_keyslist(self):
        return self.keyslist
      
    def get_commonprefix_entries(self):
        return self.commonprefix_entries


      
