#!/bin/python

import xml.etree.cElementTree as ET
import os
import shutil

import argparse

parser = argparse.ArgumentParser(description='Create mytetra index hierarhy')
parser.add_argument('source_dir', type=str,
                    help='Set mytetra data source directory')

parser.add_argument('dest_dir', type=str, help='Set destenation directory')


parser.add_argument('--encrypted', dest='encrypted', default=False,
                    action=argparse.BooleanOptionalAction,
                    help='Enable encrypted nodes')

args = parser.parse_args()
source_dir = args.source_dir
dest_dir = args.dest_dir
enable_encrypted = args.encrypted


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
                + '<link rel="stylesheet" type="text/css" href="/static/nav.css">'
                + '<link rel="stylesheet" type="text/css" href="/static/list-item.css">'
                + '<link rel="stylesheet" type="text/css" href="/static/body.css">'
                + '<link rel="stylesheet" type="text/css" href="/static/href.css">'
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
        self.block = False
        self.crypt = False
        for (name, value) in record.attrib.items():
            if name == 'id':
                self.id = value
            elif name == 'name':
                self.name = value
            elif name == 'author':
                self.author = value
            elif name == 'url':
                self.url = value
            elif name == 'tags':
                self.tags = value
            elif name == 'ctime':
                self.ctime = value
            elif name == 'dir':
                self.dir = value
            elif name == 'file':
                self.file = value
            elif name == 'block':
                self.block = value == '1'
            elif name == 'crypt':
                self.crypt = value == '1'

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
        if enable_encrypted:
            return ('<div class="list-item" onclick="window.open(\'' + self.dir + '/' + self.file + '\', \'_self\')">'
                    + '<h3>' + self.name + '</h3>'
                    + '<div>Encrypted: ' +
                    ('yes' if self.crypt else 'no') + '</div>'
                    + '<div>Author: ' + self.author + '</div>'
                    + '<div>Tags: ' + self.tags + '</div>'
                    + '<div>Blocked: ' +
                    ('yes' if self.block else 'no') + '</div>'
                    + '</div>')
        else:
            return ('<div class="list-item" onclick="window.open(\'' + self.dir + '/' + self.file + '\', \'_self\')">'
                    + '<h3>' + self.name + '</h3>'
                    + '<div>Author: ' + self.author + '</div>'
                    + '<div>Tags: ' + self.tags + '</div>'
                    + '<div>Blocked: ' +
                    ('yes' if self.block else 'no') + '</div>'
                    + '</div>') if not self.crypt else ''


class NodeParser(object):
    def __init__(self, node):
        self.nodes = []
        self.records = []
        self.crypt = False
        self.id = ''
        self.name = ''
        self.icon = ''
        for (name, value) in node.attrib.items():
            if name == 'crypt':
                self.crypt = value == '1'
            elif name == 'id':
                self.id = value
            elif name == 'name':
                self.name = value
            elif name == 'icon':
                self.icon = value
        for item in node:
            if item.tag == 'node':
                self.nodes.append(NodeParser(item))
            elif item.tag == 'recordtable':
                for record in item:
                    r = RecordParser(record)
                    self.records.append(r)

    def construct(self):
        # Create directories
        for node in self.nodes:
            os.mkdir(node.id)
            os.chdir(node.id)
            for record in node.records:
                # Copy data
                copytree(source_dir + '/base/' + record.dir,
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
        if enable_encrypted:
            return ('<div class="list-item" onclick="window.open(\'' + self.id + '/index.html\', \'_self\')">'
                    + '<h3>' + self.name + '</h3>'
                    + '<div>Encrypted: ' +
                    ('yes' if self.crypt else 'no') + '</div>'
                    + '<div>Nodes: ' + str(self.nodes.__len__()) + '</div>'
                    + '<div>Records: ' + str(self.records.__len__()) + '</div>'
                    + '</div>')
        else:
            return ('<div class="list-item" onclick="window.open(\'' + self.id + '/index.html\', \'_self\')">'
                    + '<h3>' + self.name + '</h3>'
                    + '<div>Nodes: ' + str(self.nodes.__len__()) + '</div>'
                    + '<div>Records: ' + str(self.records.__len__()) + '</div>'
                    + '</div>') if not self.crypt else ''


class MytetraParser(object):

    def __init__(self, url, flag='url'):
        xml = self.getXml(url)

        for item in xml:
            if item.tag == 'format':
                for (name, value) in item.attrib.items():
                    if name == 'version':
                        self.version = value
                    if name == 'subversion':
                        self.subversion = value
            if item.tag == 'content':
                self.content = NodeParser(item)
        self.flag = flag

    def to_string(self):
        return {'version': self.version,
                'subversion': self.subversion,
                'content': self.content.to_string(),
                }

    def getXml(self, url):
        doc = ET.ElementTree(file=url)
        return doc.getroot()


def make_indexes(root: NodeParser):
    index = HtmlIndex(root.name, root.nodes, root.records)
    with open('index.html', 'a') as f:
        f.write(index.to_html())
    for node in root.nodes:
        os.chdir(node.id)
        make_indexes(node)
        os.chdir('..')


if __name__ == '__main__':
    copytree('static', dest_dir + 'static')
    os.chdir(dest_dir)
    mytetra = MytetraParser(source_dir + 'mytetra.xml')
    mytetra.content.construct()
    make_indexes(mytetra.content)
