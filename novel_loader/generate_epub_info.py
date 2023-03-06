import os


metadata = """
    <metadata xmlns="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{title}</dc:title>
        <dc:creator>{author}</dc:creator>
        <dc:date>{date}</dc:date>
        <dc:language>{language}</dc:language>
        <dc:identifier id="bookid" scheme="calibre">{identifier}</dc:identifier>
        <meta name="cover" content="cover.jpg"/>
        <meta name="calibre:title_sort" content="{title}"/>
        <meta name="calibre:author_link_map" content="{author}"/>

    </metadata>
"""

manifest = """<manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="css" href="Styles/main.css" media-type="text/css"/>
        <item id="cover.jpg" href="Images/cover.jpg" media-type="image/jpeg"/>
        {items}
    </manifest>
"""

item = """<item id="{id}" href="{href}" media-type="{type}"/>
"""

spine = """<spine toc="ncx">
    {itemrefs}
    </spine>
"""

itemref = """   <itemref idref="{page}.xhtml"/>
"""

package = """<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">
    {metadata}
    {manifest}
    {spine}

</package>
"""

def generate_opf(title, language, date, author, identifier, item_path, chapter):
    items=''
    for Text_or_image,path in enumerate(item_path):
        if Text_or_image == 0:
            all_file=os.listdir(path)
            for file in all_file:
                items+=item.format(
                    id=file,
                    href='Text/'+file,
                    type='application/xhtml+xml',
                )
        else:
            all_file=os.listdir(path)
            for file in all_file:
                items+=item.format(
                    id=file,
                    href='Images/'+file,
                    type='image/jpeg',
                )

    itemrefs=''
    for page in chapter:
        itemrefs+=itemref.format(
            page=page
        )

    opf = package.format(
        metadata=metadata.format(
            title=title,
            author=author,
            date=date,
            language=language,
            identifier=identifier,
        ),
        manifest=manifest.format(
            items=items
        ),
        spine=spine.format(
            itemrefs=itemrefs
        )
    )
    return opf

ncx = """
<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="{identifier}"/>
        <meta name="dtb:depth" content="1"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{title}</text>
    </docTitle>
    <navMap>
        {navpoints}
    </navMap>
</ncx>
"""

navpoint = """
        <navPoint id="{id}" playOrder="{playOrder}">
            <navLabel>
                <text>{text}</text>
            </navLabel>
            <content src="{src}"/>
        </navPoint>
"""

def generate_toc(title, identifier, catalog_page_table):
    navpoints=''
    for id,text in enumerate(catalog_page_table):
        navpoints+=navpoint.format(
            id=str(id+1),
            playOrder=str(id+1),
            text=text,
            src='Text/'+text+'.xhtml',
        )
    toc = ncx.format(
        title=title,
        identifier=identifier,
        navpoints=navpoints
    )
    return toc

html= """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
  "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{title}</title>
</head>
<body>
    {body}
</body>
</html>
"""

def generate_xhtml(title,body):
    xhtml=html.format(
        title=title,
        body=body,
    )
    return xhtml

css="""
body{
	padding: 0%;
	margin-top: 0%;
	margin-bottom: 0%;
	margin-left: 1%;
	margin-right: 1%;
	line-height:120%;
	text-align: justify;
}
p {
	text-indent:2em;
	display:block;
	line-height:1.3em;
	margin-top:0.6em;
	margin-bottom:0.6em;
}
div {
	margin:0px;
	padding:0px;
	line-height:120%;
	text-align: justify;}
h1 {
	line-height:130%;
	text-align: center;
	font-weight:bold;
	font-size:xx-large;
}
h2 {
	line-height:130%;
	text-align: center;
	font-weight:bold;
	font-size:1.6em;
	margin-bottom: 1.5em;
}
h3 {
	line-height:130%;
	font-weight:bold;
	font-size:large;
}
.alr {
    font-size: 1.1em;
    line-height: 1.2
	text-indent:2.5em;
    }
.alg {
    font-size: 1.15em;
    line-height: 1.2
	text-indent:2.5em;
    }
.noi2 {
	text-indent:0em;
}

.noi {
	text-indent:0em;
	text-align: center;
}
.int {
	margin-left: 5%;
	margin-right: 5%;
}
a{
    text-decoration:none;
	color:#000000;
}
"""

def generate_css():
    return css

container='''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>
'''
def generate_container():
    return container