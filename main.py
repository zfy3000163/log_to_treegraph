import sys
import os 
from make_html import iom_log_to_graph
import datetime
import memcache


def main():
    log_list=[{'last_func': '_checks_for_create_and_rebuild', 'start': 1, 'host': 'node-3.domain.tld', 'usedtime': datetime.timedelta(0, 0, 89739), 'time': datetime.datetime(2017, 6, 9, 9, 59, 29, 306542), 'fun': 'api.py:_check_metadata_properties_quota', 'module_name': '/usr/binva-api'}, {'last_func': '_checks_for_create_and_rebuild', 'start': 1, 'host': 'node-3.domain.tld', 'time': datetime.datetime(2017, 6, 9, 9, 59, 29, 375156), 'fun': 'api.py:_check_injected_file_quota', 'module_name': '/usr/binva-api'}, {'last_func': '_checks_for_create_and_rebuild', 'start': 0, 'host': 'node-3.domain.tld', 'usedtime': datetime.timedelta(0, 0, 95657), 'time': datetime.datetime(2017, 6, 9, 9, 59, 29, 470813), 'fun': 'api.py:_check_injected_file_quota', 'module_name': '/usr/binva-api'}, {'last_func': '_checks_for_create_and_rebuild', 'start': 1, 'host': 'node-3.domain.tld', 'time': datetime.datetime(2017, 6, 9, 9, 59, 29, 528317), 'fun': 'api.py:_check_requested_image', 'module_name': '/usr/binva-api'}, {'last_func': '_checks_for_create_and_rebuild', 'start': 0, 'host': 'node-3.domain.tld', 'usedtime': datetime.timedelta(0, 0, 49857), 'time': datetime.datetime(2017, 6, 9, 9, 59, 29, 578174), 'fun': 'api.py:_check_requested_image', 'module_name': '/usr/binva-api'}]

    mc = memcache.Client(["192.168.10.3:11211","192.168.10.4:11211", "192.168.10.5:11211"])
    log = mc.get("123.123456")
    if not log:
        print "log is null"
        sys.exit()
    else:
        #print log
        pass
    opt = iom_log_to_graph.Log_to_graph()
    logdata = opt.log_format(log)
    print logdata
    _path = "/tmp/"
    _name = "iom"
    file_name = _path + _name + ".html"
    html_str = opt.make_html(logdata)
    fd = open('/tmp/iom.html','w')
    fd.write(html_str)
    fd.close()


main()
