function onDOMReady(callback) {
    if (document.readyState !== 'loading') {
        callback();
    } else if (document.addEventListener) {
        document.addEventListener('DOMContentLoaded', callback);
    } else { // IE <= 8
        document.attachEvent('onreadystatechange', function() {
            if (document.readyState === 'complete') {
                callback();
            }
        });
    }
}

onDOMReady(function() {
    console.log("Document is ready")
    document.querySelectorAll('.login-options-btn').forEach(item => {
      item.addEventListener('click', event => {
        document.getElementById("user-level").value = item.dataset.logintype;
        document.getElementById("next").setAttribute('value',item.dataset.next);
        document.getElementById("login-title").innerHTML = item.innerText;
        const cardHeader = document.querySelector(".card-header")
//        cardHeader.setAttribute('class', "card-header " + item.dataset.bg)
      })
    })
});