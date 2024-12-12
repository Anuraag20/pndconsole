const createChart = exchange => {
	const ctx = document.getElementById(exchange);
	const cfg = {
		type: 'line',
		data: { 

			datasets: [
				{
					label: exchange.toUpperCase(),
					name: exchange,
					data: [{x: null, y: null}],
					pointBackgroundColor: ["#3366CC80"]
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

	data.forEach((pointData) => {
		let name = pointData[6]	
		let chart = charts[name]
			
		point = {	
			x: new Date(pointData[5]),
			y: pointData[3]
		}

		for (const dataset of chart.data.datasets){

			if (dataset.name != name)
				continue;

			var high = document.getElementById(`${name}-high`)
			var low = document.getElementById(`${name}-low`)
			var largestChange = document.getElementById(`${name}-lc`)
			var firstAnomaly = document.getElementById((`${name}-fa`))
			var counts = document.getElementById((`${name}-c`))

			if (pointData.at(-1)){
				var color =  "#DC3912"
				if(firstAnomaly.textContent.trim() == 'N/A') firstAnomaly.textContent = point.x	
			}
			else {
				var color = "#3366CC90"
			}

			if (dataset.data.at(-1).x && dataset.data.at(-1).x.valueOf() == point.x.valueOf()){
				dataset.data.splice(dataset.data.length - 1, 1, point) 
 				dataset.pointBackgroundColor.splice(dataset.pointBackgroundColor.length - 1, 1, color) 
			}
			else {
				dataset.data.push(point);
				dataset.pointBackgroundColor.push(color);
				if (pointData.at(-1)) counts.textContent = parseInt(counts.textContent) + 1
			}
				


			if ( parseFloat(high.textContent) < point.y ){
				high.textContent = point.y
			}
			else if ( parseFloat(low.textContent) == 0 || parseFloat(low.textContent) > point.y ){
				low.textContent = point.y
			}

			largestChange.textContent = Math.round((high.textContent - low.textContent) * 10000/low.textContent)/100

			
			break;
		}
		chart.update();
		

	})
}

const fetchInitialData = (sock) => sock.send(JSON.stringify({'type': 'initialize'}))


const createStaticCharts = () => {
	var dataDiv = document.getElementById('p-data')	
	for (const child of dataDiv.children){
		updateChart({data: child.textContent})
	}
}
