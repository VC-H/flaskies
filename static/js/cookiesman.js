var cookiesMan = {

    get: function() {
        var cookieItems = document.cookie.split(';');
        if (cookieItems[0] == "") return {}
        var cookies = {}
        for (var i = 0; i < cookieItems.length; i++) {
            console.log('cookies[' + i + '] = ' + cookieItems[i]);
            var items = cookieItems[i].split('=');
            cookies[items[0].trim()] = items[1].trim(); }
        return cookies;
    },

    exec: function() {
        var cookies = cookiesMan.get();
        for (var tr of document.getElementsByClassName('cookie')) {
            var label = tr.getElementsByTagName('label')[0].textContent;
            if (!(label in cookies)) {
                checkbox = tr.querySelector('[type=checkbox]');
                checkbox.checked = true; }
        }
    },

}
