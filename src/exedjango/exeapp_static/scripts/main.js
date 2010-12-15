$(document).ready(function() {
  $.jsonRPC.setup({
    endPoint: '/exeapp/json/',
    namespace: 'main',
  });
  $("#create_package").click(create_package);
  $("#delete_selected_packages").click(delete_selected_packages);
})

// Promps a new package new and sens a "main.create_package" call via 
// rpc
function create_package(){
  var package_title = prompt('Enter package title');
    $.jsonRPC.request('create_package', [package_title], {
      success: function(results){
        callback_create_package(results.result.id, results.result.title)
      }
    });
}

// Deletes packages which idicated by selected checkboxes
function delete_selected_packages(){
  $(".package_checkbox:checked").
  each(function (i){
    var package_id = $(this).attr("packageid");
    $.jsonRPC.request('delete_package', [package_id], {
      success: function(results) {
        var deleted_package_id = results.result.package_id;
          if (deleted_package_id > 0) {
            // Just a pre-caution that we remove the same package as the
            // server
          callback_delete_package(deleted_package_id);
        }
      }
    })
  })
}

// Called after successful package creation
function callback_create_package(id, title){
  $("<li />")
  .addClass('package')
  .attr("id", "package" + id)
  // Append checkbox
  .append($('<input />')
  .attr('type', 'checkbox')
  .addClass('package_checkbox')
  // Append link to the package
  .attr('packageid', id))
  .append($('<a />')
  .attr('href', 'package/' + id + '/')
  .text(title))
  
  .appendTo('#package_list')
}

// Called after successful package deletion
function callback_delete_package(id) {
  var package_li = $("#package" + id);
  package_li.remove();
}

