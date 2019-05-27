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

function validate() {
    var pw1 = e("#pw-1").value;
    var pw2 = e("#pw-2").value;
    if (pw1 == pw2) {
        e("#password-msg").innerHTML = "";
        e("#submit").disabled = false;
    } else {
        e("#password-msg").innerHTML = "<font color='red'>两次密码不相同</font>";
        e("#submit").disabled = true;
    }
}




var __main = function() {
    initedEditor()
}


$(document).ready(function() {
    __main()
})
