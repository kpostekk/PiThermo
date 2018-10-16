$(document).ready(function () {
    collectTemp();
    collectState();
    window.setInterval(collectTemp, 6000);
    window.setInterval(collectState, 20000);
});

function collectTemp() {
    return $.ajax('/temperature/', {
        success: function (payload) {
            $('#temp').text(payload + "°C")
        }
    })
}

function collectState() {
    return $.ajax('/r/get-mode/', {
        success: function (payload) {
            if (payload === 'False') {
                $('#state').removeClass('badge-danger').addClass('badge-info')
            } else {
                $('#state').addClass('badge-danger').removeClass('badge-info')
            }

            if (payload === 'True') {
                payload = 'Włączony'
            } else if (payload === 'False') {
                payload = 'Wyłączony'
            }

            $('#state').text(payload);
        }
    })
}
