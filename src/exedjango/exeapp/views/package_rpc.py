# ===========================================================================
# eXe
# Copyright 2004-2005, University of Auckland
# Copyright 2006-2008 eXe Project, http://eXeLearning.org/
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
# ===========================================================================

"""
This is the main XUL page.
"""

import os
import sys
from time import sleep
import logging
import traceback
import shutil
#from exe.xului.propertiespage    import PropertiesPage
#from exe.webui.authoringpage     import AuthoringPage
#from exe.export.websiteexport    import WebsiteExport
#from exe.export.textexport       import TextExport
#from exe.export.singlepageexport import SinglePageExport
#from exe.export.scormexport      import ScormExport
##from exe.export.imsexport        import IMSExport
#from exe.export.ipodexport       import IpodExport
#from exe.export.presentationexport  import PresentationExport
#from exe.export.handoutexport    import HandoutExport
from exedjango.utils.path             import Path, toUnicode
#from exe                         import globals as G
from tempfile                    import mkdtemp
#from exe.engine.mimetex          import compile
#from exe.engine.pdfidevice       import PdfIdevice
#from pyPdf                       import PdfFileReader
import re, subprocess, shutil

from jsonrpc import jsonrpc_method
from exeapp.shortcuts import get_package_by_id_or_error
from exeapp.views import package_outline_rpc

log = logging.getLogger(__name__)

@jsonrpc_method('package.testPrintMessage', authenticated=True)
@get_package_by_id_or_error
def testPrintMessage(request, package, message):

    """ 
    Prints a test message, and yup, that's all! 
    """ 
    print "Test Message: ", message, " [eol, eh!]"

@jsonrpc_method('package.handleDblNode', authenticated=True)
@get_package_by_id_or_error
def handleDblNode (request, package):

    """
    Dublicates a tree element
    """

    root = package.currentNode.parent
    if root is None:
        client.alert(_("Can't dublicate root element"))
    else:
        newPackage = package.extractNode()
        newNode = newPackage.root.copyToPackage(package, root)
        newNode.RenamedNodePath(isMerge=True)
        client.sendScript(u'top.location = "/%s"' % \
                      package.name)

@jsonrpc_method('package.setEditorsWidth', authenticated=True)
@get_package_by_id_or_error
def setEditorsWidth(request, package, width):

    """
    Set application's global variable editorsWidth to width. editorsWidth is used to
    set up width of every TinyMCE editor. Updates window after that
    """
    try:
        G.application.editorsWidth = int(width)
        client.sendScript(u'top.location = "/%s"' % \
                          package.name)
    except ValueError, e:
        client.sendScript(u"alert('Please, enter a number');")
        
@jsonrpc_method('package.serveDocument', authenticated=True)
@get_package_by_id_or_error
def serveDocument(request, package):

    """
    Starts serving of $path to localhost:8000
    """

    if G.application.lastExportPath and \
            not self.servController.running:
        path = os.path.join(G.application.lastExportPath, package.name)
        self.servController.startServing(path)
    client.sendScript('document.getElementById("serving-elem").' +\
                      'setAttribute("label", "Serving")')
    #client.sendScript('document.getElementById("serving-elem").' +\
    #                  'oncommand = stopServing')
    client.sendScript('document.getElementById("quick-export").' +\
                      'setAttribute("disabled", "true");')
    client.sendScript('alert("Serving exported Document to port ' + \
                      str(self.servController.PORT) + '");')
    client.sendScript(u'top.location = "/%s"' % \
                      package.name)



@jsonrpc_method('package.stopServing', authenticated=True)
@get_package_by_id_or_error
def stopServing(request, package):

    """
    Stops a running Server
    """

    if self.servController.running:
        self.servController.stopServing()
        client.sendScript('document.getElementById("serving-elem").' +\
                      'setAttribute("label", "Start Serving")')
        client.sendScript('document.getElementById("serving-elem").' +\
                      'oncommand = serveDocument')



@jsonrpc_method('package.openNewTab', authenticated=True)
@get_package_by_id_or_error
def openNewTab(request, package):

    """
    Opens new tab with new exe instance running in it
    """
    
    exeStarter = G.application.config.exePath
    # on windows exePath links to exe dir, on linux to executable
    if os.path.isdir(exeStarter):
        exeStarter = exeStarter / 'exe'
    subprocess.Popen([exeStarter, '--child-process'])
    # file with information about new server's port
    portFile = G.application.config.configDir / 'port'
    while not os.path.exists(portFile):
    # waiting half a second for new process to start
        sleep(0.2)
    f = open(portFile, 'r')
    port = f.read()
    f.close()
    os.remove(portFile)
    client.sendScript(u"openNewTab('%s')" % port)

@jsonrpc_method('package.importStyle', authenticated=True)
@get_package_by_id_or_error
def importStyle(request, package, src):

    '''imports a user style in config directory'''

    print client
    localeStyleDir = G.application.config.configDir / "style"
    styleName = os.path.basename(src)
    shutil.copytree(src, localeStyleDir / styleName) 
    G.application.config.loadStyles()
    client.sendScript(u'top.location = "/%s"' % package.name)

    

