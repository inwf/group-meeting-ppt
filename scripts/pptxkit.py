from lxml import etree

NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
A = NS['a']
P = NS['p']
R = NS['r']

etree.register_namespace('a', A)
etree.register_namespace('p', P)
etree.register_namespace('r', R)

YH = '微软雅黑'
TNR = 'Times New Roman'


def q(ns, tag):
    return f'{{{NS[ns]}}}{tag}'


def el(ns, tag, **attrs):
    e = etree.Element(q(ns, tag))
    for k, v in attrs.items():
        e.set(k, str(v))
    return e


def sub(parent, ns, tag, **attrs):
    e = el(ns, tag, **attrs)
    parent.append(e)
    return e


def txt(parent, value):
    e = el('a', 't')
    e.text = value
    parent.append(e)
    return e


def solid(color):
    f = el('a', 'solidFill')
    sub(f, 'a', 'srgbClr', val=color)
    return f


def scheme(name):
    f = el('a', 'solidFill')
    sub(f, 'a', 'schemeClr', val=name)
    return f


def rpr(run, sz, b=0, color=None, scheme_color=None, latin=YH, ea=YH, i=0, lang=None):
    p = el('a', 'rPr', sz=sz, b=b)
    if i:
        p.set('i', str(i))
    if lang:
        p.set('lang', lang)
    if color:
        p.append(solid(color))
    elif scheme_color:
        p.append(scheme(scheme_color))
    sub(p, 'a', 'latin', typeface=latin)
    sub(p, 'a', 'ea', typeface=ea)
    run.insert(0, p)
    return p


def para(body, runs, algn=None, lnspc=None, marL=None, indent=None, spcBef=None, bullet=None):
    p = el('a', 'p')
    pPr = sub(p, 'a', 'pPr')
    if marL is not None:
        pPr.set('marL', str(marL))
    if indent is not None:
        pPr.set('indent', str(indent))
    if algn:
        pPr.set('algn', algn)
    if lnspc:
        sub(sub(pPr, 'a', 'lnSpc'), 'a', 'spcPct', val=lnspc)
    if spcBef:
        sub(sub(pPr, 'a', 'spcBef'), 'a', 'spcPts', val=spcBef)
    if bullet:
        sub(pPr, 'a', 'buFont', typeface=bullet[0], panose='05000000000000000000',
            pitchFamily=2, charset=2)
        sub(pPr, 'a', 'buChar', char=bullet[1])
    for spec in runs:
        r = sub(p, 'a', 'r')
        rpr(r, **{k: v for k, v in spec.items() if k != 't'})
        txt(r, spec['t'])
    body.append(p)
    return p


def textbox(spTree, sid, name, off, ext, paras, anchor=None, wrap='square',
            autofit=True, lIns=45720, tIns=27432, rIns=45720, bIns=27432):
    sp = sub(spTree, 'p', 'sp')
    nv = sub(sp, 'p', 'nvSpPr')
    sub(nv, 'p', 'cNvPr', id=sid, name=name)
    sub(nv, 'p', 'cNvSpPr', txBox='1')
    sub(nv, 'p', 'nvPr')
    spPr = sub(sp, 'p', 'spPr')
    xfrm = sub(spPr, 'a', 'xfrm')
    sub(xfrm, 'a', 'off', x=off[0], y=off[1])
    sub(xfrm, 'a', 'ext', cx=ext[0], cy=ext[1])
    sub(spPr, 'a', 'prstGeom', prst='rect').append(el('a', 'avLst'))
    sub(spPr, 'a', 'noFill')
    txBody = sub(sp, 'p', 'txBody')
    bp = sub(txBody, 'a', 'bodyPr', wrap=wrap, lIns=lIns, tIns=tIns, rIns=rIns, bIns=bIns)
    if anchor:
        bp.set('anchor', anchor)
    if autofit:
        sub(bp, 'a', 'spAutoFit')
    sub(txBody, 'a', 'lstStyle')
    for spec in paras:
        para(txBody, spec['runs'], **{k: v for k, v in spec.items() if k != 'runs'})
    return sp


def picture(spTree, sid, name, off, ext, rid, descr=''):
    pic = sub(spTree, 'p', 'pic')
    nv = sub(pic, 'p', 'nvPicPr')
    sub(nv, 'p', 'cNvPr', id=sid, name=name, descr=descr)
    sub(nv, 'p', 'cNvPicPr').append(el('a', 'picLocks', noChangeAspect=1))
    sub(nv, 'p', 'nvPr')
    blip = sub(pic, 'p', 'blipFill')
    sub(blip, 'a', 'blip', **{f'{{{R}}}embed': rid})
    sub(blip, 'a', 'stretch').append(el('a', 'fillRect'))
    spPr = sub(pic, 'p', 'spPr')
    xfrm = sub(spPr, 'a', 'xfrm')
    sub(xfrm, 'a', 'off', x=off[0], y=off[1])
    sub(xfrm, 'a', 'ext', cx=ext[0], cy=ext[1])
    sub(spPr, 'a', 'prstGeom', prst='rect').append(el('a', 'avLst'))
    return pic


