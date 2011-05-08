// ===========================================================================
// eXe
// Copyright 2004-2005, University of Auckland
// Copyright 2004-2007 eXe Project, New Zealand Tertiary Education Commission
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
// ===========================================================================

// This file contains all the js related to the main xul page

// Set it to false upon deployement
DEBUG = true;

// Strings to be translated
DELETE_  = 'Delete "';
NODE_AND_ALL_ITS_CHILDREN_ARE_YOU_SURE_ = '" node and all its children. Are you sure?';
RENAME_ = 'Rename "';
ENTER_THE_NEW_NAME = "Enter the new name";
SAVE_PACKAGE_FIRST_ = "Save Package first?";
THE_CURRENT_PACKAGE_HAS_BEEN_MODIFIED_AND_NOT_YET_SAVED_ = "The current package has been modified and not yet saved. ";
WOULD_YOU_LIKE_TO_SAVE_IT_BEFORE_LOADING_THE_NEW_PACKAGE_ = "Would you like to save it before loading the new package?";
DISCARD = 'Discard';
SELECT_A_FILE = "Select a File";
EXE_PACKAGE_FILES = "eXe Package Files";
APPARENTLY_USELESS_TITLE_WHICH_IS_OVERRIDDEN = "Apparently Useless Title which is Overridden";
IDEVICE_EDITOR = "iDevice Editor";
PREFERENCES = "Preferences";
METADATA_EDITOR = "metadata editor";
ABOUT = "About";
SELECT_THE_PARENT_FOLDER_FOR_EXPORT_ = "Select the parent folder for export.";
EXPORT_TEXT_PACKAGE_AS = "Export text package as";
TEXT_FILE = "Text File";
EXPORT_COMMONCARTRIDGE_AS = "Export Common Cartridge as";
EXPORT_SCORM_PACKAGE_AS = "Export SCORM package as";
EXPORT_IMS_PACKAGE_AS = "Export IMS package as";
EXPORT_WEBSITE_PACKAGE_AS = "Export Website package as";
EXPORT_IPOD_PACKAGE_AS = "Export iPod package as";
INVALID_VALUE_PASSED_TO_EXPORTPACKAGE = "INVALID VALUE PASSED TO exportPackage";
SELECT_PACKAGE_TO_INSERT = "Select package to insert";
SAVE_EXTRACTED_PACKAGE_AS = "Save extracted package as";
OVERWRITE_DIALOG = "\nFile already exists. Would you like to overwrite?"
NODE_WAS_NOT_MOVED = "An server error occured. Node was not moved."
CANT_MOVE_NODE_FURTHER = "Can't move up any farther"
NOT_IMPLEMENTED = "This function is not implemented yet."
SAVE_DIRTY_PACKAGE = "Package has been changed. Do you want to save it, before you leave?"

// initialize
jQuery(document).ready(function() {
                $.jsonRPC.setup({
                   endPoint: '/exeapp/json/',
                   namespace: 'package',
                });
                $("a.bigButton, a.smallButton").button();
                // Initialize outline tree
                $.jstree._themes = "/static/css/themes/"
                get_outline_pane().jstree({
                  "core" : {"animation" : 200},
                  "ui" : {"select_limit" : 1, 
                      "initially_select" : ["node" + get_outline_pane().attr("current_node")]},
                  "plugins" : ["themes", "html_data", "ui", "crrm"]});
                get_outline_pane().jstree('open_all', $('#outline_pane>ul'));
                //bind actions to outline nodes
                get_outline_pane().bind("select_node.jstree", 
                      handle_select_node);
                get_outline_pane().delegate("a", "dblclick", rename_current_node);
                //bind renaming event
                get_outline_pane().bind("rename_node.jstree", handle_renamed_current_node);
                // handle theme selection
                set_current_style()
                $("#style_selector").change(handle_select_style);
                $("#export_link").click(handle_export);
                
                
                // Initialize idevice Tree
                $("#idevicePane").jstree({"plugins" : ["themes", "html_data", "ui"]})
                $("#idevicePane").jstree('open_all', $('#idevicePane>ul'));
                                   
                //$("#authoring").attr('src',
                //    document.location.pathname + "authoring/");
                $("#propertiesIFrame").attr('src',
                    document.location.pathname + "properties/");
                    
                
                //bind actions to outline buttons
                $("#btnAdd").click(add_child_node)
                $("#btnRemove").click(delete_current_node)
                $("#btnRename").click(rename_current_node);
                $("#btnDuplicate").click(function() {alert(NOT_IMPLEMENTED);});
                
                $("#btnPromote").click(promote_current_node);
                $("#btnDemote").click(demote_current_node);
                $("#btnUp").click(move_current_node_up);
                $("#btnDown").click(move_current_node_down);
                
                //$(".bigButton:not(#btnRename), .smallButton").each(function(index) {
                //    bindButtonClicked(this);
                //});
                //bind action to idevice items
                $("#idevicePane").delegate(".ideviceItem", "click", add_idevice);
                $("#middle").tabs();
                updateTitle();
                //uncomment to block UI. Quite slow
                //$(document).ajaxStart($.blockUI).ajaxStop($.unblockUI);
                
            });
            
