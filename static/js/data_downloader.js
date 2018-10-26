$(document).ready(function () {
    collectVars();
    window.setInterval(collectVars, 6000);
});

function collectVars() {
    return $.getJSON('/json', function (payload) {
        console.log(payload);
        reloadTargets(payload)
    })
}

function reloadTargets(payload_json) {
    $('#temp').text((payload_json['Temperature'] + '°C').toString().replace('.', ','));
    if (payload_json['Relay switch mode'] === false) {
        $('#state').removeClass('badge-danger').addClass('badge-info')
    } else {
        $('#state').addClass('badge-danger').removeClass('badge-info')
    }

    if (payload_json['Relay switch mode'] === true) {
        msg = 'Włączony'
    } else if (payload_json['Relay switch mode'] === false) {
        msg = 'Wyłączony'
    } else {
        msg = 'Err'
    }

    $('#state').text(msg)
}