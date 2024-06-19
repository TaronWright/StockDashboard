async function candlestickPlot(period="1y"){

    let stockSymbol = document.getElementById("symbol").value

    let postData = {
        "Symbol": stockSymbol, 
        "Period": period
    }

    let response = await fetch("/stock", {
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": JSON.stringify(postData),
    })

    let stock_json = await response.json()


    var candlestickTrace = {
  
        x : stock_json['Date'], 

        close: stock_json['Close'], 
        
        decreasing: {line: {color: '#880808'}}, 
        
        high: stock_json['High'], 
        
        increasing: {line: {color: '#228B22'}}, 
        
        line: {color: 'rgba(31,119,180,1)'}, 
        
        low: stock_json['Low'], 
        
        open: stock_json['Open'], 
    
        name: "Candlestick",    
        type: 'candlestick', 
      };

      const candlestickLayout = {
        title: {
            text:'Candle Stick Chart',
        },
        xaxis: {
            rangeslider: {
                 visible: false
             }
          },
        paper_bgcolor: "#1B232F",
        plot_bgcolor: "#1B232F",
        font: {
            color: "#FFFFFF"
        },
        yaxis: {
            title: {
              text: 'Price (USD)',
              font: {
                family: 'Courier New, monospace',
                size: 18,
              }
            }
          }
        };

      
    const candlestickData = [candlestickTrace];
    // Plot the candlestick chart
    let candlestickElement = document.getElementById("candlestickChart")  
    Plotly.newPlot(candlestickElement, candlestickData, candlestickLayout, {responsive:true});

    var macdTrace = {
        x : stock_json['Date'],
        y: stock_json['MACD'],
        name: "MACD",
        type: 'scatter', 
      }

      var signalTrace = {
        x: stock_json['Date'],
        y: stock_json['Signal'],
        name: "Signal",
        type: 'scatter', 
      }

      // Calculate the MACD Histogram
      var macdBarTrace = {
        x: stock_json['Date'],
        y: stock_json['MACD-Hisogram'],
        name: "bar",
        type: "bar",
        marker: {}
      }

      // Loop through y values and format colour depending on value
      macdBarTrace.marker.color = macdBarTrace.y.map(function(value){
         return value <= 0 ? "red" : "green"
      }
      )

    const macdLayout = {
        title:{
            text: "MACD Chart"
        },
        xaxis: {
            rangeslider: {
                 visible: false
             }
          },
        paper_bgcolor: "#1B232F",
        plot_bgcolor: "#1B232F",
        font: {
            color: "#FFFFFF"
        },
        yaxis: {
            title: {
              text: 'Indicator',
              font: {
                family: 'Courier New, monospace',
                size: 18,
              }
            }
          }
        };

    const macdData = [macdTrace, signalTrace, macdBarTrace]
    let macdElement = document.getElementById("macd")
    // Plot the MACD Chart
    Plotly.newPlot(macdElement, macdData, macdLayout, {responsive:true});

    let indicatorElement = document.querySelector("#close-indicator")


    var indicatorData = [
        {
          type: "indicator",
          mode: "number+delta",
          value: stock_json['Open'].slice(-1)[0].toFixed(2),
          title: {
            text:
              "Stock Ticker",
            font: {
                color: "#FFFFFF"
            }
          },
          domain: { x: [0, 1], y: [0, 1] },
          delta: { reference: stock_json['Open'][0].toFixed(2), relative: true, position: "top", valueformat:'.2%'}
        }
      ];
      
      var indicatorLayout = {
        margin: { t: 25, r: 25, l: 25, b: 25 },
        paper_bgcolor: "#1B232F",
        font: {
            color: "#FFFFFF"
        }
      };
      
      Plotly.newPlot(indicatorElement, indicatorData, indicatorLayout);


    //   response = await fetch("/info", {
    //     method: "POST",
    //     headers: {
    //         "content-type": "application/json"
    //     },
    //     "body": JSON.stringify(postData)
    //   })

    //   let info_json = await response.json()

    //   console.log(info_json)

      stockInfo()
      stockFinancials()
      stockNews()
}





let stockInfo = async () => {
    let stockSymbol = document.getElementById("symbol").value
    let postData = {"Symbol": stockSymbol}

    let response = await fetch("/info", 
        {
            "method": "POST",
            "headers": {"content-type": "application/json"},
            "body": JSON.stringify(postData)
            
        }
    )
    let json = await response.json()
    console.log(json)

    // Set the contents of all the about headings
    // document.getElementById("info-summary").innerText = 'Summary: ' + json['longBusinessSummary']
    document.getElementById("info-industry").innerText = 'Industry: ' + json['industry']
    document.getElementById("info-sector").innerText = 'Sector: ' + json['sector']
    document.getElementById("info-address").innerText = 'Address: ' + json['address1']
    document.getElementById("info-state").innerText = 'State: ' + json['state']
    document.getElementById("info-country").innerText = 'Country: ' + json['country']
    document.getElementById("info-website").innerText = 'Website: ' + json['website']

}



let stockFinancials = async () => {
  let stockSymbol = document.getElementById("symbol").value
  let postData = {"Symbol": stockSymbol}

  let response = await fetch("/financials",
    {
      "method": "POST",
      "headers": {
        "content-type": "application/json"
        },
        "body": JSON.stringify(postData)
      }
    )

    let json = await response.json()
    console.log(json)
}


let stockNews = async () => {
  let stockSymbol = document.getElementById("symbol").value
  let postData = {"Symbol": stockSymbol}

  let response = await fetch("/news",
    {
      "method": "POST",
      "headers": {
        "content-type": "application/json"
        },
        "body": JSON.stringify(postData)
      }
    )

    let json = await response.json()
    console.log(json)
}


// Function that converts an array of string dates into Date objects
dateConvert = (dates) => {
  // .map(function(){}) or /.map(()=>) applies to every element in the array
  const dateObjects = dates.map(date => new Date(date))
  return dateObjects
}


candlestickPlot()