// Adds a new node to current one
function add_child_node() {
  
  $.jsonRPC.request('add_child_node', [get_package_id()], {
    success: function(results) {
      callback_add_child_node(results.result.id, results.result.title);
    }
  })
}



//Removes current node
function delete_current_node() {
  $.jsonRPC.request('delete_current_node', [get_package_id()], {
    success: function(results) {
      if (results.result.deleted == 1) {
        callback_delete_current_node();
      }
    }
  })
}

//Simply triggeds jstree's rename routine
function rename_current_node(){
  if (get_current_node().attr('id') != "node" + current_outline_id()) {
      alert("Somehow you managed to call dblclik event without a single click. Please, reload page!");
      return null;
  }
  get_outline_pane().jstree("rename");
}

// Promotes current node to a sibling of it's parent.
function promote_current_node(){
  // check if the current node is the root or a child of the root
  if (is_root(get_current_node()) || 
  is_root(get_current_node().parent().parent().parent())) {
              alert(CANT_MOVE_NODE_FURTHER);
              return -1;
            }
  $.jsonRPC.request('promote_current_node', [get_package_id()], {
    success: function(results){
      if (results.result.promoted != "1") {
        alert(NODE_WAS_NOT_MOVED);
      } else {
        callback_promote_current_node();
      }
    }
  });
}

function demote_current_node() {
  // Check if current node if a root
  if (is_root(get_current_node())) {
    alert("Can't demote the root.");
  } else 
    // Check if there are any nodes before current one on the same level
    if (get_current_node().parent().prev().length == 0) {
      alert ("No previous node, can't demote.");
    } else {
      $.jsonRPC.request('demote_current_node', [get_package_id()], {
        success: function(results) {
          if (results.result.demoted != "1") {
            alert(NODE_WAS_NOT_MOVED);
          } else {
            callback_demote_current_node();
          }
        }
      });
    }
}

// Move node up at the same level
function move_current_node_up(){
  // Check if there are any nodes before the current one on the same level
  if (get_current_node().parent().prev().length == 0) {
    alert(CANT_MOVE_NODE_FURTHER);
  }
  $.jsonRPC.request('move_current_node_up', [get_package_id()], {
      success: callback_move_current_node_up,
      error: function(result) { alert (NODE_WAS_NOT_MOVED); }
    });
}

// Move current node down at the same level
function move_current_node_down() {
  if (get_current_node().parent().next().length == 0) {
    alert(CANT_MOVE_NODE_FURTHER);
    return -1;
  }
  $.jsonRPC.request('move_current_node_down', [get_package_id()], {
    success: function(results) {
      if (results.result.moved != '1'){
        alert(NODE_WAN_NOT_MOVED);
      } else {
        callback_move_current_node_down();
      }
    }
  });
}

function add_idevice() {
  var ideviceid = $("#idevicePane").jstree("get_selected").find(">a").attr('ideviceid');
  $.jsonRPC.request('add_idevice', [get_package_id(), ideviceid],{
    success: function(results) {
    	window.frames['authoringIFrame1'].add_idevice(
    		results.result.idevice_id
    	);
    }
  });
  return false;
}

// Handles outline_pane selection event. Calls package.change_current_node
// via rpc. 
function handle_select_node(event, data) {

    var node = get_current_node();
    $.jsonRPC.request('change_current_node',
    [get_package_id(), $(node).attr("nodeId")], {
        success: function(results) {
              set_current_node(node);
        }
    });
    return false;
}

