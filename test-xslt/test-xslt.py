from lxml import etree

f = open('c:/deffer/SPAT_WEB/source.xml ')
tf = open('c:/deffer/SPAT_WEB/transform.xsl')

xslt_doc = etree.parse(tf)
transform = etree.XSLT(xslt_doc)
doc = etree.parse(f)

result = transform.apply(doc)

print(result)

outf = open ('c:/deffer/SPAT_WEB/result.xml', 'w')
outf.write(str(result))
outf.close()
