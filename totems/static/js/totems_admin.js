var base_url = "http://69.164.222.39:8000/";

$(document).ready(function() {

    $(".action_render_reply_modal").live("click", function() {
        $("#modalAddReply").modal('show');
        $("#id_parent_message_id").val($(this).attr("data-id"));
    });

    $(".action_delete_message").live("click", function() {
        message_id = $(this).attr("data-id");
        data = {"message_id":message_id};
        ajax("messages/delete/"+message_id+"/",data,function (response) {

            $("#msg-"+message_id+" .delete_btn").hide();
            $("#msg-"+message_id).addClass("deleted");
        });
    });

    $(".action_mark_spam_message").live("click", function() {
        message_id = $(this).attr("data-id");
        data = {"message_id":message_id};
        ajax("messages/mark/spam/"+message_id+"/",data,function(response) {
            count = parseInt($("#num_spam_"+message_id).html());

            if(response.state === true) {
                count++;
            } else {
                count--;
            }

            $("#num_spam_"+message_id).html(count);
        });
    });

    $(".action_mark_flag_message").live("click", function() {
        message_id = $(this).attr("data-id");
        data = {"message_id":message_id};
        ajax("messages/mark/flag/"+message_id+"/",data,function(response) {
            count = parseInt($("#num_flag_"+message_id).html());

            if(response.state === true) {
                count++;
            } else {
                count--;
            }

            $("#num_flag_"+message_id).html(count);

        });
    });
    $(".action_mark_upvote_message").live("click", function() {
        message_id = $(this).attr("data-id");
        data = {"message_id":message_id};
        ajax("messages/mark/upvote/"+message_id+"/",data,function(response) {
            count = parseInt($("#num_vote_"+message_id).html());

            if(response.state === true) {
                count++;
            } else {
                count--;
            }

            $("#num_vote_"+message_id).html(count);

        });
    });
    $(".action_mark_downvote_message").live("click", function() {
        message_id = $(this).attr("data-id");
        data = {"message_id":message_id};
        ajax("messages/mark/downvote/"+message_id+"/",data,function(response) {
            count = parseInt($("#num_vote_"+message_id).html());

            if(response.state === true) {
                count--;
            } else {
                count++;
            }

            $("#num_vote_"+message_id).html(count);

        });
    });

});

function ajax(url, data, success) {
    
	return $.ajax({
	    url: base_url + url,
	    type: 'POST',
	    dataType: 'json',
	    data: data,
	    error: function(jqXHR, textStatus, errorThrown) {
	    },
	    success: function(response) {
            success(response);
	    }
	});
}

// allow CSRF verification to work on AJAX requests with Django
$(document).ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    function sameOrigin(url) {
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    function safeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
});