@jsonrpc_method('package.outlineClicked', authenticated=True)
@get_package_by_id_or_error
def outlineClicked(request, package):

    """
    Sets documents title to package name + page
    """

    client.sendScript(u'setDocumentTitle("%s")' % package.name) 
    


@jsonrpc_method('package.importPDF', authenticated=True)
@get_package_by_id_or_error
def importPDF(request, package, path, importString):

    """
    Import pdf from path page by page
    """
    pageName = os.path.basename(path)
    self.outlinePane.handleAddChild(client,
        package.currentNode.id)
    self.outlinePane.handleRenNode(client, package.currentNode.id,
        pageName)
    root = package.currentNode
    importString = re.sub('[^\d,-]', '', importString)
    input = PdfFileReader(file(path, 'rb'))
    numpages = input.getNumPages()
    log.debug("Import string: " + importString)
    toimport = PdfIdevice._PdfIdevice__parseImportPages(importString, numpages - 1)
    log.debug("Import: " + str(toimport))
    for x in toimport:
        self.outlinePane.handleAddChild(client, root.id)
        self.outlinePane.handleRenNode(client, package.currentNode.id,
        "Page: %d" % (x + 1))
        # 2 is code of PdfIdevice
        PdfIdeviceCode = '2'
        package.currentNode.addIdevice(
            self.idevicePane.prototypes.get(PdfIdeviceCode).clone())
        package.currentNode.idevices[0].path = path
        # + 1 here to use uploadFile just as if we would have set page
        # number manually
        package.currentNode.idevices[0].pages = str(x + 1)
        package.currentNode.idevices[0].uploadFile()
        package.currentNode = root
    client.sendScript((u'top.location = "/%s"' % package.name).encode('utf8'))


@jsonrpc_method('package.isPackageDirty', authenticated=True)
@get_package_by_id_or_error
def isPackageDirty(request, package, ifClean, ifDirty):

    """
    Called by js to know if the package is dirty or not.
    ifClean is JavaScript to be evaled on the client if the package has
    been changed 
    ifDirty is JavaScript to be evaled on the client if the package has not
    been changed
    """
    if package.isChanged:
        client.sendScript(ifDirty)
    else:
        client.sendScript(ifClean)


@jsonrpc_method('package.getPackageFileName', authenticated=True)
@get_package_by_id_or_error
def getPackageFileName(request, package, onDone, onDoneParam):

    """
    Calls the javascript func named by 'onDone' passing as the
    only parameter the filename of our package. If the package
    has never been saved or loaded, it passes an empty string
    'onDoneParam' will be passed to onDone as a param after the
    filename
    """
    client.call(onDone, unicode(package.filename), onDoneParam)

@jsonrpc_method('package.savePackage', authenticated=True)
@get_package_by_id_or_error
def savePackage(request, package, filename=None, onDone=None):
    package.save_data_package()
    
@jsonrpc_method('package.unload_data_package', authenticated=True)
@get_package_by_id_or_error
def unload_data_package(request, package):
    '''Handles event "package.stopServing'. Unloads given data packages'''
    package.unload_data_package()

@jsonrpc_method('package.loadPackage', authenticated=True)
@get_package_by_id_or_error
def loadPackage(request, package, filename):

    """Load the package named 'filename'"""
    package = self._loadPackage(client, filename, newLoad=True)
    packageStore = self.webServer.application.packageStore
    packageStore.addPackage(package)
    self.root.bindNewPackage(package)
    client.sendScript((u'top.location = "/%s"' % \
                      package.name).encode('utf8'))

@jsonrpc_method('package.loadRecent', authenticated=True)
@get_package_by_id_or_error
def loadRecent(request, package, number):

    """
    Loads a file from our recent files list
    """
    filename = self.config.recentProjects[int(number) - 1]
    self.handleLoadPackage(client, filename)

@jsonrpc_method('package.loadTutorial', authenticated=True)
@get_package_by_id_or_error
def loadTutorial(request, package):

    """
    Loads the tutorial file, from the Help menu
    """
    filename = self.config.webDir.joinpath("docs")\
            .joinpath("eXe-tutorial.elp")
    self.handleLoadPackage(client, filename)

@jsonrpc_method('package.clearRecent', authenticated=True)
@get_package_by_id_or_error
def clearRecent(request, package):

    """
    Clear the recent project list
    """
    G.application.config.recentProjects = []
    G.application.config.configParser.write()
    # rerender the menus
    client.sendScript('top.location = "/%s"' % package.name.encode('utf8'))

@jsonrpc_method('package.setLocale', authenticated=True)
@get_package_by_id_or_error
def setLocale(request, package, locale):

    """
    Set locale using Nevow instead of a POST
    """
    G.application.config.locale = locale
    G.application.config.locales[locale].install(unicode=True)
    G.application.config.configParser.set('user', 'locale', locale)
    client.sendScript((u'top.location = "/%s"' % \
                      package.name).encode('utf8'))

@jsonrpc_method('package.setInternalAnchors', authenticated=True)
@get_package_by_id_or_error
def setInternalAnchors(request, package, internalAnchors):

    """
    Set locale using Nevow instead of a POST
    """
    G.application.config.internalAnchors = internalAnchors
    G.application.config.configParser.set('user', 'internalAnchors', internalAnchors)
    client.sendScript((u'top.location = "/%s"' % \
                      package.name).encode('utf8'))

