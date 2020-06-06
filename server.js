const express = require("express");
const bodyParser = require("body-parser");
var elasticsearch = require("elasticsearch");
const converter = require("json-2-csv");
const fs = require("fs");
const path = require("path");
const {spawn} = require('child_process');

const app = express();
const port = process.env.PORT || 5000;
var client = elasticsearch.Client({
  host: "49.50.167.198:9200",
});

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use("/download", express.static("data"));

app.get("/api/data", (req, res) => {
  client
    .search({
      body: {
        query: {
          bool: {
            should: [
              { match: { type: "dashboard" } },
              { match: { type: "visualization" } },
              { match: { type: "map" } },
            ],
          },
        },
        size: 50,
      },
    })
    .then((response) => res.send(response));
});
app.get("/api/dashboard", (req, res) => {
  const qry = [];
  req.query.raw.map((d) => {
    return qry.push({ match: { _id: `visualization:${d}` } });
  });
  req.query.raw.map((d) => {
    return qry.push({ match: { _id: `map:${d}` } });
  });
  client
    .search({
      body: {
        query: {
          bool: {
            should: qry,
          },
        },
        size: 50,
      },
    })
    .then((response) => res.send(response))
    .catch((error) => {
      console.log(error);
    });
});

app.get("/api/index", (req, res) => {
  const qry = [];
  req.query.raw.map((d) => {
    return qry.push({ match: { _id: `index-pattern:${d}` } });
  });
  client
    .search({
      body: {
        query: {
          bool: {
            should: qry,
          },
        },
        size: 50,
      },
    })
    .then((response) => res.send(response))
    .catch((error) => {
      console.log(error);
    });
});

app.get("/api/log", (req, res) => {
  client
    .search({
      index: req.query.indexName,
      body: {
        query: {
          bool: {
            must: [{ match_all: {} }],
          },
        },
        size: 10000,
      },
    })
    .then((response) => {
      let regExp = /[\{\}\[\]\/?.,;:|\)*~`!^\-+<>@\#$%&\\\=\(\'\"]/gi;

      if (regExp.test(req.query.indexName)) {
        let t = req.query.indexName.replace(regExp, "");
        req.query.indexName = t;
      }
      const data = [];
      response.hits.hits.map((d) => {
        return data.push(d._source);
      });

      // console.log(data);
      converter.json2csv(data, (err, csv) => {
        if (err) {
          throw err;
        }
        console.log(data);
        fs.writeFileSync(
          `./data/${req.query.indexName}.csv`,
          "\uFEFF" + csv,
          { encoding: "utf8" },
          (err) => {
            if (err) {
              throw err;
            }
            console.log("Good");
          }
        );
        res.sendFile(
          path.join(__dirname, "/data/", `${req.query.indexName}.csv`)
        );
      });
    });
});

app.get("/api/cluster", (req, res) => {
  const process = spawn("python", ["./get_cluster.py"]);

  process.stdout.on("data", (data) => {
    console.log(data.toString());
  });
});

app.get("/api/trend", (req, res) => {
  const {spawn} = require('child_process');

  const child = spawn('python', ['./predict.py', req.query.rentalNo]);

  child.stdout.on('data', (result)=>{
    let str = result.toString();
    let lines = str.split(/\n/g);
    lines.pop(lines.length-1);
    // console.log(lines)

    let list1 = [];

    for(let i = 0; i < lines.length; i++){
      let data = lines[i].toString().replace(`b\'`, '').replace(`\'`,'');
      let buff = Buffer.from(data, 'base64');
      let text = buff.toString('utf-8');
      // console.log(text);
      list1.push(text);
    }
    // // console.log(list1);
    // for(let i = 0; i < list1.length; i++){
    //   console.log(list1[i]);
    // }
    res.send(list1)
  })

});

app.listen(port, () => console.log(`Listening on port ${port}`));
