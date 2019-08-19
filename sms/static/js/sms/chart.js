const endpoint = `//${window.location.hostname}:8000/app/api/chart/`
var data_to_send = []
var labels = []
var cs = []
$.ajax({
  method: "GET",
  url: endpoint,
  success: (data) => {
    labels = data.labels
    data_to_send = data.data_to_send
    console.log(data_to_send)
    cs = data.current_session
    setAverageGraph()
  },

  error: (error_data) => {
    console.log(`error_data: ${error_data}`);
  },
});


const setAverageGraph = () =>{
  const ctx = document.querySelector("#income_and_expense_graph").getContext('2d');
  const myChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: cs + ' Account Summary (Naira)',
        data: data_to_send,
        backgroundColor: [
          'rgba(255, 99, 132, 0.2)',
          'rgba(54, 162, 235, 0.2)',
          'rgba(255, 206, 86, 0.2)',
          'rgba(75, 192, 192, 0.2)',
          'rgba(153, 102, 255, 0.2)',
          'rgba(255, 159, 64, 0.2)'
          ],

          borderColor: [
            'rgba(255,99,132,1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 206, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)'
            ],
            borderWidth: 1.5
          }]
        },

        options: {
          scales: {
            yAxes: [{
              ticks: {
                beginAtZero:true
              }
            }]
          }
        }
      });}