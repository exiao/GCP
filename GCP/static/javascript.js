$(".loading").on("click", function(){
    $(this).button('loading');
})

$(".folder-delete").click(function() {
    var folder_id = $(this).attr("value")
    var check = confirm("This action is permanent, would you like to proceed?")
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