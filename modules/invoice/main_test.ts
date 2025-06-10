import { assertEquals } from "@std/assert";
import { invoice } from "./main.ts";

interface Item {
  id?: string;
  description: string;
  price: number;
  quantity: number;
}

interface Invoice {
  count: number;
  price: number;
}

Deno.test(function invoiceTest() {
  const items: Item[] = [{
    id: "SKU001",
    description: "Coffee Mug",
    price: 8.99,
    quantity: 3
  }, {
    description: "Gift Card",
    price: 50.00,
    quantity: 1
  }];
  
  const result = invoice(items);
  assertEquals(result.count, 4);
  assertEquals(result.price, 76.97);
});

Deno.test(async function invoiceHttpTest() {
  const server = Deno.serve({ port: 8888 }, async (req) => {
    if (req.method === "POST" && new URL(req.url).pathname === "/invoice") {
      const items = await req.json();
      const result = invoice(items);
      return new Response(JSON.stringify(result), {
        headers: { "Content-Type": "application/json" }
      });
    }
    return new Response("Not Found", { status: 404 });
  });

  try {
    const items: Item[] = [{
      id: "SKU001",
      description: "Coffee Mug",
      price: 8.99,
      quantity: 3
    }, {
      description: "Gift Card",
      price: 50.00,
      quantity: 1
    }];

    const response = await fetch("http://127.0.0.1:8888/invoice", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(items)
    });

    const result = await response.json();
    assertEquals(result.count, 4);
    assertEquals(result.price, 76.97);
  } finally {
    server.shutdown();
  }
});