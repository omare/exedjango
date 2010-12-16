'''
Usage: meta_convert_mainpage FILENAME

Meta programming script to convert exe/xului/mainpage.py to be used in
exedjango. New handlers will be given event namens, decorators for getting
package and adding jsonRPC will be added, self.package will be changed to 
package.
Takes a filename as argument and saves the result in the same directory with
_convert.py ending.'''

import re, sys



def convert(data):
    '''Does actual converting'''
    # Get handlers and event names to a dictinary
    re_events = re.compile(r'setUpHandler\(self.(.*?),\s* \'(.*?)\'\)')
    events = dict(re_events.findall(data))
    
    def generate_signature(match):
        '''Generates a new signature from a match object'''
        sig = \
'''@jsonrpc_method('package.%(event_name)s', authenticated=True)
    @get_package_by_id_or_error
    def %(event_name)s(request, package%(additional_args)s):
''' % {'event_name' : events.get(match.group(1), match.group(1)),
       'additional_args' : match.group(2)}
        return sig

    # get list of handlers
    re_handlers = re.compile(r'def (handle.*?)\(self, client(.*?)\):',
                              re.DOTALL)
    converted = re_handlers.sub(generate_signature, data)
    # replace references to package
    converted = converted.replace('self.package', 'package')
    return converted
    

if __name__ == '__main__':
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        with open(filename, 'r') as file:
            data = file.read()
        converted = convert(data)
            
        filename = re.sub(r'^(.*)\.py', '\\1_converted.js', filename)
        with open(filename, 'w') as file:
            file.write(converted)
    else:
        print __doc__
            
        