

$(document).on('confirmation', '.remodal', function () {
    var isbn = $('#isbn').text()
    window.location.href='/gift/' + isbn
});
