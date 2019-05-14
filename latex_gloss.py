#!/usr/bin/env python3
import re, subprocess
from subprocess import Popen, PIPE
repl = [
    ['.*?<det><def><\\w+><([^/]+)/.*', r'\\tsc{DET-\1}'],
    ['.*?(<v>[^/]*/[^<>]+).*', '\\1'],
    ['[^<>]*<\\w+>(.*)', '\\1'],
    ['[^/]*/(\\w+).*', '\\1'],
    ['<([^<>]*)>', r'\\tsc{\1}'],
    ['<', '.'],
    ['>', '']
]
for x in repl:
    x[0] = re.compile(x[0])
if __name__ == '__main__':
    stream_pat = re.compile(r'^[^^]*\^|\$[^^]*\^|\$[^^]*$', re.DOTALL | re.MULTILINE)
    import sys
    txt = sys.stdin.read()
    morph_proc = Popen(['apertium', '-d', '.', 'wad-eng-morph'], stdin=PIPE, stdout=PIPE, universal_newlines=True)
    gloss_proc = Popen(['apertium', '-d', '.', 'wad-eng-biltrans'], stdin=PIPE, stdout=PIPE, universal_newlines=True)
    trans_proc = Popen(['apertium', '-d', '.', 'wad-eng'], stdin=PIPE, stdout=PIPE, universal_newlines=True)
    morph = [x for x in stream_pat.split(morph_proc.communicate(txt)[0]) if x]
    gloss = [x for x in stream_pat.split(gloss_proc.communicate(txt)[0]) if x]
    trans = trans_proc.communicate(txt)[0].strip()
    surf = [x.split('/')[0] for x in morph]
    for i in range(len(gloss)):
        for p,r in repl:
            gloss[i] = p.sub(r, gloss[i])
    print(r'''\begin{exe}
\ex \gll %s \\\\
%s \\\\
\glt `%s' \\\\
\end{exe}''' % (' '.join(surf), ' '.join(gloss), trans))