function handle_select_style() {
	
	$.jsonRPC.request("set_package_style", [get_package_id(), $("#style_selector").val()],
	{success: function() {
		// fully reload iframe to apply new style sheets
		window.frames.authoringIFrame1.location = 'authoring/';
	}});
}

function handle_export(e) {
	var export_type = $("#export_selector").val();
	var url = $("#export_link").attr("href").slice(0, -1) + export_type + "/";
	alert(url); 
	/*var download_iframe = $("<iframe />")
		.attr("src", url)
		.hide().
		appendTo(document);
	
	// download_iframe.delete();*/
	// e.preventDefault();
	window.location.href = url;
	return false;
}

//handle renamed node event. Calls package.rename_node over rpc.
function handle_renamed_current_node(e, data){
  var new_title = data.rslt.name;
  $.jsonRPC.request('rename_current_node', [get_package_id(), new_title], {
    success: function(results){
      var server_title = ""
      if ("title" in results.result){
        server_title = results.result.title;
        reload_authoring();
      }
      if (new_title != server_title){
        alert("Server couldn't rename the node");
        get_current_node().html($("<ins />").addClass('jstree-icon'));
        get_current_node().append(server_title);
      }
    }});
}

// Returns the _exe_nodeid attribute of the currently selected row item
function current_outline_id(index)
{
    return get_current_node().attr('nodeId');
}

var outlineButtons = new Array('btnAdd', 'btnDel', 'btnRename', 'btnPromote', 'btnDemote', 'btnUp', 'btnDown', 'btnDbl')

function disableButtons(state) {
    if (state){
        //$(".bigButton, .smallButton").button("disable");
        $.blockUI();
    } else {
        enableButtons();
    }
}


function addStyle() {
    var src = addDir();
    $.jsonRPC('importStyle', [get_package_id(),'',src]);
}

function enableButtons() {
    //$(".bigButton, .smallButton").button('enable');
    $.unblockUI();
}

function get_package_id(){
  return $("#package_id").text()
}

// Appends a child node with name and _exe_nodeid to the currently
// selected node
function callback_add_child_node(nodeid, title) {
    var current_li = get_current_node().parent();
    var new_node = {'data' : {'title' : title, 
        'attr': {'id' : 'node' + nodeid, 'nodeid' : nodeid}}}
    get_outline_pane().jstree("create_node",current_li, "last", new_node);
    get_outline_pane().jstree("open_node", current_li);
    get_outline_pane().jstree("select_node", $("#node" + nodeid), true);
}

// Delete the currently selected node
function callback_delete_current_node() {
    var currentNode = get_current_node();
    // parent ul
    get_outline_pane().jstree("delete_node", currentNode);
    updateTitle();
}

// Move the node to the same level as it's parent and place it after.
function callback_promote_current_node() {
  // Move through <li>, <ul> to parent's <li>
  var parent_container_node = get_current_node().parent().parent().parent()
  move_current_node_to_neighbour(parent_container_node, "after")
}

function callback_demote_current_node() {
  var previous_node = get_current_node().parent().prev();
  move_current_node_to_neighbour(previous_node, "last")
}

// Move current node before the previous
function callback_move_current_node_up() {
  var neighbour_node = get_current_node().parent().prev();
  move_current_node_to_neighbour(neighbour_node, "before")
}

// Move current node after the next
function callback_move_current_node_down() {
  var neighbour_node = get_current_node().parent().next();
  move_current_node_to_neighbour(neighbour_node, "after");
}

// places the current node to position relatively to neighbour
function move_current_node_to_neighbour(neighbour_node, position) {
	var current_node = get_current_node();
	get_outline_pane().jstree("move_node", current_node, neighbour_node, position);
}



// Checks if node is root, saves a lot parent() in the code
function is_root(node) {
  // Get parent li, if node is a <a>-reference
  if ($(node).is('a')) {
    node = $(node).parent();
  }
  return (node.parent().parent().attr('id') == 'outline_pane');
}

// called to synchronize current_node attribute of outline_pane with 
// currently selected node. Refreshes authoring
function set_current_node(node) {
  get_outline_pane().attr('current_node', get_current_node().attr('nodeid'));
  updateTitle();
  reload_authoring();
}

