#!/bin/python

import xml.dom.minidom
import os
import shutil


sourse_dir = '/tmp/test/base/'


# class IndexElem(object):
#     def __init__(self, title: str, href: str, records: int, nodes: int, crypt: bool):
#         self.title = title
#         self.href = href
#         self.records = records
#         self.nodes = nodes
#         self.crypt = crypt

#     def to_html(self):
#         return '<p class="list-item"><a href="{}" class="href">{}</a></p>'.format(self.href, self.title)


class HtmlIndex(object):
    def __init__(self, title: str, nodes: list, records: list):
        self.title = title
        self.nodes = nodes
        self.records = records

    def to_html(self):
        nodes_html = ''
        for node in self.nodes:
            nodes_html += node.to_html()
        records_html = ''
        for record in self.records:
            records_html += record.to_html()
        return ('<html>'
                + '<head>'
                + '<title>' + self.title + '</title>'
                + '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'
                + '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">'
                + '<link rel="stylesheet" type="text/css" href="nav.css">'
                + '<link rel="stylesheet" type="text/css" href="list-item.css">'
                + '<link rel="stylesheet" type="text/css" href="body.css">'
                + '<link rel="stylesheet" type="text/css" href="href.css">'
                + '</head>'
                + '<body>'
                + '<div class="topnav">'
                + '<a href="index.html" class="href">' + self.title + '</a>'
                + '</div>'
                + '<div>'
                + nodes_html
                + records_html
                + '</div>'
                + '</body>'
                + '</html>')


def copytree(src, dst, symlinks=False, ignore=None):
    os.mkdir(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


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

    def to_html(self):
        return ('<p class="list-item"><a href="' + self.dir + '/' + self.file + '" class="href">'
                + self.name + '</a></p>')


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
            node = NodeParser(node_elem)
            print('Adding ' + node.name)
            self.nodes.append(node)
        try:
            records_elems = node.getElementsByTagName(
                'recordtable')[0].getElementsByTagName('record')
            for record_elem in records_elems:
                self.records.append(RecordParser(record_elem))
        except:
            self.records = []

    def construct(self):
        # Create directories
        for node in self.nodes:
            os.mkdir(node.id)
            os.chdir(node.id)
            for record in self.records:
                # Copy data
                copytree(sourse_dir + record.dir,
                         os.path.abspath(os.getcwd()) + '/' + record.dir)
                # Construct child
            node.construct()
        if self.id.__len__() > 0:
            # Return back
            os.chdir('..')

    def to_string(self):
        return {'crypt': self.crypt,
                'id': self.id,
                'name': self.name,
                'icon': self.icon,
                'nodes': list(map(NodeParser.to_string, self.nodes)),
                'records': list(map(RecordParser.to_string, self.records)),
                }

    def to_html(self):
        return ('<p class="list-item"><a href="' + self.id + '" class="href">Node:'
                + self.name + '</a>' + (', encrypted' if self.crypt else '') + '</p>')


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
    # index = HtmlIndex('title', [IndexElem('1', '1', 0, 0, False), IndexElem('2', '2', 0, 0, False), IndexElem('3', '3', 0, 0, False)])
    # print(index.to_html())
    mytetra = MytetraParser("mytetra.xml")
    # print(mytetra.to_string())
    # mytetra.content.construct()
    # print(mytetra.content.to_html())
    index = HtmlIndex('Root', mytetra.content.nodes, [])
    index.to_html()
    # print(index.to_html())
