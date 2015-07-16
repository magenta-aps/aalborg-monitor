(function($) {
    $("table.table-clickablerows tr").on("click", function(ev) {
        if(ev.which !== 1)
            return;
        var url = $(this).find(".rowclicktarget").first().attr("href");
        if (url) {
            document.location.href = url
        }
    });
})(jQuery);