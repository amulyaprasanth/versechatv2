import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    // Read the JSON sent from your frontend
    const token = (await cookies()).get('token')?.value;

    if (!token) {
      return NextResponse.json(
        { detail: "Unauthorized" },
        { status: 401 }
      );
    }
    // Send it server-to-server to FastAPI
    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        { detail: "Invalid JSON request body" },
        { status: 400 },
      );
    }
    const response = await fetch(
      `${process.env.FASTAPI_URL}/ask/stream`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
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
