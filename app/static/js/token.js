let nxmPrice = undefined
let nxmMarketCap = undefined

const renderNXMPrice = (currency) => {
  if (nxmPrice !== undefined) {
    Plotly.newPlot('nxmPrice', [{
      x: getDateTimesInLocalTimezone(Object.keys(nxmPrice[currency])),
      y: Object.values(nxmPrice[currency]),
      fill: 'tozeroy',
      type: 'scatter'
    }], {
      yaxis: {range: [Math.min(...Object.values(nxmPrice[currency])),
          Math.max(...Object.values(nxmPrice[currency]))]}
    })
  }
}

$.get('nxm_price', (response) => {
  nxmPrice = response
  $('#nxm-price-usd').click()
})

$('#nxm-price-usd').click(() => {
  renderNXMPrice('USD')
  toggleCurrency('#nxm-price', 'usd', 'eth')
})

$('#nxm-price-eth').click(() => {
  renderNXMPrice('ETH')
  toggleCurrency('#nxm-price', 'eth', 'usd')
})

$.get('nxm_return_vs_eth', (response) => {
  Plotly.newPlot('nxmReturnVsEth', [{
    x: getDateTimesInLocalTimezone(Object.keys(response)),
    y: Object.values(response),
    fill: 'tozeroy',
    type: 'scatter'
  }])
})

$.get('nxm_supply', (response) => {
  Plotly.newPlot('nxmSupply', [{
    x: getDateTimesInLocalTimezone(Object.keys(response)),
    y: Object.values(response),
    fill: 'tozeroy',
    type: 'scatter'
  }], {
    yaxis: {range: [Math.min(...Object.values(response)), Math.max(...Object.values(response))]}
  })
})

const renderNXMMarketCap = (currency) => {
  if (nxmMarketCap !== undefined) {
    Plotly.newPlot('nxmMarketCap', [{
      x: getDateTimesInLocalTimezone(Object.keys(nxmMarketCap[currency])),
      y: Object.values(nxmMarketCap[currency]),
      fill: 'tozeroy',
      type: 'scatter'
    }], {
      yaxis: {range: [Math.min(...Object.values(nxmMarketCap[currency])),
          Math.max(...Object.values(nxmMarketCap[currency]))]}
    })
  }
}

$.get('nxm_market_cap', (response) => {
  nxmMarketCap = response
  $('#nxm-market-cap-usd').click()
})

$('#nxm-market-cap-usd').click(() => {
  renderNXMMarketCap('USD')
  toggleCurrency('#nxm-market-cap', 'usd', 'eth')
})

$('#nxm-market-cap-eth').click(() => {
  renderNXMMarketCap('ETH')
  toggleCurrency('#nxm-market-cap', 'eth', 'usd')
})

$.get('nxm_distribution', (response) => {
  Plotly.newPlot('nxmDistribution', [{
    labels: Object.keys(response),
    values: Object.values(response),
    type: 'pie',
    textinfo: 'none'
  }])
})

$.get('unique_addresses', (response) => {
  Plotly.newPlot('uniqueAddresses', [{
    x: getDateTimesInLocalTimezone(Object.keys(response)),
    y: Object.values(response),
    fill: 'tozeroy',
    type: 'scatter'
  }])
})
