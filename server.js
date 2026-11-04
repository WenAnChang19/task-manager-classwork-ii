"use strict";

const { createApp } = require("./app");
const PORT = 2234;
const app = createApp();

const server = app.listen(PORT, "127.0.0.1");
server.on("listening", () => {
  console.log(`My Task Manager: http://localhost:${PORT}`);
});
server.on("error", (error) => {
  console.error(error.code === "EADDRINUSE"
    ? `Port ${PORT} 已被使用，請先關閉占用它的程式。`
    : error.message);
  process.exitCode = 1;
});
