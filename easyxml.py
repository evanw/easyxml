# EasyXML: An easy way to generate XML output in Python
# Copyright (c) 2010 Evan Wallace
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import xml.dom.minidom
import re

class EasyXML:
    '''
    EasyXML is an easy way to output to XML using Python attribute syntax:

      books = EasyXML('books')
      books.book(title='Example A')
      books.book.author(name='John Smith', age=57)
      books.book.publisher(name='Publisher A')
      books.book(title='Example B')
      books.book.author(name='Jane Doe', age=30)
      books.book.author(name='James Cutter', age=45)
      books.book.publisher(name='Publisher B')
      print str(books)

    The above code produces the following XML:

      <books>
        <book title="Example A">
          <author name="John Smith" age="57"/>
          <publisher name="Publisher A"/>
        </book>
        <book title="Example B">
          <author name="Jane Doe" age="30"/>
          <author name="James Cutter" age="45"/>
          <publisher name="Publisher B"/>
        </book>
      </books>
    '''

    def __init__(self, name):
        '''
        Construct a new EasyXML node with a certain name.  Any keyword
        arguments are set as attributes on the new element.  This should
        only be used to create the root node, all child nodes should be
        created with the attribute syntax in the above example.
        '''
        self._parent = None
        self._name = name
        self._elements = []
        self._attributes = {}
        self._element_map = {}

    def __getattr__(self, name):
        '''
        If an element with the given name has already been added, just
        return that element.  Otherwise, return a new element with the
        given name and this object as a parent.  This does NOT add the
        returned element to this object yet, you still need to call the
        returned element.
        '''
        if name.startswith('_'):
            return object.__getattr__(self, name)
        if name in self._element_map:
            return self._element_map[name]
        element = EasyXML(name)
        element._parent = self
        return element

    def __call__(self, **kwargs):
        '''
        Add a new element with our name to our parent element.  Any keyword
        arguments are set as attributes on the new element.  This actually
        adds new elements as far up the parent chain as needed, allowing
        the following code to work:

          root = EasyXML('root')
          root.a.b.c()
          root.a.b.c()
          root.a()
          root.a.b.c()
          root.a.b.c()

        The above code produces the following XML:

          <root>
            <a>
              <b>
                <c/>
                <c/>
              </b>
            </a>
            <a>
              <b>
                <c/>
                <c/>
              </b>
            </a>
          </root>
        '''
        e = EasyXML(self._name)
        e._parent = self._parent
        e._attributes = kwargs
        while e._parent and e not in e._parent._element_map.values():
            e._parent._elements.append(e)
            e._parent._element_map[e._name] = e
            e = e._parent

    def __str__(self):
        '''
        Return generated XML representing the stored element tree.
        '''
        def to_xml(obj):
            element = doc.createElement(obj._name)
            for k in obj._attributes:
                element.setAttribute(k, str(obj._attributes[k]))
            for e in obj._elements:
                element.appendChild(to_xml(e))
            return element

        doc = xml.dom.minidom.Document()
        doc.appendChild(to_xml(self))
        return re.sub(r'<\?xml.*\?>', '', doc.toprettyxml(indent='  ')).strip()