@jsonrpc_method('package.removeTempDir', authenticated=True)
@get_package_by_id_or_error
def removeTempDir(request, package, tempdir, rm_top_dir):

    """
    Removes a temporary directory and any contents therein
    (from the bottom up), and yup, that's all!
    """
    #
    # swiped from an example on:
    #     http://docs.python.org/lib/os-file-dir.html
    top = tempdir
    ################################################################
    # Delete everything reachable from the directory named in 'top',
    # assuming there are no symbolic links.
    # CAUTION:  This is dangerous!  For example, if top == '/', it
    # could delete all your disk files.
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    ##################################################################
    # and finally, go ahead and remove the top-level tempdir itself:
    if (int(rm_top_dir) != 0):
        os.rmdir(tempdir)

def get_printdir_relative2web(request, exported_dir):
    """
    related to the following ClearParentTempPrintDirs(), return a
    local URL corresponding to the exported_dir
    """
    rel_name = exported_dir[len(G.application.tempWebDir):]
    if sys.platform[:3] == "win":
        rel_name = rel_name.replace('\\', '/')
    if rel_name.startswith('/'):
        rel_name = rel_name[1:]
    http_relative_pathname = "http://127.0.0.1:" + str(self.config.port) \
                                 + '/' + rel_name
    log.debug('printdir http_relative_pathname=' + http_relative_pathname)
    return http_relative_pathname

def ClearParentTempPrintDirs(request, client, log_dir_warnings):
    """
    Determine the parent temporary printing directory, and clear them 
    if safe to do so (i.e., if not the config dir itself, for example)
    Makes (if necessary), and clears out (if applicable) the parent 
    temporary directory.
    The calling handleClearAndMakeTempPrintDir() shall then make a 
    specific print-job subdirectory.
    """
    #
    # Create the parent temp print dir as hardcoded under the webdir, as:
    #           http://temp_print_dirs
    # (eventually may want to allow this information to be configured by
    #  the user, stored in globals, etc.)
    web_dirname = G.application.tempWebDir
    under_dirname = os.path.join(web_dirname,"temp_print_dirs")
    clear_tempdir = 0
    dir_warnings = ""

    # but first need to ensure that under_dirname itself is available; 
    # if not, create it:
    if cmp(under_dirname,"") != 0:
        if os.path.exists(under_dirname):
            if (os.path.isdir(under_dirname)):
                # Yes, this directory already exists.  
                # pre-clean it, keeping the clutter down:
                clear_tempdir = 1
            else:
                dir_warnings = "WARNING: The desired Temporary Print " \
                        + "Directory, \"" + under_dirname \
                        + "\", already exists, but as a file!\n"
                if log_dir_warnings:
                    log.warn("ClearParentTempPrintDirs(): The desired " \
                            + "Temporary Print Directory, \"%s\", " \
                            + "already exists, but as a file!", \
                            under_dirname)
                under_dirname = web_dirname
                # but, we can't just put the tempdirs directly underneath
                # the webDir, since no server object exists for it.
                # So, as a quick and dirty solution, go ahead and put 
                # them in the images folder:
                under_dirname = os.path.join(under_dirname,"images")

                dir_warnings += "    RECOMMENDATION: please " \
                        + "remove/rename this file to allow eXe easier "\
                        + "management of its temporary print files.\n"
                dir_warnings += "     eXe will create the temporary " \
                       + "printing directory directly under \"" \
                       + under_dirname + "\" instead, but this might "\
                       +"leave some files around after eXe terminates..."
                if log_dir_warnings:
                    log.warn("    RECOMMENDATION: please remove/rename "\
                        + "this file to allow eXe easier management of "\
                        + "its temporary print files.")
                    log.warn("     eXe will create the temporary " \
                        + "printing directory directly under \"%s\" " \
                        + "instead, but this might leave some files " \
                        + "around after eXe terminates...", \
                        under_dirname)
                # and note that we do NOT want to clear_tempdir 
                # on the config dir itself!!!!!
        else:
            os.makedirs(under_dirname)
            # and while we could clear_tempdir on it, there's no need to.
    if clear_tempdir : 
        # before making this particular print job's temporary print 
        # directory underneath the now-existing temp_print_dirs, 
        # go ahead and clear out temp_print_dirs such that we have 
        # AT MOST one old temporary set of print job files still existing
        # once eXe terminates:
        rm_topdir = "0"  
        # note: rm_topdir is passed in as a STRING since 
        # handleRemoveTempDir expects as such from nevow's 
        # clientToServerEvent() call:
        self.handleRemoveTempDir(client, under_dirname, rm_topdir)

    return under_dirname, dir_warnings

