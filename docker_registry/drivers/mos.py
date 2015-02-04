# -*- coding: utf-8 -*-
"""
docker_registry.drivers.mos
~~~~~~~~~~~~~~~~~~~~~~~~~~
mos is Open Storage Service provided by huawei.com
see detail http://www.hwclouds.com/
"""
import os
import logging
import StringIO

from com.hws.s3.client.huawei_s3 import HuaweiS3
from com.hws.s3.models.s3object import S3Object

from docker_registry.core import driver
from docker_registry.core import exceptions
from docker_registry.core import lru

logging.basicConfig(filename = os.path.join(os.getcwd(), '/var/log/mos/log.txt'), level = logging.WARN, filemode = 'w', format = '%(asctime)s - %(levelname)s: %(message)s')  


class Storage(driver.Base):
    def __init__(self, path=None, config=None):
        self.access_key_id = config.mos_accessid
        self.secret_access_key = config.mos_accesskey
        self.is_secure = config.secure or False
        self.server = config.mos_host or "s3-hd1.hwclouds.com"
        self.bucket = config.mos_bucket
        self.mos = self.make_connection()
        self._root_path = config.storage_path or '/registry/'
        if not self._root_path.endswith('/'):
            self._root_path += '/'
        logging.debug("AK=%s,SK=%s,secure=%s,bucker=%s,root_path=%s" %
                     (self.access_key_id, self.secret_access_key, self.is_secure,
                     self.server, self._root_path))

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
        if not self.exists(path):
            raise exceptions.FileNotFoundError("File not found %s" % path)
        path = self._init_path(path)
        output = StringIO.StringIO()
        try:
            for buf in self.get_store(path):
                output.write(buf)
            return output.getvalue()
        finally:
            output.close()

    def get_store(self, path, buffer_size=None):
        response = self.mos.get_object(path)
        try:
            while True:
                chunk = response.read(buffer_size)
                if not chunk: break
                yield chunk
        except:
            raise IOError("Could not get content: %s" % path)

    @lru.set
    def put_content(self, path, content):
        """Method to put content."""
        path = self._init_path(path)
        logging.debug("path=%s,type(content)=%s"%(path,type(content)))
        self.put_store(path, content)
        return path

    def put_store(self, path, content, buff_size=None):
        try:
            with open("/tmp/content","w+") as fp:
                fp.write(content)
            s3b = S3Object("/tmp/content")
            self.mos.create_object(self.bucket, path, s3b)
        except Exception:
             raise IOError("Could not put path: %s.content=%s" % (path, content))

    def stream_read(self, path, bytes_range=None):
        """Method to stream read."""
        if not self.exists(path):
            raise exceptions.FileNotFoundError("File not found %s" % path)
        path = self._init_path(path)
        res = self.get_store(path, self.buffer_size)
        if res.status == 200:
            block = res.read(self.buffer_size)
            while len(block) > 0:
                yield block
                block = res.read(self.buffer_size)
        else:
            raise IOError('read %s failed, status: %s' % (path, res.status))
 
    def stream_write(self, path, fp):
        """Method to stream write."""
        path = self._init_path(path)
        try:
            with open("/tmp/content", 'w') as f:
                while True:
                    buf = fp.read(self.buffer_size)
                    if not buf: break
                    f.write(buf)
            s3b = S3Object("/tmp/content")
            self.mos.create_object(self.bucket, path, s3b)
        except:
            raise
        return path

    def list_directory(self, path=None):
        """Method to list directory."""
        path = self._init_path(path)
        list_obj = self.mos.list_objects(self.bucket, path)
        if list_obj:
            for key in list_obj.keyslist:
                 yield key

    @lru.get
    def exists(self, path):
        """Method to test exists."""
        path = self._init_path(path)
        logging.debug("Check exist os path=%s" % path)
        return self.mos.check_object_exist(self.bucket, path)

    @lru.remove
    def remove(self, path):
        """Method to remove."""
        path = self._init_path(path)
        try:
            self.mos.delete_object(self.bucket, path, None)
        except Exception:
            raise(exceptions.ConnectionError("Communication with mos fail"))

    def get_size(self, path):
        """Method to get the size."""
        path = self._init_path(path)
        logging.debug("Get file size of %s" % path)
        try:
            file_size = self.mos.get_object_filesize(self.bucket, path)
            if file_size is not None:
                logging.debug("Size of %s is %s" % (path, file_size))
                return file_size
            else:
                raise exceptions.FileNotFoundError("Unable to get size of %s" % path)
        except Exception:
            raise(exceptions.ConnectionError("Unable to get size of %s" % path))

