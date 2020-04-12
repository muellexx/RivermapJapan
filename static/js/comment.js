var current_url;

function fourImages(comment) {
if (comment.imageSize == 'main'){
    imgClass = "col-lg-3 col-md-4 col-6";
} else {
    imgClass = "col-6";
}
html = '<div class="row justify-content-center">';
if (comment.image1 != null){
    html += '<div class="' + imgClass + '">';
    html += '<img class="m-1 img-fluid img-thumbnail" style="cursor: pointer;" onclick="enlargeImage(' + "'" + comment.image1 + "'" + ')" src="' + comment.image1 + '">';
    html += '</div>';
}
if (comment.image2 != null){
    html += '<div class="' + imgClass + '">';
    html += '<img class="m-1 img-fluid img-thumbnail" style="cursor: pointer;" onclick="enlargeImage(' + "'" + comment.image2 + "'" + ')" src="' + comment.image2 + '">';
    html += '</div>';
}
if (comment.image3 != null){
    html += '<div class="' + imgClass + '">';
    html += '<img class="m-1 img-fluid img-thumbnail" style="cursor: pointer;" onclick="enlargeImage(' + "'" + comment.image3 + "'" + ')" src="' + comment.image3 + '">';
    html += '</div>';
}
if (comment.image4 != null){
    html += '<div class="' + imgClass + '">';
    html += '<img class="m-1 img-fluid img-thumbnail" style="cursor: pointer;" onclick="enlargeImage(' + "'" + comment.image4 + "'" + ')" src="' + comment.image4 + '">';
    html += '</div>';
}
html += '</div>';
return html;
}

function loadComment(comment) {
html = '<article class="media content-section">'
html += '<div class="media-body">'
html += '<div class="article-metadata row">'
html += '<img class="rounded-circle comment-img" src="' + comment.image_url + '">'
html += '<div class="col">'
html += '<a class="mr-2" href="user/' + comment.author + '">' + comment.author + '</a>'
if(document.documentElement.lang == 'ja'){
    html += '<small class="text-muted">' + comment.date_posted_jp + '</small>'
} else {
    html += '<small class="text-muted">' + comment.date_posted + '</small>'
}
html += '<h4>' + comment.title + '</h4>'
html += '</div></div>'
html += '<p class="article-content">' + comment.content + '</p>'
html += fourImages(comment);
html += '</div></article>'
return html;
}

function loadComments(sectionComments) {
    $.getJSON("/static/js/data/mapObjectComments.json", {_: new Date().getTime()}, function(json){
        comments = json.comments;
        for (let i = 0; i < sectionComments.length; i++){
            sectionComment = sectionComments[i];
            comment = comments.find(x => x.id === sectionComment);
            html = loadComment(comment);
            $("#sb-comments").prepend(html);
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

function newCommentCancel () {
    $('#sb-comment-form').hide();
    $('#sb-new-comment').show();
}

$(document).on('submit', '#sb-comment-form', function(e){
    e.preventDefault();
    $form = $(this);
    var formData = new FormData(this);
    formData.append("object_type", $('#object_type').val());

    $.ajax({
        url: window.location.pathname,
        type: 'POST',
        //enctype: 'multipart/form-data',
        //url: this.current_url,
        data: formData,
        success: function(json){
            html = loadComment(json);
            document.getElementById("sb-comment-form").reset();
            $('#sb-new-comment').show();
            document.getElementById("sb-comment-form").style.display = "none";
            $("#sb-comments").prepend(html);
        },
        cache: false,
        contentType: false,
        processData: false,
        error: function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
});
