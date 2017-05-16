var spartan = spartan || {};
spartan.stopwatch = spartan.stopwatch || {};

spartan.stopwatch.timeDifferenceBetweenServer = 0;
spartan.stopwatch.eachSecondHandlers = [];
spartan.stopwatch.lastSecondTime = new Date().valueOf();

/**
 * Using built-in setTimeout function is susceptible to time drifts, using
 * precise timers will reduce this effect giving a beat on each second.
 */
spartan.stopwatch.initializePreciseTimer = function() {
    function evaluateTimers() {
        var now = new Date().valueOf();
        var drift = now - spartan.stopwatch.lastSecondTime;

        spartan.stopwatch.eachSecondHandlers.forEach(function(e) {
            e();
        });

        spartan.stopwatch.lastSecondTime += 1000;
        setTimeout(evaluateTimers, 1000 - drift);
    }

    evaluateTimers();
}

spartan.stopwatch.eachSecond = function(handler) {
    spartan.stopwatch.eachSecondHandlers.push(handler);
}

spartan.stopwatch.saveTimeOnServer = function(time) {
    var now = new Date();
    spartan.stopwatch.timeDifferenceBetweenServer = now - time;
}

spartan.stopwatch.beep = function(element, seconds) {
    var beepSound = element.attr('data-beep-sound');
    var beepInterval = element.attr('data-beep-every');

    if (beepInterval != undefined && seconds % beepInterval == 0) {
        audio = new Audio(beepSound);
        audio.play();
    }
}

spartan.stopwatch.stopwatch = function(element, startTime) {
    if (typeof(startTime) === 'undefined') {
        startTime = new Date(element.attr('data-stopwatch-from'));
    }

    spartan.stopwatch.eachSecond(function() {
        var now = new Date();
        var diff = now.getTime() - startTime.getTime() - spartan.stopwatch.timeDifferenceBetweenServer;
        var seconds = Math.round(diff / 1000);

        spartan.stopwatch.beep(element, seconds);
        element.text(spartan.utils.formatTime(diff));
    });
}

spartan.stopwatch.startAllStopwatchesWithAttribute = function() {
    $("[data-stopwatch-from]").each(function() {
        spartan.stopwatch.stopwatch($(this));
    });
}

$(document).ready(function() {
    spartan.stopwatch.initializePreciseTimer();
    spartan.stopwatch.startAllStopwatchesWithAttribute();
});