def sldnum(spTree, sid, name='灯片编号占位符 6', idx=4):
    sp = sub(spTree, 'p', 'sp')
    nv = sub(sp, 'p', 'nvSpPr')
    sub(nv, 'p', 'cNvPr', id=sid, name=name)
    sub(nv, 'p', 'cNvSpPr', txBox='1').append(el('a', 'spLocks', noGrp=1))
    sub(nv, 'p', 'nvPr').append(el('p', 'ph', type='sldNum', sz='quarter', idx=str(idx)))
    spPr = sub(sp, 'p', 'spPr')
    sub(spPr, 'a', 'noFill')
    sub(spPr, 'a', 'ln').append(el('a', 'noFill'))
    txBody = sub(sp, 'p', 'txBody')
    sub(txBody, 'a', 'bodyPr', anchor='ctr', anchorCtr=0)
    p = sub(txBody, 'a', 'p')
    pPr = sub(p, 'a', 'pPr', marL=0, indent=0, algn='r', eaLnBrk=1, hangingPunct=1)
    sub(sub(pPr, 'a', 'spcBef'), 'a', 'spcPct', val=0)
    sub(pPr, 'a', 'buSzTx')
    sub(pPr, 'a', 'buNone')
    fld = sub(p, 'a', 'fld', id='{9A0DB2DC-4C9A-4742-B13C-FB6460FD3503}', type='slidenum')
    f = sub(fld, 'a', 'rPr', lang='en-US', altLang='zh-CN', sz=1200, dirty=0)
    f.append(solid('898989'))
    sub(f, 'a', 'latin', typeface=TNR, panose='02020503050405090304', pitchFamily=18, charset=0)
    return sp


def slide_xml(spTree):
    sld = el('p', 'sld')
    cSld = sub(sld, 'p', 'cSld')
    cSld.append(spTree)
    sub(sld, 'p', 'clrMapOvr').append(el('a', 'masterClrMapping'))
    sub(sld, 'p', 'transition', advTm='0')
    return b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n' + \
        etree.tostring(sld, xml_declaration=False)


def new_spTree():
    tree = el('p', 'spTree')
    nv = sub(tree, 'p', 'nvGrpSpPr')
    sub(nv, 'p', 'cNvPr', id=1, name='')
    sub(nv, 'p', 'cNvGrpSpPr')
    sub(nv, 'p', 'nvPr')
    sub(tree, 'p', 'grpSpPr')
    return tree


def section_header(spTree, title, sid=2):
    textbox(spTree, sid, 'TextBox 1', (6483096, 9144), (1828800, 630936),
            [{'runs': [{'t': title, 'sz': 3200, 'b': 1, 'color': 'FFFFFF',
                        'latin': TNR}], 'algn': 'ctr'}],
            anchor='ctr', wrap='none')
    return spTree


TBL_STYLE = '{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}'


def table(spTree, sid, name, off, ext, rows, colw, hdr_h=365760, row_h=365760,
          hdr_sz=1300, sz=1300, hdr_color='014181'):
    gf = sub(spTree, 'p', 'graphicFrame')
    nv = sub(gf, 'p', 'nvGraphicFramePr')
    sub(nv, 'p', 'cNvPr', id=sid, name=name)
    sub(nv, 'p', 'cNvGraphicFramePr').append(el('a', 'graphicFrameLocks', noGrp=1))
    sub(nv, 'p', 'nvPr')
    xfrm = sub(gf, 'p', 'xfrm')
    sub(xfrm, 'a', 'off', x=off[0], y=off[1])
    sub(xfrm, 'a', 'ext', cx=ext[0], cy=ext[1])
    graphic = sub(gf, 'a', 'graphic')
    data = sub(graphic, 'a', 'graphicData',
               uri='http://schemas.openxmlformats.org/drawingml/2006/table')
    tbl = sub(data, 'a', 'tbl')
    sub(tbl, 'a', 'tblPr', firstRow=1, bandRow=1).append(
        (lambda e: (e.text, e)[1])(el('a', 'tableStyleId')))
    tbl.find(f'{{{A}}}tblPr/{{{A}}}tableStyleId').text = TBL_STYLE
    grid = sub(tbl, 'a', 'tblGrid')
    for w in colw:
        sub(grid, 'a', 'gridCol', w=w)
    for ri, row in enumerate(rows):
        tr = sub(tbl, 'a', 'tr', h=hdr_h if ri == 0 else row_h)
        for ci, cell in enumerate(row):
            tc = sub(tr, 'a', 'tc')
            body = sub(tc, 'a', 'txBody')
            sub(body, 'a', 'bodyPr', wrap='square')
            sub(body, 'a', 'lstStyle')
            p = sub(body, 'a', 'p')
            r = sub(p, 'a', 'r')
            if ri == 0:
                rpr(r, sz=hdr_sz, b=1, color='FFFFFF')
            else:
                rpr(r, sz=sz, b=0, color='000000')
            txt(r, cell)
            tcPr = sub(tc, 'a', 'tcPr', marL=45720, marR=45720)
            tcPr.append(solid(hdr_color if ri == 0 else 'FFFFFF'))
    return gf


def fit(box, iw, ih):
    bx, by, bw, bh = box
    k = min(bw / iw, bh / ih)
    cx, cy = int(iw * k), int(ih * k)
    ox = bx + (bw - cx) // 2
    oy = by + (bh - cy) // 2
    return (ox, oy), (cx, cy)