@jsonrpc_method('package.makeTempPrintDir', authenticated=True)
@get_package_by_id_or_error
def makeTempPrintDir(request, package, suffix, prefix, \
                                    callback):

    """
    Makes a temporary printing directory, and yup, that's pretty much it!
    """

    # First get the name of the parent temp directory, after making it 
    # (if necessary) and clearing (if applicable):
    log_dir_warnings = 1  
    (under_dirname, dir_warnings) = self.ClearParentTempPrintDirs( \
                                         client, log_dir_warnings)

    # Next, go ahead and create this particular print job's temporary 
    # directory under the parent temp directory:
    temp_dir = mkdtemp(suffix, prefix, under_dirname) 

    # Finally, pass the created temp_dir back to the expecting callback:
    client.call(callback, temp_dir, dir_warnings)

@jsonrpc_method('package.previewTinyMCEimage', authenticated=True)
@get_package_by_id_or_error
def previewTinyMCEimage(request, package, tinyMCEwin, tinyMCEwin_name, \
                         tinyMCEfield, local_filename, preview_filename):

    """
    Once an image is selected in the file browser that is spawned by the 
    TinyMCE image dialog, copy this file (which is local to the user's 
    machine) into the server space, under a preview directory 
    (after checking if this exists, and creating it if necessary).
    Note that this IS a "cheat", in violation of the client-server 
    separation, but can be done since we know that the eXe server is 
    actually sitting on the client host.
    """
    server_filename = ""
    callback_errors = ""
    errors = 0

    log.debug('handleTinyMCEimageChoice: image local = ' + local_filename 
            + ', base=' + os.path.basename(local_filename))

    webDir     = Path(G.application.tempWebDir)
    previewDir  = webDir.joinpath('previews')

    if not previewDir.exists():
        log.debug("image previews directory does not yet exist; " \
                + "creating as %s " % previewDir)
        previewDir.makedirs()
    elif not previewDir.isdir():
        client.alert( \
            _(u'Preview directory %s is a file, cannot replace it') \
            % previewDir)
        log.error("Couldn't preview tinyMCE-chosen image: "+
                  "Preview dir %s is a file, cannot replace it" \
                  % previewDir)
        callback_errors =  "Preview dir is a file, cannot replace"
        errors += 1

    if errors == 0:
        log.debug('handleTinyMCEimageChoice: originally, local_filename='
                + local_filename)
        local_filename = unicode(local_filename, 'utf-8')
        log.debug('handleTinyMCEimageChoice: in unicode, local_filename='
                + local_filename)

        localImagePath = Path(local_filename)
        log.debug('handleTinyMCEimageChoice: after Path, localImagePath= '
                + localImagePath);
        if not localImagePath.exists() or not localImagePath.isfile():
            client.alert( \
                 _(u'Local file %s is not found, cannot preview it') \
                 % localImagePath)
            log.error("Couldn't find tinyMCE-chosen image: %s" \
                    % localImagePath)
            callback_errors = "Image file %s not found, cannot preview" \
                    % localImagePath
            errors += 1

    try:
        # joinpath needs its join arguments to already be in Unicode:
        #preview_filename = toUnicode(preview_filename);
        # but that's okay, cuz preview_filename is now URI safe, right?
        log.debug('URIencoded preview filename=' + preview_filename);

        server_filename = previewDir.joinpath(preview_filename);
        log.debug("handleTinyMCEimageChoice copying image from \'"\
                + local_filename + "\' to \'" \
                + server_filename.abspath() + "\'.");
        shutil.copyfile(local_filename, \
                server_filename.abspath());

        # new optional description file to provide the 
        # actual base filename, such that once it is later processed
        # copied into the resources directory, it can be done with
        # only the basename.   Otherwise the resource filenames
        # are too long for some users, preventing them from making
        # backup CDs of the content, for example.
        # 
        # Remember that the full path of the
        # file is only used here as an easy way to keep the names
        # unique WITHOUT requiring a roundtrip call from the Javascript
        # to this server, and back again, a process which does not
        # seem to work with tinyMCE in the mix.  BUT, once tinyMCE's
        # part is done, and this image processed, it can be returned
        # to just its basename, since the resource parts have their
        # own unique-ification mechanisms already in place.

        descrip_file_path = Path(server_filename+".exe_info")
        log.debug("handleTinyMCEimageChoice creating preview " \
                + "description file \'" \
                + descrip_file_path.abspath() + "\'.");
        descrip_file = open(descrip_file_path, 'wb')

        # safety measures against TinyMCE, otherwise it will 
        # later take ampersands and entity-escape them into '&amp;',
        # and filenames with hash signs will not be found, etc.:
        unspaced_filename  = local_filename.replace(' ','_')
        unhashed_filename  = unspaced_filename.replace('#', '_num_')
        unamped_local_filename  = unhashed_filename.replace('&', '_and_')
        log.debug("and setting new file basename as: " 
                + unamped_local_filename);
        my_basename = os.path.basename(unamped_local_filename)
        descrip_file.write((u"basename="+my_basename).encode('utf-8'))

        descrip_file.flush()
        descrip_file.close()

    except Exception, e:
        client.alert(_('SAVE FAILED!\n%s' % str(e)))
        log.error("handleTinyMCEimageChoice unable to copy local image "\
                +"file to server prevew, error = " + str(e))
        raise

