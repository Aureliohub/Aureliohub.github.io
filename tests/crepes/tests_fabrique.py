# Fabrique les variantes de test du correcteur des crêpes à partir du corrigé.
# Usage : python3 tests_fabrique.py crepes_reference.docx .
import re, shutil, zipfile, os, sys
SRC = sys.argv[1]; OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
def variante(nom, transfo):
    z = zipfile.ZipFile(SRC)
    fichiers = {n: z.read(n) for n in z.namelist()}
    transfo(fichiers)
    with zipfile.ZipFile(os.path.join(OUT, nom), 'w', zipfile.ZIP_DEFLATED) as o:
        for n, d in fichiers.items(): o.writestr(n, d)
def txt(f, n): return f[n].decode('utf8')
def police(f):
    for n in ('word/document.xml', 'word/numbering.xml'):
        f[n] = txt(f, n).replace('Comic Sans MS', 'Arial').encode('utf8')
def marges(f):
    s = txt(f, 'word/document.xml')
    s = re.sub(r'<w:pgMar[^/]*/>', '<w:pgMar w:top="1417" w:right="1417" w:bottom="1417" w:left="1417" w:header="0" w:footer="709" w:gutter="0"/>', s)
    f['word/document.xml'] = s.encode('utf8')
def enligne(f):
    s = txt(f, 'word/document.xml')
    s = s.replace('behindDoc="1"', 'behindDoc="0"')
    s = re.sub(r'<wp:anchor[^>]*>', '<wp:inline>', s)
    s = s.replace('</wp:anchor>', '</wp:inline>')
    s = re.sub(r'<wp:simplePos[^>]*/>|<wp:positionH.*?</wp:positionH>|<wp:positionV.*?</wp:positionV>|<wp:wrapNone\s*/>', '', s, flags=re.S)
    f['word/document.xml'] = s.encode('utf8')
def liste(f):
    s = txt(f, 'word/document.xml')
    s = re.sub(r'<w:numPr>.*?</w:numPr>', '', s, flags=re.S)
    n = [0]
    def numerote(m):
        n[0] += 1
        return m.group(0).replace('<w:t xml:space="preserve">', '<w:t xml:space="preserve">%d. ' % n[0], 1)
    for cible in ['Verse la farine', 'Casse les', 'Ajoute l', 'Laisse reposer', 'Fais chauffer', 'Laisse cuire et']:
        s = re.sub(r'<w:r>(?:(?!</w:r>).)*?<w:t xml:space="preserve">' + cible + r'(?:(?!</w:r>).)*?</w:r>', numerote, s, count=1, flags=re.S)
    f['word/document.xml'] = s.encode('utf8')
def superpose(f):
    s = txt(f, 'word/document.xml')
    s = re.sub(r'(<wp:positionH relativeFrom="column">\s*<wp:posOffset>)-?\d+', r'\g<1>1080000', s)
    s = re.sub(r'(<wp:positionV relativeFrom="paragraph">\s*<wp:posOffset>)-?\d+', r'\g<1>180000', s)
    f['word/document.xml'] = s.encode('utf8')
def degrade(f):
    police(f); marges(f); liste(f)
    f['word/document.xml'] = txt(f, 'word/document.xml').replace('<w:b/>', '').encode('utf8')
for nom, t in [('police', police), ('marges', marges), ('enligne', enligne), ('liste_tapee', liste), ('superpose', superpose), ('degrade', degrade)]:
    variante('crepes_TEST_%s.docx' % nom, t)
shutil.copy(SRC, os.path.join(OUT, 'crepes_reference.docx'))
