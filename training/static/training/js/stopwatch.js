var spartan = spartan || {};
spartan.stopwatch = spartan.stopwatch || {};

spartan.stopwatch.time_difference_between_server = 0;

spartan.stopwatch.saveTimeOnServer = function(on_server)
{
    var now = new Date();
    spartan.stopwatch.time_difference_between_server = now - on_server;
}

spartan.stopwatch.beep = function(element, seconds)
{
    var beepSound = element.attr('data-beep-sound');
    var beepInterval = element.attr('data-beep-every');

    if (beepInterval != undefined && seconds % beepInterval == 0)
    {
        $(beepSound)[0].play();
    }
}

spartan.stopwatch.stopwatch = function this_function(html_element_id, start_time)
{
    element = $(html_element_id);

    var now = new Date();
    var diff = now.getTime() - start_time.getTime() - spartan.stopwatch.time_difference_between_server;
    var seconds = Math.round(diff / 1000);
    spartan.stopwatch.beep(element, seconds);

    element.text(formatTime(diff));
    setTimeout(function() { this_function(html_element_id, start_time); }, 500);
}

spartan.stopwatch.stopwatch2 = function this_function(element)
{
    var start_time = new Date(element.attr('data-stopwatch-from'));
    var now = new Date();
    var diff = now.getTime() - start_time.getTime() - spartan.stopwatch.time_difference_between_server;
    var seconds = Math.round(diff / 1000);
    spartan.stopwatch.beep(element, seconds);

    element.text(formatTime(diff));
    setTimeout(function() { this_function(element); }, 500);
}

function formatTime(ms)
{
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

spartan.stopwatch.startAllStopwatchesWithAttribute = function()
{
    $("[data-stopwatch-from]").each(function()
    {
        spartan.stopwatch.stopwatch2($(this));
    });
}

$(document).ready(function() {
    spartan.stopwatch.startAllStopwatchesWithAttribute();
});
