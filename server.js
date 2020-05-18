const express = require("express");
const bodyParser = require("body-parser");
// const request = require("request");
const app = express();
const port = process.env.PORT || 5000;
var elasticsearch = require("elasticsearch");
var client = elasticsearch.Client({
  host: "localhost:9200",
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.get("/api/data", (req, res) => {
  //     request(
  //     "http://localhost:9200/classes/_search",
  //     (err, res) => {
  //       res.json(body);
  //     }
  //   );
  client
    .search({
      index: "classes",
      body: {
        query: {
          match: { title: "" },
        },
      },
    })
    .then((response) => res.send(response));
});

app.listen(port, () => console.log(`Listening on port ${port}`));
