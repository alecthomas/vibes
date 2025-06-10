import { assertEquals } from "@std/assert";
import { helloThere } from "./main.ts";

Deno.test(function helloThereTest() {
  const mockGetCurrentTime = () => "12:34:56";
  assertEquals(helloThere("Bob", mockGetCurrentTime), "Hello, Bob, it is 12:34:56");
});

Deno.test(async function helloThereHttpTest() {
  const server = Deno.serve({ port: 8888 }, async (req) => {
    if (req.method === "POST" && new URL(req.url).pathname === "/helloThere") {
      const body = await req.json();
      const mockGetCurrentTime = () => "12:34:56";
      const result = helloThere(body.name, mockGetCurrentTime);
      return new Response(JSON.stringify({ result }), {
        headers: { "Content-Type": "application/json" }
      });
    }
    return new Response("Not Found", { status: 404 });
  });

  try {
    const response = await fetch("http://127.0.0.1:8888/helloThere", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "Bob" })
    });
    
    const data = await response.json();
    assertEquals(data.result, "Hello, Bob, it is 12:34:56");
  } finally {
    server.shutdown();
  }
});