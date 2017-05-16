var spartan = spartan || {};
spartan.utils = spartan.utils || {};

spartan.utils.formatTime = function(ms) {
    if (ms < 0) {
        return "--";
    }

    var day = Math.floor(ms / (24 * 60 * 60 * 1000));
    ms = ms % (24 * 60 * 60 * 1000);

    var hour = Math.floor(ms / (60 * 60 * 1000));
    ms = ms % (60 * 60 * 1000);

    var minute = Math.floor(ms / (60 * 1000));
    ms = ms % (60 * 1000);

    var second = Math.floor(ms / 1000);

    function formatNumber(number) {
        if (number > 9) {
            return '' + number
        } else {
            return '0' + number
        }
    }

    var minsAndSecs = formatNumber(minute) + 'm:' + formatNumber(second) + 's';

    if (day > 0) {
        return day + 'd:' + hour + 'h:' + minsAndSecs;
    } else if (hour > 0) {
        return hour + 'h:' + minsAndSecs;
    } else {
        return minsAndSecs;
    }
}
