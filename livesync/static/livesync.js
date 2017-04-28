var refreshing = false;
var scrolling = false;
var elementInFocus = null;

var asyncConnection = new WebSocket('ws://' + window.DJANGO_LIVESYNC.HOST + ':' + window.DJANGO_LIVESYNC.PORT)

asyncConnection.onmessage = function(evt) {
    var element;
    var evObj = JSON.parse(evt.data);

    if (!evObj.action) {
        return;
    }

    if (evObj.target) {
        element = document.getElementByLocator(evObj.target);
        if (!element) { return; }
    }

    eventHandlers[evObj.action](element, evObj.payload);
};

asyncConnection.dispatchAction = function(action, target, payload) {
    var targetLocator = target ? document.getElementLocator(target) : null

    if (asyncConnection.readyState == 1) {
        asyncConnection.send(JSON.stringify({
            action: action,
            target: targetLocator,
            payload: payload
        }));
    }
}

/**
 * Event handlers
 *
 */
window.setInterval(function() {
    // this will prevent the event to be fired from mirrored browsers.
    if (!document.hasFocus()) return;

    var newFocus = document.activeElement !== document.body &&
                   document.activeElement !== document.documentElement &&
                   document.activeElement;

    if (elementInFocus && elementInFocus !== newFocus) {
        asyncConnection.dispatchAction('blur', elementInFocus);
    }

    elementInFocus = newFocus;

}, 500);

window.onbeforeunload = function(evt) {
    if (refreshing) {
        refreshing = false;
        return;
    }

    asyncConnection.dispatchAction('refresh');
}

document.onscroll = function(evt) {
    if (scrolling) {
        scrolling = false;
        return;
    }

    asyncConnection.dispatchAction('scroll', null, { x: window.scrollX, y: window.scrollY });
}

document.onclick = function(evt) {
    if (!evt.isTrusted) { return; }
    asyncConnection.dispatchAction(evt.type, evt.getElement());
}

document.onkeyup = function(evt) {
    if (!evt.isTrusted) { return; }
    var element = evt.getElement();

    if (element.tagName == 'INPUT' || element.tagName == 'TEXTAREA') {
        asyncConnection.dispatchAction('keyup', element, { key: evt.key, value: element.value });
    }
}

document.onchange = function(evt) {
    if (!evt.isTrusted) { return; }
    var element = evt.getElement();

    if (element.tagName == 'SELECT') {
        asyncConnection.dispatchAction('change', element, { value: element.value });
    }
}

/**
 * Event triggers
 *
 */
createEventObject = function(type, name) {
    var evObj = document.createEvent(type);
    evObj.initEvent(name, true, true);
    return evObj;
}

triggerEvent = function(element, type, name) {
    var evObj = createEventObject(type, name);
    element.dispatchEvent(evObj);
}

var eventTriggers = {
    click: function(element) {
        triggerEvent(element, 'MouseEvents', 'click');
    },
    blur: function (element) {
        triggerEvent(element, 'Events', 'blur');
    },
    change: function (element) {
        triggerEvent(element, 'Events', 'change');
    },
    input: function (element) {
        triggerEvent(element, 'Events', 'input');
    }
}

/**
 * Action handlers
 *
 */
var eventHandlers = {
    scroll: function(el, payload) {
        scrolling = true;
        window.scrollTo(payload.x, payload.y);
    },
    keyup: function(el, payload) {
        el.value = payload.value
        eventTriggers.change(el);
        eventTriggers.input(el);
    },
    change: function(el, payload) {
        el.value = payload.value
        eventTriggers.change(el);
        eventTriggers.input(el);
    },
    blur: function(el, payload) {
        eventTriggers.blur(el);
    },
    refresh: function(el, payload) {
        refreshing = true;
        document.location.reload(true);
    },
    click: function(el, payload) {
        eventTriggers.click(el);
    }
}


/**
 * DOM Helpers
 *
 */
HTMLDocument.prototype.getElementIndex = function(elem) {
    return Array.prototype.indexOf.call(
        document.getElementsByTagName(elem.tagName), elem);
};

HTMLDocument.prototype.getElementLocator = function(elem) {
    return {
        tagName: elem.tagName,
        index:  document.getElementIndex(elem)
    };
};

HTMLDocument.prototype.getElementByLocator = function(locator) {
    return document.getElementsByTagName(locator.tagName)[locator.index];
};


/**
 * Event Helpers
 *
 */
 Event.prototype.getElement = function() {
     return this.target || this.srcElement;
 };