@jsonrpc_method('package.generateTinyMCEmath', authenticated=True)
@get_package_by_id_or_error
def generateTinyMCEmath(request, package, tinyMCEwin, tinyMCEwin_name, \
                         tinyMCEfield, latex_source, math_fontsize, \
                         preview_image_filename, preview_math_srcfile):

    """
    Based off of handleTinyMCEimageChoice(), 
    handleTinyMCEmath() is similar in that it places a .gif math image 
    (and a corresponding .tex LaTeX source file) into the previews dir.
    Rather than copying the image from a user-selected directory, though,
    this routine actually generates the math image using mimetex.
    """
    server_filename = ""
    callback_errors = ""
    errors = 0

    webDir     = Path(G.application.tempWebDir)
    previewDir  = webDir.joinpath('previews')

    if not previewDir.exists():
        log.debug("image previews directory does not yet exist; " \
                + "creating as %s " % previewDir)
        previewDir.makedirs()
    elif not previewDir.isdir():
        client.alert( \
            _(u'Preview directory %s is a file, cannot replace it') \
            % previewDir)
        log.error("Couldn't preview tinyMCE-chosen image: "+
                  "Preview dir %s is a file, cannot replace it" \
                  % previewDir)
        callback_errors =  "Preview dir is a file, cannot replace"
        errors += 1

    #if errors == 0:
    #    localImagePath = Path(local_filename)
    #    if not localImagePath.exists() or not localImagePath.isfile():
    #        client.alert( \
    #             _(u'Image file %s is not found, cannot preview it') \
    #             % localImagePath)
    #        log.error("Couldn't find tinyMCE-chosen image: %s" \
    #                % localImagePath)
    #        callback_errors = "Image file %s not found, cannot preview" \
    #                % localImagePath
    #        errors += 1

    # the mimetex usage code was swiped from the Math iDevice:
    if latex_source <> "":

        # first write the latex_source out into the preview_math_srcfile,
        # such that it can then be passed into the compile command:
        math_filename = previewDir.joinpath(preview_math_srcfile)
        math_filename_str = math_filename.abspath().encode('utf-8')
        log.info("handleTinyMCEmath: using LaTeX source: " + latex_source)
        log.debug("writing LaTeX source into \'" \
                + math_filename_str + "\'.")
        math_file = open(math_filename, 'wb')
        # do we need to append a \n here?:
        math_file.write(latex_source)
        math_file.flush()
        math_file.close()


        try: 
            use_latex_sourcefile = math_filename_str
            tempFileName = compile(use_latex_sourcefile, math_fontsize, \
                    latex_is_file=True)
        except Exception, e:
            client.alert(_('MimeTeX compile failed!\n%s' % str(e)))
            log.error("handleTinyMCEmath unable to compile LaTeX using "\
                +"mimetex, error = " + str(e))
            raise

        # copy the file into previews
        server_filename = previewDir.joinpath(preview_image_filename);
        log.debug("handleTinyMCEmath copying math image from \'"\
                + tempFileName + "\' to \'" \
                + server_filename.abspath().encode('utf-8') + "\'.");
        shutil.copyfile(tempFileName, \
                server_filename.abspath().encode('utf-8'));

        # Delete the temp file made by compile 
        Path(tempFileName).remove()
    return

@jsonrpc_method('package.quickExport', authenticated=True)
@get_package_by_id_or_error
def quickExport(request, package):

    """
    Called by js.
    Checks if already exported, does last export
    """

    if G.application.lastExportType:
        self.handleExport(client, G.application.lastExportType, 
                    G.application.lastExportPath, quick=True) 

