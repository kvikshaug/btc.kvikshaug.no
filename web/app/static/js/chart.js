$(function() {
  google.setOnLoadCallback(function() {
    var data = google.visualization.arrayToDataTable(window.Kvikshaug.price_history);

    var options = {
      title: window.Kvikshaug.price_history_title,
      legend: { position: 'bottom' }
    };

    var chart = new google.visualization.LineChart($('.chart').get(0));

    chart.draw(data, options);
  });
});