function set_current_style() {
	$.jsonRPC.request('get_current_style', [get_package_id()],
		{success: function(results){
			var style_val = results.result.style;
			$("#style_selector").val(style_val);
		}});
}

function get_current_node() {
    var selected = get_outline_pane().jstree("get_selected").find(">a");
    return selected;
}

function get_outline_pane() {
  return $("#outline_pane");
}

// Reloads content of authoring part. Convinience function, just 
// calls reload from authoring iframe
function reload_authoring(){
	if ("reload_authoring" in window.frames['authoringIFrame1']) {
  		window.frames['authoringIFrame1'].reload_authoring();
	} else {
		window.frames['authoringIFrame1'].location = 'authoring/';
	}
}

function setDocumentTitle(title) {
    document.title = title + " : " + $(".curNode").text();
}

// Call this to ask the server if the package is dirty
// 'ifDirty' will be evaled if the package is dirty
function checkDirty(ifClean, ifDirty) {
    $.jsonRPC('isPackageDirty', [get_package_id(),'',ifClean,ifDirty]);
}


// This is called by the server to ask the user if they want to save their
// package before changing filenew/fileopen
// 'onProceed' is a string that is evaluated after the package has been saved or
// the user has chosen not to save the package, but not if user cancels
function askSave(onProceed) {
    netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect")
    var promptClass = Components.classes["@mozilla.org/embedcomp/prompt-service;1"]
    var promptService = promptClass.getService(Components.interfaces.nsIPromptService)
    var flags = promptService.BUTTON_TITLE_SAVE * promptService.BUTTON_POS_0 +
                promptService.BUTTON_TITLE_IS_STRING * promptService.BUTTON_POS_1 +
                promptService.BUTTON_TITLE_CANCEL * promptService.BUTTON_POS_2
    var res = promptService.confirmEx(window,SAVE_PACKAGE_FIRST_,
                                      THE_CURRENT_PACKAGE_HAS_BEEN_MODIFIED_AND_NOT_YET_SAVED_ +
                                      WOULD_YOU_LIKE_TO_SAVE_IT_BEFORE_LOADING_THE_NEW_PACKAGE_,
                                      flags, null, DISCARD, null, '', {});
    if (res == 0) {
      // If we need to save the file
      // go through the whole save process
      fileSave(onProceed)
    } else if (res == 1) {
      // If Not to be saved, contiue the process
      eval(onProceed)
    } else if (res == 2) {
      // If cancel loading, cancel the whole process
      return
    }
}

// This is called when a user wants to create a new package
function fileNew() {
    // Ask the server if the current package is dirty
    askDirty("window.top.location = '/'")
}

function tabNew() {
    $.jsonRPC('openNewTab', [get_package_id(),]);
}

function openPreview(path) {
    netscape.security.PrivilegeManager.enablePrivilege("UniversalFileRead");
    window.open("file://" + path);
}

function openNewTab(port) {
    //used to open new tab for a new server
    window.open("http://127.0.0.1:" + port)
}

// This is called when a user wants to open a new file
// It starts a chain of fileOpenX() funcs...
function fileOpen() {
    // Ask the server if the current package needs changing
    // And once we have the answer, go to fileOpen2()
    // The ansert is stored by the server in the global variable
    // isPackageDirty
    askDirty('fileOpen2()')
}

//gets editors width in pixel and sets its width accordingly
function setEditorsWidth() {
	var width = prompt("Enter editor's new width. 0 or empty to set it to 100%");
	$.jsonRPC('setEditorsWidth', [get_package_id(),'',width]);
}

// Shows the the load dialog and actually loads the new package
function fileOpen2() {
    netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect")
    var nsIFilePicker = Components.interfaces.nsIFilePicker;
    var fp = Components.classes["@mozilla.org/filepicker;1"].createInstance(nsIFilePicker);
    fp.init(window, SELECT_A_FILE, nsIFilePicker.modeOpen);
    fp.appendFilter(EXE_PACKAGE_FILES,"*.elp");
    fp.appendFilters(nsIFilePicker.filterAll);
    var res = fp.show();
    if (res == nsIFilePicker.returnOK) {
        $.jsonRPC('loadPackage', [get_package_id(),'',fp.file.path]);
    }
}

// Opens the tutorial document
function fileOpenTutorial() {
    askDirty("fileOpenTutorial2();")
}

