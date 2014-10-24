import json
from bs4 import BeautifulSoup,NavigableString,Tag
from collections import OrderedDict

def hasDictValue(data,multikey):
    try:
        keys=multikey.split('.',1)

        if isinstance(data,dict) and keys[0] != '':
            if len(keys) > 1:
                value=data.get(keys[0],"")
                value = hasDictValue(value,keys[1])
            else:
                value = keys[0] in data

        else:
            value = False

        return value
    except Exception as e:
        return False

def dictToText(value):
    if isinstance(value,dict):
        return " ".join([dictToText(value[key]) for key in value])
    elif isinstance(value,list):
        return " ".join([dictToText(lval) for lval in value])
    elif isinstance(value, (int, long)):
        return str(value)
    else:
        return value

def searchDictKeys(value,search):
    if isinstance(value,dict):
        out = [dictToText(value[key]) if key == search else searchDictKeys(value[key],search) for key in value]
    elif isinstance(value,list):
        out = [searchDictKeys(lval,search) for lval in value]
    else:
        return ""

    return " ".join([val for val in out if val != ""]).strip("\n\t ")


def getDictValue(data,multikey,dump=True):
    try:
        keys=multikey.split('.',1)
        if len(keys) == 1:
            dumptype = keys[0].split(' ',1)
            keys[0] = dumptype[0]
            dumptype = dumptype[1] if len(dumptype) > 1 else None


        try:
            if isinstance(data,dict) and (keys[0] != ''):
                value=data[keys[0]]
            elif type(data) is list and keys[0] != '':
                value=data[int(keys[0])]
            elif keys[0] == '':
                value = data
            else:
                value = ''

            if len(keys) > 1:
                value = getDictValue(value,keys[1],dump)
        except:
            if keys[0] == '*':
                listkey = keys[1] if len(keys) > 1 else ''

                valuelist=[]
                if isinstance(data,dict):
                    data = [data[key] for key in data]
                for elem in data:
                    valuelist.append(getDictValue(elem,listkey,dump))
                value = ";".join([val for val in valuelist if val !=""])
            else:
                value = ''

        if dump and (isinstance(value,dict) or type(value) is list):
            if dumptype is not None:
                return searchDictKeys(value,dumptype)
            else:
                return json.dumps(value)
        elif dump and (isinstance(value, (int, long))):
            return str(value)
        else:
            return value
    except Exception as e:
        return ""

def filterDictValue(data,multikey,dump=True):
    try:
        keys=multikey.split('.',1)

        if isinstance(data,dict) and keys[0] != '':
            value = { key: data[key] for key in data.keys() if key != keys[0]}
            if len(keys) > 1:
                value[keys[0]] = filterDictValue(data[keys[0]],keys[1],False)
            if not len(value):
                value = None

        elif type(data) is list and keys[0] != '':
            try:
                value=data
                if len(keys) > 1:
                    value[int(keys[0])] = getDictValue(value[int(keys[0])],keys[1],False)
                else:
                    value[int(keys[0])] = ''
            except:
                if keys[0] == '*' and len(keys) > 1:
                    listkey = keys[1]
                elif keys[0] == '*':
                    listkey = ''
                else:
                    listkey = keys[0]

                valuelist=[]
                for elem in data:
                    valuelist.append(filterDictValue(elem,listkey,False))
                value = valuelist

        else:
            value = ''


        if dump and (isinstance(value,dict) or type(value) is list):
            return json.dumps(value)
        else:
            return value

    except Exception as e:
        return ""

def recursiveIterKeys(value,prefix=None):
    if isinstance(value,dict):
        keys = value.iterkeys()
    elif isinstance(value,list):
        keys = range(len(value))

    for key in keys:
        if isinstance(value[key],dict) or isinstance(value[key],list):
            for subkey in recursiveIterKeys(value[key],str(key)):
                fullkey = subkey if prefix is None else ".".join([prefix,subkey])
                yield fullkey
        else:
            fullkey = str(key) if prefix is None else ".".join([prefix,str(key)])
            yield fullkey

def htmlToJson(data,csskey=None):
    soup = BeautifulSoup(data)

    def parseSoup(element):
        out = []
        out.append({'_tagname_'+element.name})
        for attr in element.attrs:
            out.append({'_'+attr+'_':element[attr]})
        for child in element.children:
            if isinstance(child,NavigableString):
                value = unicode(child).strip("\n\t ")
                if value != '':
                    out.append({'_text_':value})
            elif isinstance(child,Tag):
                id = str(child.get('id',''))
                key = child.name+'#'+id if id != '' else child.name
                out.append({key:parseSoup(child)})
        return out

    output = []
    if csskey is not None:
        for part in soup.select(csskey):
            output.extend(parseSoup(part))
    else:
        output.extend(parseSoup(soup))

    return output

