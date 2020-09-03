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
        cardHeader.setAttribute('class', "card-header " + item.dataset.bg)
      })
    })

    function doToggleBtn(){
    }

    function toggleDetail() {
        console.log("Toggled")
        const detailToggleBtn = document.getElementById('detail-toggle');

        const visibles = document.querySelectorAll(".show-more")
        const invisibles = document.querySelectorAll(".hide-more")

        if (detailToggleBtn.innerText == "Show All Details") {
            detailToggleBtn.innerHTML = "Show Basic Details";

//            visibles.forEach(el => {
//                el.classList.add('hide-detail');
//            })

            invisibles.forEach(el => {
                el.classList.remove('hide-more');
                el.classList.add('show-more');
            })
        } else {
            detailToggleBtn.innerText = "Show All Details";

//            invisibles.forEach(el => {
//                el.classList.add('hide-detail');
//            })

            visibles.forEach(el => {
                el.classList.remove('show-more');
                el.classList.add('hide-more');
            })
        }
    }

    document.getElementById('detail-toggle').addEventListener('click', toggleDetail)


});