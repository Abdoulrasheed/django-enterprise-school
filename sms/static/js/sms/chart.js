const endpoint = `//${window.location.hostname}:8000/app/api/chart/`
var data_to_send = []
var labels = []
var cs = []
$.ajax({
  method: "GET",
  url: endpoint,
  success: (data) => {
    expense = data.expenditure
    income = data.income
    cs = data.current_session
    setAverageGraph()
    getTargetPercentage(income)
  },

  error: (error_data) => {
    console.log(`error_data: ${error_data}`);
  },
});

const setAverageGraph = () =>{
//line
  const ctx = document.querySelector("#income_and_expense_graph").getContext('2d');
var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [ "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December" ],
    datasets: [{
        label: "Income",
        data: income,
        backgroundColor: [
          'rgba(105, 0, 132, .2)',
        ],
        borderColor: [
          'rgba(200, 99, 132, .7)',
        ],
        borderWidth: 2
      },
      {
        label: "Expenditure",
        data: expense,
        backgroundColor: [
          'rgba(0, 137, 132, .2)',
        ],
        borderColor: [
          'rgba(0, 10, 130, .7)',
        ],
        borderWidth: 2
      }
    ]
  },
  options: {
    responsive: true,
  }
});}

const getTargetPercentage = (income) => {
  // target income percentage
  var target_income = $.trim($('.target-income').text());
  target_income = parseFloat(target_income.replace(',', '')); // remove comma
  const reducer = (accumulator, currentValue) => accumulator + currentValue;
  const total_income = income.reduce(reducer);
  const perc = ((total_income/target_income) * 100).toFixed(1); // toFixed three decimal places
  $(".target-progress").text(
    `${perc}%`
  );
  $(".target-progress").css(
    "width", perc
  );
}