const express = require("express");
const app = express();

app.use(express.json());

// Hardcoded secret
const API_KEY = "sk-live-abc123def456";

app.get("/api/users/:id", (req, res) => {
  const query = `SELECT * FROM users WHERE id = ${req.params.id}`;
  db.query(query, (err, result) => {
    res.json(result);
  });
});

app.post("/api/exec", (req, res) => {
  const { cmd } = req.body;
  require("child_process").exec(cmd, (err, stdout) => {
    res.send(stdout);
  });
});

app.listen(3000, "0.0.0.0", () => {
  console.log("Server running on port 3000");
});
