export function echo(name: string, getCurrentTime: () => string): string {
  const time = getCurrentTime();
  return `Hello, ${name}, it is ${time}`;
}

