$(document).ready(function() {
  $.jsonRPC.setup({
    endPoint: '/exeapp/json/',
    namespace: 'main',
  });
  $("#create_package").click(function(){
    var package_title = prompt('Enter package title');
    $.jsonRPC.request('create_package', [package_title], {
      success: function(results){
        add_new_package(results.result.id, results.result.title)
      }});
  })
})

function add_new_package(id, title){
  $("<li />")
  .addClass('package')
  .html($('<a />')
  .attr('href', 'package/' + id + '/')
  .text(title))
  .appendTo('#package_list')
}

