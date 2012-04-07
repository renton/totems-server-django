$(document).ready(function() {

    $(".action_render_reply_modal").live("click", function() {
        $("#modalAddReply").modal('show');
        $("#id_parent_message_id").val($(this).attr("data-id"));
    });

});
