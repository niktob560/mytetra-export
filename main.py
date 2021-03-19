#!/bin/python

import xml.dom.minidom
import os


class RecordParser(object):
    def __init__(self, record):
        self.id = record.getAttribute('id')
        self.name = record.getAttribute('name')
        self.author = record.getAttribute('author')
        self.url = record.getAttribute('url')
        self.tags = record.getAttribute('tags')
        self.ctime = record.getAttribute('ctime')
        self.dir = record.getAttribute('dir')
        self.file = record.getAttribute('file')
        self.block = record.getAttribute('block') == '1'

    def to_string(self):
        return {'id': self.id,
                'name': self.name,
                'author': self.author,
                'url': self.url,
                'tags': self.tags,
                'ctime': self.ctime,
                'dir': self.dir,
                'file': self.file,
                'block': self.block,
                }


class NodeParser(object):
    def __init__(self, node):
        self.crypt = node.getAttribute('crypt') == '1'
        self.id = node.getAttribute('id')
        self.name = node.getAttribute('name')
        self.icon = node.getAttribute('icon')
        nodes_elems = node.getElementsByTagName('node')
        self.nodes = []
        self.records = []
        for node_elem in nodes_elems:
            self.nodes.append(NodeParser(node_elem))
        try:
            records_elems = node.getElementsByTagName(
                'recordtable')[0].getElementsByTagName('record')
            for record_elem in records_elems:
                self.records.append(RecordParser(record_elem))
        except:
            self.records = []

    def construct(self):
        print('construct from {}'.format(os.getcwd()))
        if self.id.__len__() > 0:
            print('mkdir {}'.format(self.id))
            os.mkdir(self.id)
            os.chdir(self.id)
        for node in self.nodes:
            node.construct()
        if self.id.__len__() > 0:
            os.chdir('..')

    def to_string(self):
        return {'crypt': self.crypt,
                'id': self.id,
                'name': self.name,
                'icon': self.icon,
                'nodes': list(map(NodeParser.to_string, self.nodes)),
                'records': list(map(RecordParser.to_string, self.records)),
                }


class MytetraParser(object):

    def __init__(self, url, flag='url'):
        xml = self.getXml(url)
        fmt = xml.getElementsByTagName('format')[0]
        self.version = int(fmt.getAttribute('version'))
        self.subversion = int(fmt.getAttribute('subversion'))
        self.content = NodeParser(xml.getElementsByTagName('content')[0])
        self.flag = flag

    def to_string(self):
        return {'version': self.version,
                'subversion': self.subversion,
                'content': self.content.to_string(),
                }

    def getXml(self, url):
        doc = xml.dom.minidom.parse(url)
        node = doc.documentElement
        return node


if __name__ == "__main__":
    mytetra = MytetraParser("mytetra.xml")
    # print(mytetra.to_string())
    mytetra.content.construct()
