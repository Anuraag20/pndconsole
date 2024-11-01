const createChart = exchange => {
	const ctx = document.getElementById(exchange);
	const cfg = {
		type: 'line',
		data: {
			datasets: [
				{
					label: exchange.toUpperCase(),
					name: exchange,
					data: [{x: new Date(), y: null}]
				},
			]
		},
		options: {
			scales: {
				x: {
					type: 'time',
				}
			}
		}
	}
	let chart = new Chart(ctx, cfg)	
	return chart
}


const updateChart = (message) => {
	var data = JSON.parse(message.data)

	data.forEach((point) => {
		let name = point[6]	
		let chart = charts[name]

		point = {	
			x: new Date(point[5]),
			y: point[3]
		}

		for (const dataset of chart.data.datasets){

			if (dataset.name != name)
				continue;

			dataset.data.at(-1).x.valueOf() == point.x.valueOf() 
				? dataset.data.splice(dataset.data.length - 1, 1, point) 
				: dataset.data.push(point)

			// Getting out of the loop when the correct exchange has been found
			break
		}
		chart.update();

	})
}

const fetchInitialData = (sock) => sock.send(JSON.stringify({'type': 'initialize'}))


