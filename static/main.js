$(function () {
    $(".tochangeimg").click(function () {
        if ($(this).text() === 'Change to detected') {
            $(this).attr('class', 'tochangeimg btn btn-danger');
            $(this).text('Change to non-detected');
            $(this).parents().siblings('.image').attr('src', '/static/data/detected/' + this.id)
        } else {
            $(this).attr('class', 'tochangeimg btn btn-success');
            $(this).text('Change to detected');
            $(this).parents().siblings('.image').attr('src', '/static/data/uploads/' + this.id)
        }
    });
});