@jsonrpc_method('package.exportPackage', authenticated=True)
@get_package_by_id_or_error
def exportPackage(request, package, exportType, filename, print_callback='', quick=False):

    """
    Called by js. 
    Exports the current package to one of the above formats
    'exportType' can be one of 'singlePage' 'webSite' 'zipFile' 'ipod'
                 'textFile' 'scorm' or 'presentation'
    'filename' is a file for scorm pages, and a directory for websites
    """ 
    G.application.lastExportType = exportType
    G.application.lastExportPath = filename
    client.sendScript('document.getElementById("quick-export")' + \
                      '.setAttribute("disabled", "false");')
    client.sendScript('document.getElementById("serving-elem")' + \
                      '.setAttribute("disabled", "false");')
    client.sendScript('document.getElementById("serving-elem")' + \
                      '.setAttribute("label", "Start Serving");')
    client.sendScript('document.getElementById("serving-elem")' + \
                    '.setAttribute("oncommand", "serveDocument\(\)");')
    client.sendScript('document.getElementById("quick-export").' +\
                      'setAttribute("disabled", "false");')
    log.info("Filename to export" + filename)
    webDir     = Path(self.config.webDir)
    if package.style.find("locale/") != -1:
        # local style loaded
        stylesDir  = self.config.configDir / "style"
        # delete "locale/" from style name
        stylesDir /= package.style[package.style.find\
                                        ("locale/") + len("locale/"):]
    else:
        # global style
        stylesDir = webDir / "style"
        stylesDir /= package.style

    exportDir  = Path(filename).dirname()
    if exportDir and not exportDir.exists():
        client.alert(_(u'Cannot access directory named ') +
                     unicode(exportDir) +
                     _(u'. Please use ASCII names.'))
        return

    """ 
    adding the print feature in using the same export functionality:
    """
    if exportType == 'singlePage' or exportType == 'printSinglePage':
        printit = 0
        if exportType == 'printSinglePage':
            printit = 1
        exported_dir = self.exportSinglePage(client, filename, webDir, \
                                             stylesDir, printit)
        # the above will return None if the desired exported directory
        # already exists (printing always goes to a new temp dir, though):
        if printit == 1 and not exported_dir is None:
            web_printdir = self.get_printdir_relative2web(exported_dir)
            # now that this has ben exported, go ahead and trigger 
            # the requested printing callback:
            client.call(print_callback, filename, exported_dir, \
                        web_printdir)

    elif exportType == 'webSite':
        self.exportWebSite(client, filename, stylesDir, quick=quick)

    elif exportType == 'presentation':
        self.exportPresentation(client, filename, stylesDir)
    elif exportType == 'printHandout':
        exported_dir = self.printHandout(client, filename, stylesDir)
        print exported_dir
        web_printdir = self.get_printdir_relative2web(exported_dir)
        client.call(print_callback, filename, exported_dir, 
            web_printdir)
        
    elif exportType == 'zipFile':
        filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
        self.exportWebZip(client, filename, stylesDir)
    elif exportType == 'textFile':
        self.exportText(client, filename)
    elif exportType == 'ipod':
        self.exportIpod(client, filename)
    elif exportType == "scorm":
        filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
        self.exportScorm(client, filename, stylesDir, "scorm1.2")
    elif exportType == "scorm2004":
        filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
        self.exportScorm(client, filename, stylesDir, "scorm2004")
    elif exportType == "commoncartridge":
        filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
        self.exportScorm(client, filename, stylesDir, "commoncartridge")
    else:
        filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
        self.exportIMS(client, filename, stylesDir)

@jsonrpc_method('package.quit', authenticated=True)
@get_package_by_id_or_error
def quit(request, package):

    """
    Stops the server
    """
    # first, go ahead and clear out any temp job files still in 
    # the temporary print directory:
    log_dir_warnings = 0  
    # don't warn of any issues with the directories at quit, 
    # since already warned at initial directory creation
    (parent_temp_print_dir, dir_warnings) = \
            self.ClearParentTempPrintDirs(client, log_dir_warnings)

#       self.servController.stopServing()
    reactor.stop()

@jsonrpc_method('package.browseURL', authenticated=True)
@get_package_by_id_or_error
def browseURL(request, package, url):

    """visit the specified URL using the system browser
    
    if the URL contains %s, substitute the local webDir
    if the URL contains %t, show a temp file containing NEWS and README """
    if '%t' in url.find:
        release_notes = os.path.join(G.application.tempWebDir,
                'Release_Notes.html')
        f = open(release_notes, 'wt')
        f.write('''<html><head><title>eXe Release Notes</title></head>
            <body><h1>News</h1><pre>\n''')
        try:
            news = open(os.path.join(self.config.webDir, 'NEWS'),
                    'rt').read()
            readme = open(os.path.join(self.config.webDir, 'README'),
                    'rt').read()
            f.write(news)
            f.write('</pre><hr><h1>Read Me</h1><pre>\n')
            f.write(readme)
        except IOError:
            # fail silently if we can't read either of the files
            pass
        f.write('</pre></body></html>')
        f.close()
        url = url.replace('%t', release_notes)
    else:
        url = url.replace('%s', self.config.webDir)
    log.debug(u'browseURL: ' + url)
    if hasattr(os, 'startfile'):
        os.startfile(url)
    elif sys.platform[:6] == "darwin":
        import webbrowser
        webbrowser.open(url, new=True)
    else:
        os.system("firefox " + url + "&")

@jsonrpc_method('package.insertPackage', authenticated=True)
@get_package_by_id_or_error
def insertPackage(request, package, filename):

    """
    Load the package and insert in current node
    """
    loadedPackage = self._loadPackage(client, filename, newLoad=False,
                                      destinationPackage=package)
    newNode = loadedPackage.root.copyToPackage(package, 
                                               package.currentNode)
    # trigger a rename of all of the internal nodes and links,
    # and to add any such anchors into the dest package via isMerge:
    try:
        newNode.RenamedNodePath(isMerge=True)
    except Exception, e:
        client.alert(str(e))

    client.sendScript((u'top.location = "/%s"' % \
                      package.name).encode('utf8'))


@jsonrpc_method('package.extractPackage', authenticated=True)
@get_package_by_id_or_error
def extractPackage(request, package, filename, existOk):

    """
    Create a new package consisting of the current node and export
    'existOk' means the user has been informed of existance and ok'd it
    """
    filename  = Path(filename)
    saveDir = filename.dirname()
    if saveDir and not saveDir.exists():
        client.alert(_(u'Cannot access directory named ') + unicode(saveDir) + _(u'. Please use ASCII names.'))
        return

    # Add the extension if its not already there
    if not filename.lower().endswith('.elp'):
        filename += '.elp'

    if Path(filename).exists() and existOk != 'true':
        msg = _(u'"%s" already exists.\nPlease try again with a different filename') % filename
        client.alert(_(u'EXTRACT FAILED!\n%s' % msg))
        return

    try:
        # Create a new package for the extracted nodes
        newPackage = package.extractNode()

        # trigger a rename of all of the internal nodes and links,
        # and to remove any old anchors from the dest package,
        # and remove any zombie links via isExtract:
        newNode = newPackage.root
        if newNode: 
            newNode.RenamedNodePath(isExtract=True)

        # Save the new package
        newPackage.save(filename)
    except Exception, e:
        client.alert(_('EXTRACT FAILED!\n%s' % str(e)))
        raise
    client.alert(_(u'Package extracted to: %s' % filename))

