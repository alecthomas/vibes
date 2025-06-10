import { assertEquals } from "@std/assert";
import { time } from "./main.ts";

Deno.test(function timeTest() {
  const mockGetCurrentTime = () => new Date("2023-01-01T12:34:56");
  assertEquals(time(mockGetCurrentTime), "12:34:56");
});

Deno.test(async function timeHttpTest() {
  const server = Deno.serve({ port: 8888 }, async (req) => {
    if (req.method === "POST" && new URL(req.url).pathname === "/time") {
      const mockGetCurrentTime = () => new Date("2023-01-01T12:34:56");
      const result = time(mockGetCurrentTime);
      return new Response(result);
    }
    return new Response("Not Found", { status: 404 });
  });

  try {
    const response = await fetch("http://127.0.0.1:8888/time", {
      method: "POST"
    });
    const result = await response.text();
    assertEquals(result, "12:34:56");
  } finally {
    await server.shutdown();
  }
});