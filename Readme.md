1. Start kafka (app\kafka\docker-compose.yaml)
2. Run app
3. Subscribe to map:
```javascript
(async () => {
  await new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = "https://cdn.socket.io/4.7.5/socket.io.min.js";
    s.onload = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });

  const socket = io("http://localhost:5000", {
    path: "/socket.io",
    transports: ["websocket", "polling"],
  });

  socket.on("connect", () => console.log("connect", socket.id));
  socket.on("connect_error", (e) => console.log("connect_error", e));
  socket.on("disconnect", (r) => console.log("disconnect", r));

  socket.emit("join_map");
  socket.on("joined", (payload) => console.log("joined:", payload));
  socket.on("new_message", (payload) => console.log("new_message:", payload));

  window.__socket = socket;
})();
```
4. Subscribe to chat:
```javascript
(async () => {
  await new Promise((resolve, reject) => {
    const s = document.createElement("script");
    s.src = "https://cdn.socket.io/4.7.5/socket.io.min.js";
    s.onload = resolve;
    s.onerror = reject;
    document.head.appendChild(s);
  });

  const socket = io("http://localhost:5000", {
    path: "/socket.io",
    transports: ["websocket", "polling"],
  });

  socket.on("connect", () => console.log("connect", socket.id));
  socket.on("connect_error", (e) => console.log("connect_error", e));
  socket.on("disconnect", (r) => console.log("disconnect", r));

  socket.emit("join_chat", { chat_id: "e15d65b4-ccba-42fc-9514-0e67a691f756" });
  socket.on("joined", (payload) => console.log("joined:", payload));
  socket.on("new_message", (payload) => console.log("new_message:", payload));

  window.__socket = socket;
})();
```