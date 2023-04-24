baseURL = "https://raw.githubusercontent.com/Flyyrin/GIP-2022-2023/main"

var code = {
    "code-block-1": "main/json/config.json",
    "code-block-2": "main/json/layout.json",
    "code-block-3": "main/algorithm.py",
    "code-block-4": "main/checker.py",
    "code-block-5": "main/controller.py",
    "code-block-6": "main/start.py",
    "code-block-7": "main/webInterface.py"
}

$(document).ready(function() {
    function highlight() {
        hljs.highlightAll()
    }
    $.each(code, function(name, path) {
        $.get(`${baseURL}/${path}`, function(data) {
            $(`.${name}`).text(data);
        });
    });
    setTimeout(highlight, 1000)
});