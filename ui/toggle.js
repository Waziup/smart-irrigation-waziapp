
var deviceID = "61f7b40b784524000705af83"  // replace with your device id
var actuatorID= "61f7b980784524000705afaa" // replace with your actuator id


const toggle = document.querySelector('.toggle input')

toggle.addEventListener('click', () => {
    const onOff = toggle.parentNode.querySelector('.onoff')
    if(toggle.checked)
    {
        onOff.textContent = 'Water on';
        POST_true();
    }
    if(!toggle.checked)
    {
        onOff.textContent = 'Water off';
        POST_false();
    }
})

function POST_true() // function to set actuator value as 'true'
{
    var url = `http://wazigate.local/devices/${deviceID}/actuators/${actuatorID}/value`;
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            // console.log(xhr.status);
            // console.log(xhr.responseText);
        }
    };

    var data = 'true'; // Actuator value to be set

    xhr.send(data);
}
function POST_false() // function to set actuator value as 'false'
{
    var url = `http://wazigate.local/devices/${deviceID}/actuators/${actuatorID}/value`;
    
    var xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            // console.log(xhr.status);
            // console.log(xhr.responseText);
        }
    };

    var data = 'false'; // Actuator value to be set

    xhr.send(data);
}