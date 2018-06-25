// cf. https://bl.ocks.org/mbostock/3884955
//     https://bl.ocks.org/mbostock/0533f44f2cfabecc5e3a



var svg = d3.select("svg");
MARGIN = ({top: 20, right: 20, bottom: 30, left: 40});
WIDTH = svg.attr("width") - MARGIN.left - MARGIN.right;
HEIGHT = svg.attr("height") - MARGIN.top - MARGIN.bottom;

g = svg.append("g")
    .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")")


//var x = d3.scaleTime().range([0, WIDTH - MARGIN.left - MARGIN.right]);
var x = d3.scaleLinear().range([0, WIDTH - MARGIN.left - MARGIN.right]);
var y = d3.scaleLinear().range([HEIGHT - MARGIN.top - MARGIN.bottom, 0]);
//var z = d3.scaleOrdinal(d3.schemeCategory10);

var line = d3.line()
//    .curve(d3.curveBasis)
    .x(function(d) { return x(d.time); })
    .y(function(d) { return y(d.gb); });

data = '[{"bytes":675769528,"end":6.000079870223999,"start":0},{"bytes":677642240,"end":12.002346992492676,"start":6.000079870223999},{"bytes":665845760,"end":18.000200033187866,"start":12.002346992492676},{"bytes":693370880,"end":24.000130891799927,"start":18.000200033187866},{"bytes":627834880,"end":30.000110864639282,"start":24.000130891799927}]';
measurements = JSON.parse(data);

series = measurements.map(x => ({
    time: x.end,
    gb: (x.bytes * 8.0)/(1024.0 * 1024.0 * (x.end - x.start))
}));

console.log(series);

x.domain(d3.extent(series, d => d.time));

y.domain([
    d3.min(series, d => d.gb),
    d3.max(series, d => d.gb)
]);

//z.domain(cities.map(function(c) { return c.id; }));


g.append("g")
    .attr("class", "axis axis--x")
    .attr("transform", "translate(0," + HEIGHT + ")")
    .call(d3.axisBottom(x));

//g.append("g")
//  .attr("class", "axis axis--x")
//  .attr("transform", "translate(0," + HEIGHT + ")")
//  .call(d3.axisBottom(x));
//  .append("text")
//  .attr("x", 10)
//  .attr("dx", "0.71em")
//  .attr("fill", "#000")
//    .text("seconds");

g.append("g")
//g
//g.enter()
  .attr("class", "axis axis--y")
  .call(d3.axisLeft(y))
.append("text")
  .attr("transform", "rotate(-90)")
  .attr("y", 6)
  .attr("dy", "0.71em")
  .attr("fill", "#000")
  .text("Gb");

//var zzz = g.selectAll(".zzz")
//    .data(series)
//    .enter().append("g")
//        .attr("class", "zzz");
//
//zzz.append("path")
//    .attr("class", "line")
//    .attr("d", function(d) { return line(series); });
////    .attr("d", function(d) { return line(d) });

g.append("path")
    .datum(series)
    .attr("class", "line")
//    .attr("d", line(series));
    .attr("d", line);

