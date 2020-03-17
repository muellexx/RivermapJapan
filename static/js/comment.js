var current_url;

function loadComments(sectionComments) {
    $.getJSON("/static/js/data/mapObjectComments.json", {_: new Date().getTime()}, function(json){
        comments = json.comments;
        for (let i = 0; i < sectionComments.length; i++){
            sectionComment = sectionComments[i];
            comment = comments.find(x => x.id === sectionComment);

            if(document.documentElement.lang == 'ja'){
                date_posted =comment.date_posted_jp;
            } else {
                date_posted =comment.date_posted;
            }

            $("#sb-comments").prepend('<article class="media content-section" style="margin: 0; margin-top: 5px; width: 100%;">'+
                '<div class="media-body">' +
                    '<div class="article-metadata row">' +
                        '<div class="column-md-5"><img class="rounded-circle comment-img" src="' + comment.image_url + '"></div>' +
                        '<div id="sb-comment-author" class="column-md-7"><a class="mr-2" href="user/' + comment.author + '">' + comment.author + '</a></br>' +
                        '<small class="text-muted">' + date_posted + '</small></div>' +
                    '</div>' +
                    '<h5>' + comment.title + '</h5>' +
                    '<p class="article-content">' + comment.content + '</p>' +
                '</div>' +
            '</article>'
            );
            if (comment.author == "Deleted User") {
                $("#sb-comment-author").html(comment.author);
            }
        }
    });
}

function setUrl (url) {
    this.current_url = url;
}

function newComment () {
    $('#sb-comment-form').show();
    $('#sb-new-comment').hide();
}

$(document).on('submit', '#sb-comment-form', function(e){
    $.ajax({
        type: 'POST',
        //url: this.current_url,
        data:{
            section:$('#id_section').val(),
            object_type:$('#object_type').val(),
            title:$('#id_title').val(),
            content:$('#id_content').val(),
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function(json){
            document.getElementById("sb-comment-form").reset();
            $('#sb-new-comment').show();
            document.getElementById("sb-comment-form").style.display = "none";
            $("#sb-comments").prepend('<article class="media content-section" style="margin: 0; margin-top: 5px; width: 100%;">'+
                '<div class="media-body">' +
                    '<div class="article-metadata row">' +
                        '<div class="column-md-5"><img class="rounded-circle comment-img" src="' + json.image_url + '"></div>' +
                        '<div id="sb-comment-author" class="column-md-7"><a class="mr-2" href="user/' + json.author + '">' + json.author + '</a></br>' +
                        '<small class="text-muted">' + json.date_posted + '</small></div>' +
                    '</div>' +
                    '<h5>' + json.title + '</h5>' +
                    '<p class="article-content">' + json.content + '</p>' +
                '</div>' +
            '</article>'
            );
        },
        error: function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
    e.preventDefault();
});