# Public Methods

def exportSinglePage(request, client, filename, webDir, stylesDir, \
                     printFlag):
    """
    Export 'client' to a single web page,
    'webDir' is just read from config.webDir
    'stylesDir' is where to copy the style sheet information from
    'printFlag' indicates whether or not this is for print 
                (and whatever else that might mean)
    """
    try:
        imagesDir    = webDir.joinpath('images')
        scriptsDir   = webDir.joinpath('scripts')
        templatesDir = webDir.joinpath('templates')
        # filename is a directory where we will export the website to
        # We assume that the user knows what they are doing
        # and don't check if the directory is already full or not
        # and we just overwrite what's already there
        filename = Path(filename)
        # Append the package name to the folder path if necessary
        if filename.basename() != package.name:
            filename /= package.name
        if not filename.exists():
            filename.makedirs()
        elif not filename.isdir():
            client.alert(_(u'Filename %s is a file, cannot replace it') % 
                         filename)
            log.error("Couldn't export web page: "+
                      "Filename %s is a file, cannot replace it" % filename)
            return
        else:
            client.alert(_(u'Folder name %s already exists. '
                            'Please choose another one or delete existing one then try again.') % filename)           
            return 
        # Now do the export
        singlePageExport = SinglePageExport(stylesDir, filename, \
                                     imagesDir, scriptsDir, templatesDir)
        singlePageExport.export(package, printFlag)
    except Exception, e:
        client.alert(_('SAVE FAILED!\n%s' % str(e)))
        raise
    # Show the newly exported web site in a new window
    if not printFlag:
       self._startFile(client, filename)
    # and return a string of the actual directory name, 
    # in case the package name was added, etc.:
    return filename.abspath().encode('utf-8')
    # WARNING: the above only returns the RELATIVE pathname

    
def exportPresentation(request, client, filename, stylesDir):
    """
    export client to a DOM presentation
    """

    try:
        # filename is a directory where we will export the website to
        # We assume that the user knows what they are doing
        # and don't check if the directory is already full or not
        # and we just overwrite what's already there
        filename = Path(filename)
        # Append the package name to the folder path if necessary
        if filename.basename() != package.name:
            filename /= package.name
        if not filename.exists():
            filename.makedirs()
        elif not filename.isdir():
            client.alert(_(u'Filename %s is a file, cannot replace it') %
                         filename)
            log.error("Couldn't export web page: "+
                      "Filename %s is a file, cannot replace it" % filename)
            return
        else:
            client.alert(_(u'Folder name %s already exists. '
                            'Please choose another one or delete existing one then try again.') % filename)
            return
        # Now do the export
        presentationExport = PresentationExport(self.config, stylesDir,
            filename)
        presentationExport.export(package)
    except Exception, e:
        client.alert(_('EXPORT FAILED!\n%s') % str(e))
        raise

    # show new presentation in a new window
    self._startFile(client, filename)


def printHandout(request, client, exportDir, stylesDir):
    """
    export client to a DOM presentation
    """

    print exportDir
    handoutExport = HandoutExport(self.config, stylesDir,
        exportDir)
    handoutExport.export(package)
    return exportDir.encode('utf-8')


def exportWebSite(request, client, filename, stylesDir, quick=False):
    """
    Export 'client' to a web site,
    'webDir' is just read from config.webDir
    'stylesDir' is where to copy the style sheet information from
    """
    # filename is a directory where we will export the website to
    filename = Path(filename)
    # Append the package name to the folder path if necessary
    if filename.basename() != package.name:
        filename /= package.name

    if filename.exists() and not quick:
        client.sendScript('askOverwrite("%s", "%s");' \
                          % (str(filename).replace("\\", "\\\\"),
                             stylesDir.replace("\\", "\\\\")))
    else:
        # Now do the export
        self.exportWebSite2(client, filename, stylesDir)

def exportWebSite2(request, client, filename, stylesDir):
    '''Overwrite allowed, proceed'''
    try:
        filename = Path(filename)
        if filename.exists():
            if filename.isdir():
                shutil.rmtree(filename)
            else:
                os.remove(filename)
        filename.makedirs()
        websiteExport = WebsiteExport(self.config, stylesDir, filename)
        websiteExport.export(package)
        self._startFile(client, filename)
    except Exception, e:
        log.error("EXPORT FAILED! %s" % filename)
        raise

