'''
Usage: meta_convert_mainpage_js.py FILENAME

Converts legacy mainpage.js to work with jsonRPC. Replaces nevow_clientToS...
calls with jQuery jsonRPC-plugin call. Convertes arguments

Saves results in FILENAME_converted.js
'''

import sys, re

def convert(data):
    '''Does actual convesion'''
    
    re_nevow = re.compile(r"""
    nevow_clientToServerEvent\(\'(.*?)\' # command name
         ,\s*this ,?\s*                  # this and leading , isn't important
         (.*?)\);?                        # comma-separated list of args
         """, re.VERBOSE)

    def generate_rpc_call(match):
        '''Generates a rpc call for jquery rpc plugin from a match object'''
        
        args = ['get_package_id()']
        for arg in match.group(2).split(','):
            args.append(arg.strip())
        call = '$.jsonRPC.request(\'%s\', [%s]);' % (match.group(1), ",".join(args))
        return call
    
    converted = re_nevow.sub(generate_rpc_call, data)
    return converted

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        with open(filename, 'r') as file:
            data = file.read()
        converted = convert(data)
        
        filename = re.sub(r'^(.*)\.js', '\\1_converted.js', filename)
        print "Saving result as %s." % filename
        with open(filename, 'w') as file:
            file.write(converted)
    else:
        print __doc__