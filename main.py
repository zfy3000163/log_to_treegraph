import sys
import os 
from make_html import iom_log_to_graph


def main():
    opt = iom_log_to_graph.Log_to_graph()
    logdata = opt.file_format(sys.argv[1])
    _path = os.path.dirname(sys.argv[1])
    _name = os.path.basename(sys.argv[1])
    file_name = _path + _name + ".html"
    opt.make_html(logdata, file_name)


main()
