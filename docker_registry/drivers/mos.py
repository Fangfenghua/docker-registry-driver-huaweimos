# -*- coding: utf-8 -*-
"""
docker_registry.drivers.mos
~~~~~~~~~~~~~~~~~~~~~~~~~~
mos is Open Storage Service provided by huawei.com
see detail http://www.hwclouds.com/
"""
import os

from com.hws.s3.client.hwawei_s3 import HuaweiS3
from com.hws.s3.models.s3object import S3Object

from docker_registry.core import dirver
from docker_registry.core import exceptions
from docker_registry.core import lru

class Storage(dirver.Base):
    def __init__(self, path=None, config=None):
        self.access_key_id = config.access_key_id
        self.secret_access_key = config.secret_access_key
        self.is_secure = config.is_secure
        self.server = config.server
        self.bucket = config.bucket
        self.mos = self.make_connection()
        self._root_path = config.storage_path or '/'
        if not self._root_path.endswith('/'):
            self._root_path += '/'

    def make_connection(self):
        if self.server:
            hw_mos = HuaweiS3(self.access_key_id,
                                   self.secret_access_key,
                                   self.is_secure,
                                   self.server)
        else:
            hw_mos = HuaweiS3(self.access_key_id,
                                   self.secret_access_key,
                                   self.is_secure)
        return hw_mos

    def _init_path(self, path=None):
        path = self._root_path + path if path else self._root_path
        if path:
            if path.startswith('/'):
                path = path[1:]
            if path.endswith('/'):
                path = path[:-1]
        return path

    @lru.get
    def get_content(self, path):
        path = self._init_path(path)
        obj = self.mos.get_object(self.bucket, path)
        return self.get_store(path)


    def get_store(self, path):
        obj = self.mos.get_object(self.bucket, path)
        if obj:
            data = str(obj.object[0])
        return data



    @lru.set
    def put_content(self, path, content):
        """Method to put content."""
        path = self._init_path(path)
        self.put_store(path, content)
        return path

    def put_store(self, path, content):
        try:
            s3b = S3Object(content)
            self.mos.create_object(self.bucket, path, s3b)
        except Exception:
             raise IOError("Could not put content: %s" % path)

    def stream_read(self, path, bytes_range=None):
        """Method to stream read."""
        pass
    
    def stream_write(self, path, fp):
        """Method to stream write."""
        pass

    def list_directory(self, path=None):
        """Method to list directory."""
        pass

    @lru.get
    def exists(self, path):
        """Method to test exists."""
        for i in range(1, 3):
            try:
                return self.mos.check_object_exist(self.bucket, path)
            except Exception:
                continue


    def remove(self, path):
        """Method to remove."""
        delobject = self.mos.delete_object(self.bucket, path, None)

    def get_size(self, path):
        """Method to get the size."""
        self.mos.get_object_filesize(self.bucket, path)
