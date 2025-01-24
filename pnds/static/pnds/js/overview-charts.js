const createPieChart = () => {
	
	var pData = JSON.parse(document.getElementById('by-channel').textContent)
	//console.log(data)
	const ctx = document.getElementById('by-channel-pie');
	const cfg = {
		type: 'doughnut',
		responsive: true,
		data: {
			labels: pData.map(entry => entry.channel),
			datasets: [{
				label: 'Organized pumps',
				data: pData.map(entry => entry.c),
				hoverOffset: 4,
				borderWidth: 0
			}]
		}

	}
	new Chart(ctx, cfg)	
	

}

const createBarChart = () => {
	
	const dow = [
		'Monday',
		'Tuesday',
		'Wednesday',
		'Thursday',
		'Friday',
		'Saturday',
		'Sunday'
	]
	var bData = JSON.parse(document.getElementById('by-weeks').textContent)

	const ctx = document.getElementById('by-weeks-bar');
	const labels = bData.map(entry => dow[entry.weekday]);
	
	const data = {
		labels: labels,
		datasets: [{
			label: 'Most Popular Weekdays for Pumps',
			data: bData.map(entry => entry.c),
			backgroundColor: '#f3933d' 
		}]
	};
	const cfg = {
		type: 'bar',
		data: data,
		options: {
			scales: {
				y: {
					beginAtZero: true
				}
			},
			indexAxis: 'y'
		},
	};

	new Chart(ctx, cfg)
}
new DataTable('#overview-table');
createPieChart()
createBarChart()

