import { cookies } from "next/headers";
import { NextResponse } from "next/server";

type RefreshedTokens = {
  access_token: string;
  refresh_token: string;
};

function setAuthCookies(response: NextResponse, tokens: RefreshedTokens) {
  const secure = process.env.NODE_ENV === "production";

  response.cookies.set("token", tokens.access_token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 30,
  });
  response.cookies.set("refreshToken", tokens.refresh_token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 30,
  });
}

function clearAuthCookies(response: NextResponse) {
  response.cookies.set("token", "", { path: "/", maxAge: 0 });
  response.cookies.set("refreshToken", "", { path: "/", maxAge: 0 });
}

function unauthorizedResponse() {
  const response = NextResponse.json(
    { detail: "Your session has expired. Please sign in again." },
    { status: 401 },
  );
  clearAuthCookies(response);
  return response;
}

export async function POST(request: Request) {
  try {
    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return NextResponse.json(
        { detail: "Invalid JSON request body" },
        { status: 400 },
      );
    }

    const cookieStore = await cookies();
    const accessToken = cookieStore.get("token")?.value;
    const refreshToken = cookieStore.get("refreshToken")?.value;

    const sendStreamRequest = (token: string) =>
      fetch(`${process.env.FASTAPI_URL}/ask/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

    let response: Response | undefined;
    let refreshedTokens: RefreshedTokens | undefined;

    if (accessToken) {
      response = await sendStreamRequest(accessToken);
    }

    if (!response || response.status === 401) {
      if (!refreshToken) {
        return unauthorizedResponse();
      }

      const refreshResponse = await fetch(
        `${process.env.FASTAPI_URL}/auth/refresh`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
        },
      );

      if (!refreshResponse.ok) {
        return unauthorizedResponse();
      }

      let refreshData: unknown;
      try {
        refreshData = await refreshResponse.json();
      } catch {
        return NextResponse.json(
          { detail: "Authentication service returned an invalid response." },
          { status: 502 },
        );
      }

      if (!refreshData || typeof refreshData !== "object") {
        return NextResponse.json(
          { detail: "Authentication service returned an invalid response." },
          { status: 502 },
        );
      }

      const tokenData = refreshData as {
        access_token?: unknown;
        refresh_token?: unknown;
      };

      if (
        typeof tokenData.access_token !== "string" ||
        !tokenData.access_token.trim() ||
        typeof tokenData.refresh_token !== "string" ||
        !tokenData.refresh_token.trim()
      ) {
        return NextResponse.json(
          { detail: "Authentication service returned invalid tokens." },
          { status: 502 },
        );
      }

      refreshedTokens = {
        access_token: tokenData.access_token,
        refresh_token: tokenData.refresh_token,
      };
      response = await sendStreamRequest(refreshedTokens.access_token);

      if (response.status === 401) {
        return unauthorizedResponse();
      }
    }

    if (!response) {
      return unauthorizedResponse();
    }

    if (!response.ok) {
      const errorResponse = new NextResponse(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: {
          "Content-Type":
            response.headers.get("Content-Type") ?? "application/json",
        },
      });
      if (refreshedTokens) setAuthCookies(errorResponse, refreshedTokens);
      return errorResponse;
    }

    if (!response.body) {
      const emptyResponse = NextResponse.json(
        { detail: "FastAPI returned no response body" },
        { status: 500 },
      );
      if (refreshedTokens) setAuthCookies(emptyResponse, refreshedTokens);
      return emptyResponse;
    }

    const streamResponse = new NextResponse(response.body, {
      status: response.status,
      headers: {
        "Content-Type":
          response.headers.get("Content-Type") ?? "text/plain; charset=utf-8",
        "Cache-Control": "no-cache, no-transform",
      },
    });
    if (refreshedTokens) setAuthCookies(streamResponse, refreshedTokens);
    return streamResponse;
  } catch {
    return NextResponse.json(
      { detail: "Failed to connect to backend" },
      { status: 500 },
    );
  }
}
