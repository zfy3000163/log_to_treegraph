import re
import sys
import random
import time
import datetime
import copy
#import plotly.plotly as py
#import plotly.figure_factory as FF
import pdb

Level=50

class Log_to_graph():

    def file_format(self, filename=None):
        #pdb.set_trace()
        #filename = "/var/log/neutron/server.log"
        #filename = "/tmp/server"
        #filename = sys.argv[1]
        assert(filename)
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

        stack_list=[]
        output_list=[]
        tmp_list=[]
        arg_list=[]
        tree_dict={}

        while True:
            line = logfile.readline()
            if line:
                #print "line:%s\n\n" % line
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
                        tree_dict={'name':splited[5], 'arg':record, 'child':[]}
                        stack_list.append(tree_dict)
                    else:
                        if stack_list[-1]['name'] == splited[5]:
                            stack_list[-1]['arg']['used_time'] = splited[6]
                            stack_list[-1]['arg']['stop_time'] = logtime
                            stack_list[-1]['arg']['color'] = (0,(random.randrange(0,255,1)), (random.randrange(0,255,1)))

                            if stack_list[0]['name'] == splited[5]:
                                tmp_list=copy.deepcopy(stack_list)
                                output_list.append(tmp_list)
                                tmp_list=[]
                            else:
                                stack_list[-2]['child'].append( stack_list[-1])

                            stack_list.pop()
            else:
                break

        """
        case for Error, not have end flag
        """
        if stack_list:
            for i in range(len(stack_list)-1):
                #print "stack:%s\n\n" % la
                stack_list[-1]['arg']['used_time'] = 'ERROR'
                stack_list[-1]['arg']['color'] = (255,0,0)

                stack_list[-2]['child'].append(stack_list[-1])

                stack_list.pop()

            stack_list[-1]['arg']['used_time'] = 'ERROR'
            stack_list[-1]['arg']['color'] = (255,0,0)
            output_list.append(stack_list)

        return output_list

    def make_html(self, logdata=None, output_file_path=None):
        assert(output_file_path)
        assert(logdata)
        fd = open(output_file_path,'w')

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
        tree = tree_opt()
        data = tree.one_dim(logdata)
        body = ''
        for l in data:
            body += tree.parse(l)

        fd.write(body)

        """
        write tail
        """
        html_tail = '</div>\n'\
                '</body>\n'\
                '</html>\n'
        fd.write(html_tail)

        fd.close()



class tree_opt():
    def __init__(self):
        self.bodystr=""

    def one_dim(self, lists):
        l_new=[j for i in lists for j in i]
        return l_new


    def get_child(self, child=None):
        if isinstance(child,dict):
            if child:
                child_lists = child.get("child",None)
                #one_dim(child_lists)
                return child_lists
            else:
                return None

    def parse_child(self, tr=None):
        child = tr['child']
        """
        case:child is None, same parent tree.
        """
        if  child:
            self.parse_parent(tr)
        else:
            html_span = "<span><i class=\"\"></i> %s</span>\n" % (tr['name'])
            self.bodystr += (html_span)
            html_canvas = "<a  title=\"(BeginTime: %s)    (EndTime: %s)    (UsedTime: %s)\">\n \
                    <canvas width=%s height=\"10\" style=\"border:2px solid #%s ;\"></canvas>\n</a>\n" \
                    % (tr['arg']['start_time'], tr['arg']['stop_time'], tr['arg']['used_time'], \
                    Level if tr['arg']['used_time'] == 'ERROR' else Level*float(tr['arg']['used_time']),\
                    self.rgb2hex(tr['arg']['color']))
            self.bodystr += (html_canvas)
            return None



    def parse_parent(self, tr=None):
        assert(tr)
        #pdb.set_trace()
        html_span = "<span><i class=\"class-minus\"></i> %s</span>\n" % (tr['name'])
        self.bodystr += html_span
        html_canvas = "<a title=\"(BeginTime: %s)    (EndTime: %s)    (UsedTime: %s)\">\n \
                <canvas width=%s height=\"10\" style=\"border:2px solid #%s ;\"></canvas>\n</a>\n" \
                % (tr['arg']['start_time'], tr['arg']['stop_time'], tr['arg']['used_time'], \
                Level if tr['arg']['used_time'] == 'ERROR' else Level*float(tr['arg']['used_time']), \
                self.rgb2hex(tr['arg']['color']))

        self.bodystr += html_canvas
        self.bodystr += "<ul>\n"

        child = self.get_child(tr)
        if child:
            for l in child:
                self.bodystr += ("<li>\n")
                self.parse_child(l)
                self.bodystr += ("</li>\n")

        self.bodystr += ("</ul>\n")

    def parse(self, tr=None):
        assert(tr)
        self.bodystr = '' 
        self.bodystr += ("<ul><li>\n")
        self.parse_parent(tr)
        self.bodystr += ("</li></ul>\n")
        return self.bodystr

    def rgb2hex(self, rgbcolor):
        Red, Green, Blue = rgbcolor
        HEX = '%02x%02x%02x' % (Red, Green, Blue)
        return HEX


"""
dirname = sys.argv[1]
opt = Log_to_graph()
logdata = opt.file_format(dirname)
print "logdata:%s\n\n" % logdata
opt.make_html(logdata, "index.html")
"""