// Actually does the opening of the tutorial document, 
// once the current package has  been saved or discarded
function fileOpenTutorial2() {
    $.jsonRPC('loadTutorial', [get_package_id(),'']);
}


// Opens a recent document
function fileOpenRecent(number) {
    askDirty("fileOpenRecent2('" + number + "');")
}

// Actually does the openning of the recent file, once the current package has 
// been saved or discarded
function fileOpenRecent2(number) {
    $.jsonRPC('loadRecent', [get_package_id(),'',number]);
}

// Clear recent files menu
function fileRecentClear() {
    $.jsonRPC('clearRecent', [get_package_id(),'']);
}

// Called by the user when they want to save their package
// Also called by some java scripts.
function fileSave() {
    $.jsonRPC.request("save_data_package", [get_package_id()], undefined, undefined, false);
}

// Takes the server's response after we asked it for the
// filename of the package we are currently editing
function fileSave2(filename, onDone) {
    if (filename) {
        saveWorkInProgress();
        // If the package has been previously saved/loaded
        // Just save it over the old file
        if (onDone) {
            $.jsonRPC('savePackage', [get_package_id(),'','',onDone]);
        } else {
            $.jsonRPC('savePackage', [get_package_id(),'']);
        }
    } else {
        // If the package is new (never saved/loaded) show a
        // fileSaveAs dialog
        fileSaveAs(onDone)
    }
}

function askOverwrite(filename, stylesDir) {
    if (confirm(filename + OVERWRITE_DIALOG)) {
        $.jsonRPC('exportWebSite2', [get_package_id(),'',filename,stylesDir]);
        }
}

// Called by the user when they want to save their package
function fileSaveAs(onDone) {
    netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect")
    var nsIFilePicker = Components.interfaces.nsIFilePicker;
    var fp = Components.classes["@mozilla.org/filepicker;1"].createInstance(nsIFilePicker);
    fp.init(window, SELECT_A_FILE, nsIFilePicker.modeSave);
    fp.appendFilter(EXE_PACKAGE_FILES,"*.elp");
    var res = fp.show();
    if (res == nsIFilePicker.returnOK || res == nsIFilePicker.returnReplace) {
        saveWorkInProgress();
        if (onDone) {
            $.jsonRPC('savePackage', [get_package_id(),'',fp.file.path,onDone]);
        } else {
            $.jsonRPC('savePackage', [get_package_id(),'',fp.file.path]);
        }
    } else {
        eval(onDone)
    }
}


// the first in a multi-function sequence for printing:
function filePrint() {
   // filePrint step#1: create a temporary print directory, 
   // and return that to filePrint2, which will then call exportPackage():
   netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect")
   var tmpdir_suffix = ""
   var tmpdir_prefix = "eXeTempPrintDir_"
   nevow_clientToServerEvent('makeTempPrintDir', this, '', tmpdir_suffix, 
                              tmpdir_prefix, 'filePrint2')
   // note: as discussed below, at the end of filePrint3_openPrintWin(), 
   // the above makeTempPrintDir also removes any previous print jobs
}

function filePrint2(tempPrintDir, printDir_warnings) {
   if (printDir_warnings.length > 0) {
      alert(printDir_warnings)
   }
   exportPackage('printSinglePage', tempPrintDir, "filePrint3_openPrintWin");
}

function filePrint3_openPrintWin(tempPrintDir, tempExportedDir, webPrintDir) {
    // okay, at this point, exportPackage() has already been called and the 
    // exported file created, complete with its printing Javascript
    // into the tempPrintDir was created (and everything below it, and 
    // including it, will need to be removed), the actual files for printing 
    // were exported into tempExportedDir/index.html, where tempExportedDir 
    // is typically a subdirectory of tempDir, named as the package name.

   netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect")

    // Still needs to be (a) opened, printed, and closed:
    var features = "width=680,height=440,status=1,resizable=1,left=260,top=200";
    print_url = webPrintDir+"/index.html"

    printWin = window.open (print_url, 
                  APPARENTLY_USELESS_TITLE_WHICH_IS_OVERRIDDEN, features);


    // and that's all she wrote!

    // note that due to difficulty with timing issues, the files are not 
    // (yet!) immediately removed upon completion of the print job 
    // the hope is for this to be resolved someday, somehow, 
    // but for now the nevow_clientToServerEvent('makeTempPrintDir',...) 
    // call in filePrint() also clears out any previous print jobs,
    // and this is called upon Quit of eXe as well, leaving *at most* 
    // one temporary print job sitting around.
} // function filePrint3_openPrintWin()


