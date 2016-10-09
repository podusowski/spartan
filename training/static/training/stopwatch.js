var time_difference_between_server = 0;

function time_on_server(on_server)
{
    var now = new Date();
    time_difference_between_server = now - on_server;
}

function stopwatch(html_element_id, start_time)
{
    var now = new Date();
    var diff = now.getTime() - start_time.getTime() - time_difference_between_server;

    document.getElementById(html_element_id).innerHTML = format_timespan(diff);
    setTimeout(function() { stopwatch(html_element_id, start_time); }, 500);
}

function format_number(number)
{
    if (number > 9)
    {
        return '' + number
    }
    else
    {
        return '0' + number
    }
}

function format_timespan(ms)
{
    if (ms < 0)
    {
        return "--";
    }

    var day = Math.floor(ms / (24 * 60 * 60 * 1000));
    ms = ms % (24 * 60 * 60 * 1000);

    var hour = Math.floor(ms / (60 * 60 * 1000));
    ms = ms % (60 * 60 * 1000);

    var minute = Math.floor(ms / (60 * 1000));
    ms = ms % (60 * 1000);

    var second = Math.floor(ms / 1000);

    var mins_and_secs = format_number(minute) + 'm:' + format_number(second) + 's';

    if (day > 0)
    {
        return day + 'd:' + hour + 'h:' + mins_and_secs;
    }
    else if (hour > 0)
    {
        return hour + 'h:' + mins_and_secs;
    }
    else
    {
        return mins_and_secs;
    }
}
