export interface Item {
  description: string;
  price: number;
  quantity: number;
}

export interface Invoice {
  count: number;
  price: number;
}

export function invoice(items: Item[]): Invoice {
  const count = items.reduce((sum, item) => sum + item.quantity, 0);
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const price = subtotal * 1.1;
  
  return { count, price };
}

