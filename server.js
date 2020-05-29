const express = require("express");
const bodyParser = require("body-parser");
var elasticsearch = require("elasticsearch");

const app = express();
const port = process.env.PORT || 5000;
var client = elasticsearch.Client({
  host: "localhost:9200",
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.get("/api/data", (req, res) => {
  client
    .search({
      body: {
        query: {
          bool: {
            should: [
              { match: { type: "dashboard" } },
              { match: { type: "visualization" } },
            ],
          },
        },
        size: 50,
      },
    })
    .then((response) => res.send(response));
});

app.listen(port, () => console.log(`Listening on port ${port}`));
