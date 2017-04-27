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
    child = tr['child']
    if not child:
        print "<span>%s</span>" % (tr['name'])
        return None
    else:
        parse_parent(tr)



def parse_parent(tr):
    assert(tr)
    print "<span>%s</span>" % (tr['name'])
    print "<ul>"

    child = get_child(tr)
    if child:
        for l in child:
            print "<li>"
            parse_child(l)
            print "</li>"

    print "</ul>"

def parse(tr):
    assert(tr)
    print "<ul><li>"
    parse_parent(tr)
    print "</li></ul>"



def split():
    parse(tr)



split()

