import { proxyToBackend } from "../fetch-backend";

export async function GET() {
  return proxyToBackend("/conversations");
}

export async function POST(request: Request) {
  let body: string | undefined;
  try {
    body = await request.text();
  } catch {
    body = undefined;
  }

  return proxyToBackend("/conversations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: body || undefined,
  });
}
