import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const contentType = request.headers.get("content-type") ?? "";
    let payload: Record<string, unknown>;

    if (contentType.includes("application/x-www-form-urlencoded")) {
      const text = await request.text();
      const params = new URLSearchParams(text);
      payload = {
        fullname: params.get("fullname"),
        email: params.get("email") ?? params.get("username"),
        password: params.get("password"),
      };
    } else {
      try {
        payload = await request.json();
      } catch {
        return NextResponse.json(
          { detail: "Invalid JSON request body" },
          { status: 400 },
        );
      }
    }

    const response = await fetch(
      `${process.env.FASTAPI_URL}/auth/register`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      }
    );

    const data = await response.text();

    return new Response(data, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
      },
    });
  } catch {
    return NextResponse.json(
      { detail: "Failed to register the user" },
      { status: 500 },
    );
  }
}
