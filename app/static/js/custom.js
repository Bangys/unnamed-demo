var initedEditor = function() {
    var e = new Editor()
    var element = $('.editor').get(0)
    e.render(element)
    return e
}


var trigger = $('.hamburger'),
    overlay = $('.overlay'),
    isClosed = false;

function hamburger_cross() {

    if (isClosed == true) {
        overlay.hide();
        // trigger.removeClass('is-open');
        // trigger.addClass('is-closed');
        isClosed = false;
    } else {
        overlay.show();
        // trigger.removeClass('is-closed');
        // trigger.addClass('is-open');
        isClosed = true;
    }
}

$('[data-toggle="offcanvas"]').click(function() {
    $('#wrapper').toggleClass('toggled');
});

$('.sidebar-brand').click(function() {
    $('#wrapper').toggleClass('toggled');
});


var __main = function() {
    initedEditor()
}

$(document).ready(function() {
    __main()
})
