import re
import sys
import random
import time
import datetime
import copy
#import plotly.plotly as py
#import plotly.figure_factory as FF
import pdb

data=[]
colors=[]
text = []
n_colors=[]
n_text=[]

def gettime(strtime):
    hours = strtime[11:13]
    mins = strtime[14:16]
    senconds = strtime[17:19]
    msenconds = strtime[20:]
    return int(hours)*60*60 + int(mins)*60 + int(senconds) + float(msenconds) / 1000
def getdata(filename):
    #pdb.set_trace()
    #filename = "/var/log/neutron/server.log"
    #filename = "/tmp/server"
    #filename = sys.argv[1]
    logfile = open(filename, 'r')

    isiom = re.compile('\[iom]')
    splitre = re.compile('\[[^]]*]' )
    findid = re.compile('req[\w\-]*\s')
    isbegin = re.compile('\[begin]')

    ids = []
    outputs = []
    last = []
    tmp = []
    rdata=[]

    stack_name=[]
    stack_list=[]

    child_list=[]
    output_list=[]
    tmp_list=[]
    arg_list=[]
    tree_dict={}

    while True:
        line = logfile.readline()
        if line:
            print "line:%s\n\n" % line
            if isiom.search(line):
                line = line[0:-1]
                requestid = findid.search(splitre.search(line).group(0)).group(0)
                if requestid not in ids:
                    ids.append(requestid)
                    outputs.append([])
                    #last.append(outputs[-1])
                    last.append([])

                splited = splitre.split(line)
                #print splited
                #0-time,4-lastfun,5-fun,6-used/args, 7-args
                logtime = splited[0][0:23]
                n = ids.index(requestid)
                if isbegin.search(line):
                    record = {"request_id":requestid,
                              "function_name":splited[5],
                              "sub_function":[],
                              "start_time":logtime,
                              "stop_time":'',
                              "used_time":'-1'}

                    arg_list.append(record)
                    stack_name.append(splited[5])
                    tree_dict={'name':splited[5], 'arg':record, 'child':[]}
                    stack_list.append(tree_dict)
                else:
                    if stack_list[-1]['name'] == splited[5]:
                        stack_list[-1]['arg']['used_time'] = splited[6]
                        stack_list[-1]['arg']['stop_time'] = logtime
                        stack_list[-1]['arg']['color'] = (0,(random.randrange(0,255,1)), (random.randrange(0,255,1)))
                        print stack_list[-1]['arg']['color']

                        if stack_list[0]['name'] == splited[5]:
                            tmp_list=copy.deepcopy(stack_list)
                            output_list.append(tmp_list)
                            tmp_list=[]
                        else:
                            stack_list[-2]['child'].append( stack_list[-1])

                        stack_list.pop()
        else:
            break

    return output_list


def one_dim(lists):
    l_new=[j for i in lists for j in i]
    return l_new


def get_child(child=None):
    if isinstance(child,dict):
        if child:
            child_lists = child.get("child",None)
            #one_dim(child_lists)
            return child_lists
        else:
            return None

def parse_child(tr=None, fd=None):
    child = tr['child']
    """
    case:child is None, same parent tree.
    """
    if not child:
        print "<span><i class=\"\"></i> %s</span>" % (tr['name'])
        html_span = "<span><i class=\"\"></i> %s</span>\n" % (tr['name'])
        fd.write(html_span)
        print "<a title=%s >\n<canvas width=%s height=\"10\" style=\"border:2px solid #%s;\"></canvas>\n</a>" % (tr['arg']['used_time'], 50*float(tr['arg']['used_time']), rgb2hex(tr['arg']['color']))
        html_canvas = "<a title=%s>\n <canvas width=%s height=\"10\" style=\"border:2px solid #%s;\"></canvas>\n</a>" % (tr['arg']['used_time'], 50*float(tr['arg']['used_time']), rgb2hex(tr['arg']['color']))
        fd.write(html_canvas)
        return None
    else:
        parse_parent(tr,fd)



def parse_parent(tr=None,fd=None):
    assert(tr)
    #pdb.set_trace()
    print "<span><i class=\"class-minus\"></i> %s</span>" % (tr['name'])
    html_span = "<span><i class=\"class-minus\"></i> %s</span>\n" % (tr['name'])
    fd.write(html_span)
    print "<a title=%s >\n<canvas width=%s height=\"10\" style=\"border:2px solid #%s;\"></canvas>\n</a>" % (tr['arg']['used_time'], 50*float(tr['arg']['used_time']), rgb2hex(tr['arg']['color']))
    html_canvas = "<a title=%s>\n <canvas width=%s height=\"10\" style=\"border:2px solid #%s;\"></canvas>\n</a>" % (tr['arg']['used_time'], 50*float(tr['arg']['used_time']), rgb2hex(tr['arg']['color']))
    fd.write(html_canvas)
    print "<ul>"
    fd.write("<ul>\n")

    child = get_child(tr)
    if child:
        for l in child:
            print "<li>"
            fd.write("<li>\n")
            parse_child(l,fd)
            print "</li>"
            fd.write("</li>\n")

    print "</ul>"
    fd.write("</ul>\n")

def parse(tr=None,fd=None):
    assert(tr)
    print "<ul><li>"
    fd.write("<ul><li>\n")
    parse_parent(tr,fd)
    print "</li></ul>"
    fd.write("</li></ul>\n")

def rgb2hex(rgbcolor):
    Red, Green, Blue = rgbcolor
    HEX = '%02x%02x%02x' % (Red, Green, Blue)
    return HEX

def make_html(logdata):
    fd = open('index.html','w')

    """
    write head
    """
    html_head = '<!DOCTYPE html>\n'\
            '<html>\n'\
            '<head>\n'\
            '<title>IOM</title>\n'\
            '<style>\n'\
            '@import "css/mytree.css";\n'\
            '@import "css/pic.css";\n'\
            '@import "css/bootstrap.min.css";\n'\
            '</style>\n'\
            '</head>\n'\
            '<script src="js/jquery-3.2.0.min.js"></script>\n'\
            '<script src="js/tree_jq.js"></script>\n'\
            '<body>\n'\
            '<div class="tree " >\n'
    fd.write(html_head)

    """
    write body
    """
    data = one_dim(logdata)
    for l in data:
        parse(l,fd)

    """
    write tail
    """
    html_tail = '</div>\n'\
            '</html>\n'
    fd.write(html_tail)

    fd.close()



dirname = sys.argv[1]
logdata = getdata(dirname)
print logdata
make_html(logdata)


