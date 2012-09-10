#! /usr/bin/env python

import sys, os

def find_prefix(l, p):
    for i, v in enumerate(l):
        if v.find(p) == 0:
            return i
    return -1

def process_method(m):
    m = m.strip()
    if m.find('//') != -1:
        m = m[:m.find('//')]
    m = m.strip()

    q = '-'
    if m.find('-') != -1:
        m = m[m.find('-') + 1:]
        q = '-'
    if m.find('+') != -1:
        m = m[m.find('+') + 1:]
        q = '+'
    m = m.strip()

    if m.find('(') == 0:
        m = m[m.find(')') + 1:]
    m = m.strip()

    while m.find('(') != -1:
        o = m.find('(')
        c = m.find(')')
        n = 1 if m[c + 1] == ' ' else 0
        n += m[c + 1 + n:].find(' ') if ' ' in m[c + 1 + n:] else len(m[c + 1 + n:])
        m = m[:o] + m[c + 1 + n:]
    
    if m[len(m) - 1] == ';':
        m = m[:-1]
    m = m.strip()

    m = m.replace(' ', '')
    m = q + m

    return m

def process_property(p):
    p = p.strip()
    if p.find('//') != -1:
        p = p[:p.find('//')]
    p = p.strip()

    p = p[len('@property'):]
    p = p.strip()

    attrs = ['readwrite']
    if p[0] == '(':
        attrs = p[1:p.find(')')].split(',')
        attrs = [a.strip() for a in attrs]

        p = p[p.find(')') + 1:]
        p.strip()
   
    if p[len(p) - 1] == ';':
        p = p[:-1]
    p = p.strip()

    name = p[max(p.rfind(' '), p.rfind('*'), p.rfind(']')) + 1:].strip()
   
    getter = name
    if find_prefix(attrs, 'getter') != -1:
        getter = attrs[find_prefix(attrs, 'getter')]
        getter = getter[getter.find('=') + 1:].strip()
    methods = [getter]
    
    if find_prefix(attrs, 'readonly') == -1:
        setter = 'set%s:' % (name[0].capitalize() + name[1:])
        if find_prefix(attrs, 'setter') != -1:
            setter = attrs[find_prefix(attrs, 'setter')]
            setter = setter[setter.find('=') + 1:].strip()
        methods.append(setter)

    methods = ['-'+m for m in methods]
    return methods

def find_methods(header):
    header = header.split('\n')
    out = {}

    while find_prefix(header, '@interface') != -1:
        cls = header[find_prefix(header, '@interface')]
        cls = cls[len('@interface '):cls.find(' : ')] if ' : ' in cls else cls[len('@interface '):]

        header = header[find_prefix(header, '@interface') + 1:]
        working = header[:find_prefix(header, '@end')]

        methods = []
        for m in working:
            s = m.strip()
            if s.find('^') != -1:
                continue
            elif s.find('-') == 0 or s.find('+') == 0:
                methods.append(process_method(m))
            elif s.find('@property') == 0:
                methods = methods + process_property(m)

        out[cls] = methods

    return out

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Usage: %s iPhonePrivate.h SpringBoard/" % sys.argv[0]
        sys.exit(0)

    header = open(sys.argv[1], 'r').read()
    classd = ''.join(open(os.path.join(sys.argv[2], f), 'r').read() for f in os.listdir(sys.argv[2])) if os.path.isdir(sys.argv[2]) else open(sys.argv[2], 'r').read()

    header_methods = find_methods(header)
    classd_methods = find_methods(classd)

    #print header_methods
    #print classd_methods
   
    for k in header_methods:
        if k in classd_methods:
            hv = header_methods[k] 
            cv = classd_methods[k] 

            for m in hv:
                if m not in cv:
                    print '%s: %s' % (k, m)
        elif k.find('(') == -1:
            print "Missing class: %s" % k
    