function serveDocument() {
    $.jsonRPC('serveDocument', [get_package_id(),]);
}

function stopServing() {
    $.jsonRPC('stopServing', [get_package_id(),]);
}


function handoutPrint() {
   // for fuction description look at filePrint comments
   netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect")
   var tmpdir_suffix = ""
   var tmpdir_prefix = "eXeTempPrintDir_"
   nevow_clientToServerEvent('makeTempPrintDir', this, '', tmpdir_suffix, 
                              tmpdir_prefix, 'handoutPrint2')
}

function handoutPrint2(tempPrintDir, printDir_warnings) {
   if (printDir_warnings.length > 0) {
      alert(printDir_warnings)
   }
   exportPackage('printHandout', tempPrintDir, "filePrint3_openPrintWin");
}


// Quit the application
function fileQuit() {
    // Call file - save as
    this.wrappedJSObject = this;
    saveWorkInProgress()
    askDirty('doQuit()')
}

// Closes the window and stops the server
function doQuit() {
    netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect")
    $.jsonRPC('quit', [get_package_id(),'']);
    //var start = new Date().getTime();
    //while (new Date().getTime() < start + 500);
    //klass = Components.classes["@mozilla.org/toolkit/app-startup;1"]
    //interfac = Components.interfaces.nsIAppStartup
    //instance = klass.getService(interfac)
    //instance.quit(3)
    window.open('', '_parent', '');
    window.close();
}

// Submit any open iDevices
function saveWorkInProgress() {
    // Do a submit so any editing is saved to the server
    $("#authoringIFrame").contents().find("#contentForm").submit();
}

// Launch the iDevice Editor Window
function toolsEditor() {
    var features  = "width=800,height=700,status=no,resizeable=yes,"+
                    "scrollbars=yes";
    var editorWin = window.open("/editor", IDEVICE_EDITOR, features);
}

// Launch the Preferences Window
function toolsPreferences() {
    var features  = "width=450,height=200,status=no,resizeable=yes,"+
                    "scrollbars=yes";
    var editorWin = window.open("/preferences", PREFERENCES, features);
}

function importPDF() {
    var features = "width=510,height=225, status=no,resizeable=yes" +
                "pageXOffset=100,pageYOffset=100";
    var pdfWin = window.open("/importPDF", "Import PDF", features);
}

// launch brents crazy robot metadata editor and tag warehouse 
// loads the metadata editor
// of course i don't really know what to do after here ...
// but you get the idea right ;-) i just make em look purty!

function metadataEditor() {
    var features = "width=500,height=640,status=yes,resizeable=yes,scrollbars=yes";
    var metadataWin = window.open ("/templates/metadata.xul", METADATA_EDITOR, features);
}

// load the About page
function aboutPage() {
    var features = "width=299,height=515,status=0,resizable=0,left=260,top=150";
    aboutWin = window.open ("/about", ABOUT, features);
}

// browse the specified URL in system browser
function browseURL(url) {
    $.jsonRPC('browseURL', [get_package_id(),'',url]);
}

// Appends an iDevice
// XH means that the func is actually called by the server over xmlhttp
function XHAddIdeviceListItem(ideviceId, ideviceTitle) {
    var list = document.getElementById('ideviceList');
    // Create the new listitem
    var newListItem = document.createElement('listitem')
    newListItem.setAttribute("onclick", 
                             "submitLink('AddIdevice', "+ideviceId+", 1);")
    newListItem.setAttribute("label", unescape(ideviceTitle))
    list.appendChild(newListItem)
    updateTitle();
}

function addIdevice(ideviceId) {
  $.jsonRPC.request('addidevice', [get_current_package(), ideviceId],{
    success: function(result) {
      alert('Idevice added');
    }
  })
    submitLink('AddIdevice', ideviceId, 1);
}

function updateTitle() {
    // nevow_clientToServerEvent("updateTitle", this);
}


// This function takes care of all
// exports. At the moment, this means web page export
// and scorm packages, with and without meta data
// 'exportType' is passed straight to the server
// Currently valid values are:
// 'scoem' 'ims' 'webSite'
// 'presentation' exports marked freetext passages to a
// DOMSlides-presentation

