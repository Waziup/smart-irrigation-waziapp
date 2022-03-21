
console.log("sensor id: "+sensorID);
console.log("device id: "+deviceID);

// url =  `https://api.waziup.io/api/v2/devices/${deviceID}/sensors/${sensorID}/values`;
url =  `http://waziup.wazigate-edge/devices/${deviceID}/sensors/${sensorID}/values`;
timestamps  = [];
values  = [];

async function getData() 
{
    const response = await fetch(url);
    console.log(response);
    const data = await response.json();
    console.log("data : " + data);
    length = Object.keys(data).length; // number of elements in the list
    console.log("data length : " + length);

    // push time and sensor values to lists
    for (i = 0; i < length; i++) 
    {
        timestamps.push(data[i].timestamp);
        values.push(data[i].value);
    }

    // console.log(timestamps);
    // console.log(values);

    // Define Data
    var data_plot = [
        {
            x: timestamps,
            y: values,
            mode: "line",
            type: "scatter",
            opacity: 0.8,
            line: 
            {
                color: "#3366ff",
                width: 2
            }
        }
    ];
    
        
    // Define Layout
    var layout = 
    {
        xaxis: { title: "Timestamp",  showgrid: true},
        yaxis: { range: [0, 780], title: "Raw Values",  showgrid: false},  
        title: `${sensorID} Sensor Data With Time`,

        // to highlight the insights we use shapes and create a rectangular
        shapes: [
            {   // very wet region
                layer: 'below',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 0,
                y1: 195,
                type: 'rect',
                fillcolor: 'lightblue',
                opacity: 0.4,
                line: 
                {
                    width: 0
                }
            },

            {   // wet region  
                layer: 'below',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 196,
                y1: 390,
                type: 'rect',
                fillcolor: 'green',
                opacity: 0.4,
                line: 
                {
                    width: 0
                }
            },

            {   // dry region
                layer: 'below',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 391,
                y1: 585,
                type: 'rect',
                fillcolor: 'orange',
                opacity: 0.4,
                line: 
                {
                    width: 0
                }
            },

            {   // very dry region
                layer: 'below',
                xref: 'paper',
                yref: 'y',
                x0: 0,
                x1: 1,
                y0: 586,
                y1: 780,
                type: 'rect',
                fillcolor: 'red',
                opacity: 0.4,
                line: 
                {
                    width: 0
                }
            }
        ]
    };

    // Display using Plotly
    Plotly.newPlot("values_chart", data_plot, layout, {displaylogo: false}, {scrollZoom: true});         
    
}
getData();

/*
function foo() {

    getData();


    setTimeout(foo, 5000);
}

foo(); */