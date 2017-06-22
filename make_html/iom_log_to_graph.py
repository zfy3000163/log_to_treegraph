import re
import sys
import random
import time
import datetime
import copy
import pdb

Level=50


"""
dirname = sys.argv[1]
opt = Log_to_graph()
logdata = opt.log_format(dirname)
print "logdata:%s\n\n" % logdata
opt.make_html(logdata, "index.html")
"""

class Log_to_graph():
    """
    Class Log_to_graph:
        Desc:When create instance and upload images,Draw a function call stack diagram
        method:
        log_format()
            input:
                log for str
            output:
                function's stack log for list
        make_html()
            input:
                function's tree for list
            output:
                HTML markup language for str
    """
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
        #self.bodystr = ''
        self.bodystr += ("<ul><li>\n")
        self.parse_parent(tr)
        self.bodystr += ("</li></ul>\n")
        #return self.bodystr

    def rgb2hex(self, rgbcolor):
        Red, Green, Blue = rgbcolor
        HEX = '%02x%02x%02x' % (Red, Green, Blue)
        return HEX

    def log_format(self, log_list=None):
        #pdb.set_trace()
        assert(log_list)
        if not isinstance(log_list, list):
            return

        stack_list=[]
        output_list=[]
        wait_list=[]
        wait_dict=[]
        tmp_list=[]
        arg_list=[]
        tree_dict={}

        def module_get_color(module_name=None):
            return {"/usr/bin/nova-api":(65,105,225),
                    "/usr/bin/nova-conductor":(95,158,160),
                    "/usr/bin/nova-compute":(138,43,226),
                    "/usr/bin/nova-scheduler":(255,215,0)
                    }.get(module_name, (0,(random.randrange(0,255,1)), (random.randrange(0,255,1))))

        for line in log_list:
            #print "line:%s\n\n" % line
            if isinstance(line, dict):
                funcname_merg = line['host'] + "->"+ line['module_name'].split('/')[-1] + "->" + line['fun']
                if line['start'] == 1:
                    record = {"function_name": funcname_merg,
                            "start_time":time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(line['time'])),
                              "stop_time":'',
                              "color":(255,0,0),
                              "used_time":'-1'}

                    arg_list.append(record)
                    tree_dict={'name':funcname_merg, 'arg':record, 'child':[]}
                    stack_list.append(tree_dict)
                elif line['start'] == 0 and stack_list:
                    """travers the wait_list
                    """
                    def wait_process():
                        if wait_list and stack_list:
                            #print "wait_list:%s\n\n" % (wait_list)
                            for wl in wait_list:
                                if wl['name'] == stack_list[-1]['name']:
                                    stack_list[-1]['arg']['used_time'] = wl['used_time']
                                    stack_list[-1]['arg']['stop_time'] = wl['stop_time']
                                    stack_list[-1]['arg']['color'] = wl['color']

                                    if len(stack_list) == 1 and stack_list[0]['name'] == wl['name']:
                                        tmp_list = copy.deepcopy(stack_list)
                                        output_list.append(tmp_list)
                                        tmp_list=[]
                                    else:
                                        stack_list[-2]['child'].append(stack_list[-1])

                                    stack_list.pop()

                                    wait_list.remove(wl)

                    if stack_list[-1]['name'] == funcname_merg:
                        stack_list[-1]['arg']['used_time'] = line['usedtime']
                        stack_list[-1]['arg']['stop_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(line['time']))
                        stack_list[-1]['arg']['color'] = module_get_color(line['module_name'])

                        if len(stack_list) == 1 and stack_list[0]['name'] == funcname_merg:
                            tmp_list=copy.deepcopy(stack_list)
                            output_list.append(tmp_list)
                            tmp_list=[]
                            stack_list.pop()
                        else:
                            stack_list[-2]['child'].append( stack_list[-1])
                            stack_list.pop()

                        wait_process()

                    elif stack_list[-1]['name'] != funcname_merg:
                        """
                        case for rpc cast
                        """
                        j = len(stack_list)
                        find_flag = 1
                        for i in range(1, j+1):
                            if stack_list[j-i]['name'] == funcname_merg:
                                #print "rpc:%s, %d, len:%d\n\n" % (stack_list[j-i]['name'], j-i, len(stack_list))
                                find_flag = 0
                                stack_list[j-i]['arg']['used_time'] = line['usedtime']
                                stack_list[j-i]['arg']['stop_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(line['time']))
                                stack_list[j-i]['arg']['color'] = module_get_color(line['module_name'])

                                if len(stack_list) == 1 and stack_list[0]['name'] == funcname_merg:
                                    tmp_list=copy.deepcopy(stack_list)
                                    output_list.append(tmp_list)
                                    tmp_list=[]
                                    stack_list.pop()
                                else:
                                    if j-i == 0:
                                        tmp_list.append(stack_list[j-i])
                                        tmp_list = copy.deepcopy(tmp_list)
                                        output_list.append(tmp_list)
                                        tmp_list=[]
                                        stack_list.remove(stack_list[j-i])
                                        pass
                                    else:
                                        stack_list[j-i-1]['child'].append( stack_list[j-i])
                                        stack_list.remove(stack_list[j-i])

                                break

                        """add wait_list,pop stack_list
                        """
                        if find_flag:
                            wait_dict={"name": funcname_merg, "used_time":line['usedtime'], "stop_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(line['time'])), \
                                    "color":module_get_color(line['module_name'])}
                            wait_list.append(wait_dict)

                            wait_process()
                else:
                    print "else else:%s\n\n" % funcname_merg
                    pass

            else:
                break
            #print "stack_list:%s\n\n, output:%s\n\n" % (stack_list, output_list)

        #print "for end\n\n"
        #print "stack_list:%s\n\n, output:%s\n\n, wait_list:%s\n" % (stack_list, output_list, wait_list)
        """
        case for sequence reserve
        """
        if wait_list:
            if len(stack_list) == 1:
                wait_process()
            else:
                for i in range(len(stack_list)-1):
                    wait_process()

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


    def make_html(self, logdata=None):
        assert(logdata)
        out_html= ''

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


        html_head += '<div class="tree" id="tree">\n'
        out_html += html_head

        """
        write body
        """
        data = self.one_dim(logdata)
        for l in data:
            self.parse(l)

        out_html += self.bodystr

        """
        write tail
        """
        html_tail = '</div>\n'\
                '</body>\n'\
                '</html>\n'
        out_html  += html_tail 

        return out_html


