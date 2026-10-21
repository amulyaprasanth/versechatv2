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

    let data: unknown;

    try {
      data = await response.json();
    } catch {
      return NextResponse.json(
        { detail: "Authentication service returned an invalid response." },
        { status: 502 },
      );
    }

    if (!data || typeof data !== "object") {
      return NextResponse.json(
        { detail: "Authentication service returned an invalid response." },
        { status: 502 },
      );
    }

    const authData = data as {
      detail?: unknown;
      access_token?: unknown;
      refresh_token?: unknown;
    };

    if (!response.ok) {
      return NextResponse.json(
        {
          detail:
            typeof authData.detail === "string"
              ? authData.detail
              : "Login failed",
        },
        { status: response.status }
      );
    }

    if (
      typeof authData.access_token !== "string" ||
      !authData.access_token.trim()
    ) {
      return NextResponse.json(
        { detail: "Authentication service returned an invalid access token." },
        { status: 502 },
      );
    }

    if (
      typeof authData.refresh_token !== "string" ||
      !authData.refresh_token.trim()
    ) {
      return NextResponse.json(
        { detail: "Authentication service returned an invalid refresh token." },
        { status: 502 },
      );
    }

    const result = NextResponse.json({ ok: true });

    // set token in cookie
    result.cookies.set('token', authData.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 30 // Match the backend's 30-minute token expiry
    })
    result.cookies.set('refreshToken', authData.refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 60 * 60 * 24 * 30
    });

    return result

  } catch {
    return NextResponse.json(
      { detail: "Failed to log in. Please try again." },
      { status: 500 },
    );
  }
}

