import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const contentType = request.headers.get("content-type") ?? "";
    let body: string;

    if (contentType.includes("application/json")) {
      let json: Record<string, string>;

      try {
        json = await request.json();
      } catch {
        return NextResponse.json(
          { detail: "Invalid JSON request body" },
          { status: 400 },
        );
      }

      body = new URLSearchParams(json).toString();
    } else {
      body = await request.text();
    }

    const response = await fetch(
      `${process.env.FASTAPI_URL}/auth/token`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
      }
    );

    let data: { detail?: unknown; access_token?: string };

    try {
      data = await response.json();
    } catch {
      return NextResponse.json(
        { detail: "Authentication service returned an invalid response." },
        { status: 502 },
      );
    }

    if (!response.ok) {
      return NextResponse.json(
        {
          detail:
            typeof data.detail === "string" ? data.detail : "Login failed",
        },
        { status: response.status }
      );
    }

    if (typeof data.access_token !== "string" || !data.access_token.trim()) {
      return NextResponse.json(
        { detail: "Authentication service returned an invalid token." },
        { status: 502 },
      );
    }

    const result = NextResponse.json({ ok: true });

    // set token in cookie
    result.cookies.set('token', data.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 30 // Match the backend's 30-minute token expiry
    });

    return result

  } catch {
    return NextResponse.json(
      { detail: "Failed to log in. Please try again." },
      { status: 500 },
    );
  }
}

