$(".loading").on("click", function(){
    $(this).button('loading');
})

$(".folder-delete").click(function() {
    var folder_id = $(this).attr("value")
    var check = confirm("You're about to delete a folder and all its contents forever, would you like to proceed?")
    if (check) {
        data = {}
        data['csrfmiddlewaretoken'] = csrf_token
        data['folder_id'] = folder_id
          
        $.ajax({
          type: "POST",
          url: "/ajax_delete_folder/",
          data: data,
          success: function(){
            location.reload();
          }
        })
    }
})

$(".file-delete").click(function() {
    var file_id = $(this).attr("value")
    var check = confirm("You're going to delete this file forever, would you like to proceed?")
    if (check) {
        data = {}
        data['csrfmiddlewaretoken'] = csrf_token
        data['file_id'] = file_id
          
        $.ajax({
          type: "POST",
          url: "/ajax_delete_file/",
          data: data,
          success: function(){
            location.reload();
          }
        })
    }
})