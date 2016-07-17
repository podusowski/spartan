function stopwatch(html_element_id, start_time)
{
    var now = new Date();
    var diff = now.getTime() - start_time.getTime();

    document.getElementById(html_element_id).innerHTML = format_timespan(diff);
    setTimeout(function() { stopwatch(html_element_id, start_time); }, 500);
}

function format_timespan(ms)
{
    var second = Math.floor(ms/1000);
    var minute = Math.floor(ms/60000);
    second = second - 60 * minute;
    return minute + 'm ' + second + 's';
}