def exportWebZip(request, client, filename, stylesDir):
    try:
        log.debug(u"exportWebsite, filename=%s" % filename)
        filename = Path(filename)
        # Do the export
        filename = self.b4save(client, filename, '.zip', _(u'EXPORT FAILED!'))
        websiteExport = WebsiteExport(self.config, stylesDir, filename)
        websiteExport.exportZip(package)
    except Exception, e:
        client.alert(_('EXPORT FAILED!\n%s' % str(e)))
        raise
    client.alert(_(u'Exported to %s') % filename)
    
def exportText(self, client, filename):
    try: 
        filename = Path(filename)
        log.debug(u"exportWebsite, filename=%s" % filename)
        # Append an extension if required
        if not filename.lower().endswith('.txt'):
            filename += '.txt'
            if Path(filename).exists():
                msg = _(u'"%s" already exists.\nPlease try again with a different filename') % filename
                client.alert(_(u'EXPORT FAILED!\n%s' % msg))
                return
        # Do the export
        textExport = TextExport(filename)
        textExport.export(package)
    except Exception, e:
        client.alert(_('EXPORT FAILED!\n%s' % str(e)))
        raise
    client.alert(_(u'Exported to %s') % filename)
    
def exportIpod(request, client, filename):
    """
    Export 'client' to an iPod Notes folder tree
    'webDir' is just read from config.webDir
    """
    try:
        # filename is a directory where we will export the notes to
        # We assume that the user knows what they are doing
        # and don't check if the directory is already full or not
        # and we just overwrite what's already there
        filename = Path(filename)
        # Append the package name to the folder path if necessary
        if filename.basename() != package.name:
            filename /= package.name
        if not filename.exists():
            filename.makedirs()
        elif not filename.isdir():
            client.alert(_(u'Filename %s is a file, cannot replace it') % 
                         filename)
            log.error("Couldn't export web page: "+
                      "Filename %s is a file, cannot replace it" % filename)
            return
        else:
            client.alert(_(u'Folder name %s already exists. '
                            'Please choose another one or delete existing one then try again.') % filename)           
            return 
        # Now do the export
        ipodExport = IpodExport(self.config, filename)
        ipodExport.export(package)
    except Exception, e:
        client.alert(_('EXPORT FAILED!\n%s') % str(e))
        raise
    client.alert(_(u'Exported to %s') % filename)

def exportScorm(request, client, filename, stylesDir, scormType):
    """
    Exports this package to a scorm package file
    """
    try:
        filename = Path(filename)
        log.debug(u"exportScorm, filename=%s" % filename)
        # Append an extension if required
        if not filename.lower().endswith('.zip'):
            filename += '.zip'
            if Path(filename).exists():
                msg = _(u'"%s" already exists.\nPlease try again with a different filename') % filename
                client.alert(_(u'EXPORT FAILED!\n%s' % msg))
                return
        # Do the export
        scormExport = ScormExport(self.config, stylesDir, filename, scormType)
        scormExport.export(package)
    except Exception, e:
        client.alert(_('EXPORT FAILED!\n%s' % str(e)))
        raise
    client.alert(_(u'Exported to %s') % filename)

def exportIMS(request, client, filename, stylesDir):
    """
    Exports this package to a ims package file
    """
    try:
        log.debug(u"exportIMS")
        # Append an extension if required
        if not filename.lower().endswith('.zip'):
            filename += '.zip'
            if Path(filename).exists():
                msg = _(u'"%s" already exists.\nPlease try again with a different filename') % filename
                client.alert(_(u'EXPORT FAILED!\n%s' % msg))
                return
        # Do the export
        imsExport = IMSExport(self.config, stylesDir, filename)
        imsExport.export(package)
    except Exception, e:
        client.alert(_('EXPORT FAILED!\n%s' % str(e)))
        raise
    client.alert(_(u'Exported to %s' % filename))

# Utility methods
def _startFile(request, client, filename):
    """
    Launches an exported web site or page
    """
    if not filename.endswith("/index.html"):
        filename /= 'index.html'
    filename = filename.replace("\\", "\\\\")
    log.info(filename)
    client.sendScript("openPreview('%s');" % filename)

def _loadPackage(request, client, filename, newLoad=True,
                 destinationPackage=None):
    """Load the package named 'filename'"""
    try:
        encoding = sys.getfilesystemencoding()
        if encoding is None:
            encoding = 'utf-8'
        filename2 = toUnicode(filename, encoding)
        log.debug("filename and path" + filename2)
        # see if the file exists AND is readable by the user
        try:
            open(filename2, 'rb').close()
        except IOError:
            filename2 = toUnicode(filename, 'utf-8')
            try:
                open(filename2, 'rb').close()
            except IOError:
                client.alert(_(u'File %s does not exist or is not readable.') % filename2)
                return None
        package = Package.load(filename2, newLoad, destinationPackage)
        if package is None:
            raise Exception(_("Couldn't load file, please email file to bugs@exelearning.org"))
    except Exception, exc:
        if log.getEffectiveLevel() == logging.DEBUG:
            client.alert(_(u'Sorry, wrong file format:\n%s') % unicode(exc))
        else:
            client.alert(_(u'Sorry, wrong file format'))
        log.error(u'Error loading package "%s": %s' % (filename2, unicode(exc)))
        log.error(u'Traceback:\n%s' % traceback.format_exc())
        raise
    return package

