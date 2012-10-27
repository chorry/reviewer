/**
 * Simple sticky note
 */

(function ($) {
    $.fn.stickyNote = function (o) {
        console.log('sticky init ok');
        var id = 0;
        var stickyNoteDiv = $('#jqnotice');
        var stickyNoteIdName = 'noteStickerId_';
        var defaultTtl = 500;
        var defaultSpeed = 'slow';
        var objects = {};

        return {
            create:function (stick, noteType) {
                var stick = $.extend({
                    time:defaultTtl,
                    speed:defaultSpeed,
                    noteContent:null,
                    className:null,
                    header:null,
                    extended: false, //show until forcefully closed
                    sticked:false, // no close button
                    position:{top:0, right:0} // default position
                }, stick);

                if (noteType == 'error') stick.className="alert-error";
                id += 1;
                console.log('++++++++');
                console.debug(stickyNoteDiv);
                console.debug(($('#jqnotice')));
                console.log('----');
                //init storage div, if not exists
                if (!$(stickyNoteDiv).length) {
                    $('body').append('<div id="jqnotice"></div>');
                    stickyNoteDiv = $('#jqnotice');
                }

                //create sticker itself
                stickyNoteDiv.css('position', 'fixed').css({right:'auto', left:'auto', top:'auto', bottom:'auto'}).css(stick.position);
                var stickItem = $('<div class="alert"></div>');
                stickyNoteDiv.append(stickItem);
                if (stick.className) stickItem.addClass(stick.className);
                stickItem.attr('id', stickyNoteIdName + id);
                stickItem.html(stick.noteContent);

                if (stick.extended)
                {
                    if (stick.sticked)
                    {
                        var exit = $('<a class="close">x</a>');
                        stick.prepend(exit);
                        exit.click(function () {
                            stickItem.fadeOut(stick.speed, function () {
                                $(this).remove();
                            })
                        });
                    }
                }
                else
                {
                    this.closeWithFadeOut(id, stick.time)
                }
                return id;
            },


            closeWithFadeOut:function(id, ttl)
            {
                if (typeof ttl == 'undefined')
                {
                   var ttl = defaultTtl;
                }
                var stickItem = $('#'+stickyNoteIdName+id);
                setTimeout(function () {
                    stickItem.fadeOut(defaultSpeed, function () {
                        $(this).remove();
                    });
                }, ttl);
            },

            /**
             * Updates content of existent sticker
             * @param id int
             * @param params object
             */
            update:function (id, params) {

                //get sticker by id
                var sticker = $('#'+stickyNoteIdName+id);
                if (!sticker.length) {
//                    console.log('cant find sticker #' + id + " for update");
                    return false;
                }
                if (typeof params.noteContent != 'undefined')
                {
                    sticker.html(params.noteContent);
                }

                if (typeof params.extended != 'undefined')
                {
                    if (params.extended == false)
                    {
                        this.closeWithFadeOut(id);
                    }
                }
            },

            destroy:function (id) {
                var sticker = $('#'+stickyNoteIdName+id);
                if (!sticker.length) {
//                    console.log('cant find sticker #' + id + " for destruction");
                    return false;
                }
                sticker.remove();
            }
        }
    };
})(jQuery);
