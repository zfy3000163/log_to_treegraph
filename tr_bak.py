#tr={'name':"create",'child':[ [{'name':"props",'child':[] }], [{'name':"quota",'child':[] }], [{'name':"_reserve",'child':[ [{'name':"add_image_metadata",'child':[ [{'name':"add_image", 'child':[] }] ] }] ] }]  ]   }
tr={'name':"create",'child':[ [{'name':"props",'child':[] }], [{'name':"quota",'child':[] }], [{'name':"_reserve",'child':[ [{'name':"add_image_metadata",'child':[ [{'name':"add_image", 'child':[] }] ] }] ] }]  ]   }

print tr

def one_dim(lists):
    l_new=[j for i in lists for j in i]
    return l_new


def get_child(child=None):
    if isinstance(child,dict):
        if child:
            child_lists = child.get("child",None)
            one_dim(child_lists)
            return one_dim(child_lists)
        else:
            return None

def parse_child(tr):
    assert(tr)
    child_lists = get_child(tr)
    #print "lists:%s, %d" % (child_lists, len(child_lists))
    print "    <ul><li><span>%s</span>" % (tr['name'])

    if child_lists:
        for l in child_lists:
            #print "L:%s, %s" % (l, len(l))
            child_lists = get_child(l)
            if child_lists:
                child_lists = get_child(l)
                parse_child(l)

            else:
                print "       <li><span>%s</span>>" %  (l['name'])
    else:
        print "   </li>"


    print "     </li></ul>"


def parse(tr):
    assert(tr)
    child_lists = get_child(tr)
    #print "lists:%s, %d" % (child_lists, len(child_lists))
    print "<ul><li><span>%s</span>" % (tr['name'])
    print "<ul>"

    if child_lists:
        for l in child_lists:
            #print "L:%s, %s" % (l, len(l))
            child_lists = get_child(l)
            if child_lists:
                print "<li>"
                child_lists = get_child(l)
                parse_child(l)

            else:
                print "   </li>"
    else:
        print "   </li>"

    print "</li></ul>" 


def split():
    parse(tr)



split()

