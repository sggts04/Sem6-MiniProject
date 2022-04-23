const express = require("express");
const app = express();
const citizenData = require("./data");

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get("/", (req, res) => {
  res.send("Wassup");
});

app.post("/verify", (req, res) => {
  console.log(req.body);
  const { aadhar } = req.body;
  for (let citizen of citizenData) {
    if (citizen.aadhar === aadhar && citizen.age >= 18) {
      console.log(citizen);
      res.json(citizen);
    }
  }

  res.status(404).end();
});

app.listen(3002, () => {
  console.log("Running on port 3002");
});
