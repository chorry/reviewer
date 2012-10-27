$(document).ready(function () {
    var notes = $.fn.stickyNote();
    var orphansToReview = [];
    $('.changed_path_file').live("click", function (e) {

        e.preventDefault();
        console.debug($(e.target));
        path = $(e.target).attr('file') + '/' + $(e.target).attr('rev1') + '/' + $(e.target).attr('rev2');
        $.ajax({
            url:'/get/diff/' + path
        }).done(function (data) {
                console.debug(data);
            }
        );
    });

    $('.expand_orphan_file_list').live('clicl', function(e) {
        $.ajax({
            type:'GET',
            url:'/ajax/addReviewItem/'+
                $(e.target).attr('x-vcs')+'/'+
                $(e.target).attr('x-reviewId')
        }).done(function(d){

        });
    });

    //add repo
    $('#add_repo_button').live('click', function(e) {
        $.ajax({
            url:'/ajax/addRepo/' + $("#add_repo_type option:selected").val() + '/' + $('#add_repo_value').val()
        }).done(function (data) {
                console.debug(data);
                var className = 'alert-success';
                if (data != 'Ok')
                {
                    className = 'alert-error';
                }
                notes.create ({noteContent: data, className: className});
            }
        );
    })


    //add commit to review
    $('.create_review').live('click', function(e){
        console.debug(orphansToReview);
        $.ajax({
            type:'GET',
            url:'/ajax/addReviewItem/'+
                $(e.target).attr('x-vcs')+'/'+
                $(e.target).attr('x-author')+'/'+
                $(e.target).attr('x-revision1')+'/'+
                $(e.target).attr('x-revision2') + '/' +
                $(e.target).attr('x-count'),
            data: { items: orphansToReview }
        }).done(function (data) {
            if (data == 'true') {
                notes.create({noteContent:"Added! ", className:'alert-info', extended: false, time: 4000});
            } else {
                notes.create({noteContent:"Already exists ", className:'alert-error', extended: false, time: 4000});
            }
            console.debug(data);
        });
    });

    //create review from orphans
    $('.create_review_from_selected').live('click', function(e){
        console.debug(orphansToReview)
        $.ajax({
            type:'POST',
            url:'/ajax/addReviewItems',
            data: JSON.stringify( orphansToReview ),
            contentType: 'application/json;charset=UTF-8'
        }).done(function (data) {
                console.debug(data);
        });
    });

    //add selected to review :)
    $('.add_selected_to_review').live('click', function(e){
        console.debug($(e.target));
        var vcs = $(e.target).attr('x-vcs'),
            author=$(e.target).attr('x-author'),
            rev1=$(e.target).attr('x-revision1'),
            rev2=$(e.target).attr('x-revision2'),
            count=$(e.target).attr('x-count'),
            item_id=$(e.target).attr('x-itemid'),
            divId=vcs+'_'+author+'_'+rev1+'_'+rev2;
        orphansToReview.push ( {
        'vcs' : vcs,
        'author' : author,
        'rev1' : rev1,
        'rev2' : rev2,
        'itemid': item_id
        } );
        //updateOrphansReviewBlock
        $('#'+divId).remove();
        var tdiv = '<div id="'+divId+'" class="remove_orphans_from_review "><span><i class="icon-remove"></i></span> ' + count + ' files of ' + author + '(' +
            rev1 + ':' + rev2
            +')</div>';
            $(tdiv).appendTo('#create_review');
    });

    $('.remove_orphans_from_review').live('click', function(e){
        console.debug($(e.target));
        $(e.target).remove();
    });

});