#!/bin/python

import xml.dom.minidom


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
        nodes_elems = node.getElementsByTagName('node')
        self.nodes = []
        for node_elem in nodes_elems:
            self.nodes.append(NodeParser(node_elem))
        records_elems = node.getElementsByTagName(
            'recordtable')[0].getElementsByTagName('record')
        self.records = []
        for record_elem in records_elems:
            self.records.append(RecordParser(record_elem))

    def to_string(self):
        return {'crypt': self.crypt,
                'id': self.id,
                'name': self.name,
                'nodes': list(map(NodeParser.to_string, self.nodes)),
                'records': list(map(RecordParser.to_string, self.records)),
                }


class ContentParser(object):
    def __init__(self, content):
        self.nodes = list(
            map(NodeParser, content.getElementsByTagName('node')))
    
    def to_string(self):
        return {'nodes': list(map(NodeParser.to_string, self.nodes))}


class MytetraParser(object):

    def __init__(self, url, flag='url'):
        xml = self.getXml(url)
        format = xml.getElementsByTagName('format')[0]
        self.version = int(format.getAttribute('version'))
        self.subversion = int(format.getAttribute('subversion'))
        self.content = ContentParser(xml.getElementsByTagName('content')[0])
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
    appt = MytetraParser("mytetra.xml")
    print(appt.to_string())