import { assertEquals } from "@std/assert";
import { echo } from "./main.ts";

Deno.test(function echoTest() {
  const mockGetCurrentTime = () => "12:34:56";
  assertEquals(echo("Bob", mockGetCurrentTime), "Hello, Bob, it is 12:34:56");
});

Deno.test(async function echoHttpTest() {
  const mockGetCurrentTime = () => "12:34:56";
  
  const server = Deno.serve({ port: 8888 }, async (req) => {
    if (req.method === "POST" && new URL(req.url).pathname === "/echo") {
      const body = await req.text();
      const result = echo(body, mockGetCurrentTime);
      return new Response(result);
    }
    return new Response("Not Found", { status: 404 });
  });

  try {
    const response = await fetch("http://127.0.0.1:8888/echo", {
      method: "POST",
      body: "Bob"
    });
    const result = await response.text();
    assertEquals(result, "Hello, Bob, it is 12:34:56");
  } finally {
    server.shutdown();
  }
});