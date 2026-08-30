export const runtime = "nodejs";

export async function POST(request: Request) {
  try {
    // Read the JSON sent from your frontend
    const body = await request.json();

    // Send it server-to-server to FastAPI
    const response = await fetch(
      `${process.env.FASTAPI_URL}/ask/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      }
    );

    // Forward FastAPI errors
    if (!response.ok) {
      return new Response(
        response.body,
        {
          status: response.status,
          statusText: response.statusText,
          headers: {
            "Content-Type":
              response.headers.get("Content-Type") ??
              "application/json",
          },
        }
      );
    }

    // Important: FastAPI must return a stream
    if (!response.body) {
      return new Response("FastAPI returned no response body", {
        status: 500,
      });
    }

    // Directly return the stream
    return new Response(response.body, {
      status: response.status,
      headers: {
        "Content-Type":
          response.headers.get("Content-Type") ??
          "text/plain; charset=utf-8",

        "Cache-Control": "no-cache, no-transform",
      },
    });
  } catch (error) {
    console.error("Streaming proxy error:", error);

    return new Response(
      JSON.stringify({
        detail: "Failed to connect to backend",
      }),
      {
        status: 500,
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
  }
}