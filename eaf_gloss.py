#!/usr/bin/env python3
import xml.etree.ElementTree as ET
import re, subprocess
repl = [
    ['.*?<det><def><\\w+><([^/]+)/.*', r'DET-\1'],
    ['.*?(<v>[^/]*)/([^<>]+).*', '\\1-\\2'],
    ['[^<>]*<\\w+>(.*)', '\\1'],
    ['[^/]*/(\\w+).*', '\\1'],
    ['<([^<>]*)>', r'\1'],
    ['<', '.'],
    ['^\\.', ''],
    ['>', '']
]
for x in repl:
    x[0] = re.compile(x[0])
ANN_ID = 1
def addannot(src, txt):
    global ANN_ID
    ret = ET.Element('ANNOTATION')
    ref = ET.SubElement(ret, 'REF_ANNOTATION')
    val = ET.SubElement(ref, 'ANNOTATION_VALUE')
    ANN_ID += 1
    ref.set('ANNOTATION_ID', 'a%d' % ANN_ID)
    ref.set('ANNOTATION_REF', src[0].get('ANNOTATION_ID'))
    val.text = txt
    return ret
if __name__ == '__main__':
    import sys
    doc = ET.parse(sys.stdin)
    for node in doc.findall('[@ANNOTATION_ID]'):
        ANN_ID = max(ANN_ID, int(node.attrib['ANNOTATION_ID'][1:]))
    root = doc.getroot()
    for i in range(len(root)):
        if root[i].get('TIER_ID') == 'WAD phonetic':
            tier = ET.Element('TIER')
            tier.set('ANNOTATOR', "Apertium")
            tier.set('DEFAULT_LOCALE', "en")
            tier.set('LINGUISTIC_TYPE_REF', "apertium")
            tier.set('PARENT_REF', "WAD phonetic")
            tier.set('PARTICIPANT', root[i].get('PARTICIPANT'))
            tier.set('TIER_ID', 'Apertium gloss')
            txt = '\n'.join(x[0][0].text for x in root[i])
            proc = subprocess.Popen(['apertium', 'wad-eng-biltrans'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
            newtxt = proc.communicate(txt)[0]
            for p,r in repl.splitlines():
                newtxt = p.sub(r, newtxt)
            lines = newtxt.splitlines()
            for a,t in zip(root[i], lines):
                tier.append(addannot(annot, newtxt))
            root.insert(i+1, tier)
        elif root[i].tag == 'LINGUISTIC_TYPE':
            lingtype = ET.Element('LINGUISTIC_TYPE')
            lingtype.set('CONSTRAINTS', "Symbolic_Association"
            lingtype.set('GRAPHIC_REFERENCES', "false")
            lingtype.set('LINGUISTIC_TYPE_ID', "apertium")
            lingtype.set('TIME_ALIGNABLE', "false")
            root.insert(i+1, lingtype)
            break
    doc.write(sys.stdout)