function quickExport() {
    $.jsonRPC('quickExport', [get_package_id(),]);
}

function exportPackage(exportType, exportDir, printCallback) {
    netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");

    var nsIFilePicker = Components.interfaces.nsIFilePicker;
    var fp = Components.classes["@mozilla.org/filepicker;1"].createInstance(nsIFilePicker);
    if (exportType == 'webSite' || exportType == 'singlePage' || exportType == 'printSinglePage' || exportType == 'ipod' || exportType == 'presentation' || exportType == 'printHandout') {
        if (exportDir == '') {
            fp.init(window, SELECT_THE_PARENT_FOLDER_FOR_EXPORT_,
                         nsIFilePicker.modeGetFolder);
            var res = fp.show();
            if (res == nsIFilePicker.returnOK || res == nsIFilePicker.returnReplace) {
                $.jsonRPC('exportPackage', [get_package_id(),'',exportType,fp.file.path,'']);
            }
        }
        else {
            // use the supplied exportDir, rather than asking.
            // NOTE: currently only the printing mechanism will provide an exportDir, hence the printCallback function.
            $.jsonRPC('exportPackage', [get_package_id(),'',exportType,exportDir,printCallback]);
        }
    } else if(exportType == "textFile"){
        title = EXPORT_TEXT_PACKAGE_AS;
        fp.init(window, title, nsIFilePicker.modeSave);
        fp.appendFilter(TEXT_FILE, "*.txt");
        fp.appendFilters(nsIFilePicker.filterAll);
        var res = fp.show();
        if (res == nsIFilePicker.returnOK || res == nsIFilePicker.returnReplace)
            $.jsonRPC('exportPackage', [get_package_id(),'',exportType,fp.file.path]);
    } else {
        if (exportType == "scorm")
            title = EXPORT_SCORM_PACKAGE_AS;
        else if (exportType == "ims")
            title = EXPORT_IMS_PACKAGE_AS;
        else if (exportType == "zipFile")
            title = EXPORT_WEBSITE_PACKAGE_AS;
	else if (exportType == "commoncartridge")
	    title = EXPORT_COMMONCARTRIDGE_AS;
        else
            title = INVALID_VALUE_PASSED_TO_EXPORTPACKAGE;
        fp.init(window, title, nsIFilePicker.modeSave);
        fp.appendFilter("SCORM/IMS/ZipFile", "*.zip");
        fp.appendFilters(nsIFilePicker.filterAll);
        var res = fp.show();
        if (res == nsIFilePicker.returnOK || res == nsIFilePicker.returnReplace) {
            $.jsonRPC('exportPackage', [get_package_id(),'',exportType,fp.file.path]);
        }
    }
} // exportPackage()


// This function takes care of mergeing packages
function insertPackage() {
    netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
    var nsIFilePicker = Components.interfaces.nsIFilePicker;
    var fp = Components.classes["@mozilla.org/filepicker;1"].createInstance(nsIFilePicker);
    fp.init(window, SELECT_PACKAGE_TO_INSERT, nsIFilePicker.modeOpen);
    fp.appendFilter(EXE_PACKAGE_FILES,"*.elp");
    fp.appendFilters(nsIFilePicker.filterAll);
    var res = fp.show();
    if (res == nsIFilePicker.returnOK) {
        $.jsonRPC('insertPackage', [get_package_id(),'',fp.file.path]);
    }
}

// This function takes care of mergeing packages
function extractPackage() {
    netscape.security.PrivilegeManager.enablePrivilege("UniversalXPConnect");
    var nsIFilePicker = Components.interfaces.nsIFilePicker;
    var fp = Components.classes["@mozilla.org/filepicker;1"].createInstance(nsIFilePicker);
    fp.init(window, SAVE_EXTRACTED_PACKAGE_AS, nsIFilePicker.modeSave);
    fp.appendFilter(EXE_PACKAGE_FILES,"*.elp");
    fp.appendFilters(nsIFilePicker.filterAll);
    var res = fp.show();
    if (res == nsIFilePicker.returnOK || res == nsIFilePicker.returnReplace) {
        $.jsonRPC('extractPackage', [get_package_id(),'',fp.file.path,res == nsIFilePicker.returnReplace]);
    }
}

