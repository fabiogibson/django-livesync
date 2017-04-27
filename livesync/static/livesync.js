var refreshing = false;
var scrolling = false;
var ws = new WebSocket('ws://' + window.DJANGO_LIVESYNC.HOST + ':' + window.DJANGO_LIVESYNC.PORT)

var sendEvent = function(action, target, payload) {
    if (ws.readyState == 1) {
        ws.send(JSON.stringify({
            action: action,
            target: target,
            payload: payload
        }));
    }
}

var getSource = function(evt, attr) {
    return (evt.target || evt.srcElement)[attr];
}

var getSourceId = function(evt) {
    return getSource(evt, 'id');
}

var getSourceValue = function(evt) {
    return getSource(evt, 'value');
}

window.onbeforeunload = function(evt) {
    if (refreshing) {
        refreshing = false;
        return;
    }

    sendEvent('refresh','window');
}

document.onscroll = function(evt) {
    if (scrolling) {
        scrolling = false;
        return;
    }

    sendEvent('scroll', 'window', {
        x: window.scrollX,
        y: window.scrollY,
    });
}

document.onkeyup = function(evt) {
    if (!evt.ctrlKey && evt.keyCode == 17) {
        return;
    }

    if (evt.ctrlKey && (evt.keyCode == 65 || evt.keyCode == 67)) {
        return;
    }

    sendEvent('keyup', getSourceId(evt), { value: getSourceValue(evt) });
}

ws.onmessage = function(evt) {
    obj = JSON.parse(evt.data);
    var input = document.getElementById(obj.target);
    if (!input && obj.target != 'window') return;

    switch(obj.action) {
        case "scroll":
            scrolling = true;
            window.scrollTo(obj.payload.x, obj.payload.y);
            break;
        case "keyup":
            input.value = obj.payload.value
            break;
        case "refresh":
            refreshing = true;
            document.location.reload(true);
            break;
    }
};
