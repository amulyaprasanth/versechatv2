import { cookies } from "next/headers";
import { NextResponse } from "next/server";

export type TokenPair = {
  access_token: string;
  refresh_token: string;
};

export function setAuthCookies(response: NextResponse, tokens: TokenPair) {
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

export function clearAuthCookies(response: NextResponse) {
  for (const name of ["token", "refreshToken"]) {
    response.cookies.set(name, "", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 0,
    });
  }
}

function createUnauthorizedResponse(detail: string) {
  const response = NextResponse.json({ detail }, { status: 401 });
  clearAuthCookies(response);
  return response;
}

export async function refreshAuthTokens(
  refreshToken: string,
): Promise<TokenPair | null> {
  const response = await fetch(`${process.env.FASTAPI_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
    cache: "no-store",
  });
  if (!response.ok) return null;

  const data: unknown = await response.json().catch(() => null);
  if (
    !data ||
    typeof data !== "object" ||
    typeof (data as Partial<TokenPair>).access_token !== "string" ||
    typeof (data as Partial<TokenPair>).refresh_token !== "string"
  ) {
    return null;
  }
  return data as TokenPair;
}

export async function proxyToBackend(
  path: string,
  options?: RequestInit,
): Promise<NextResponse> {
  try {
    const cookieStore = await cookies();
    const accessToken = cookieStore.get("token")?.value;
    const refreshToken = cookieStore.get("refreshToken")?.value;

    if (!accessToken && !refreshToken) {
      return createUnauthorizedResponse("Not authenticated");
    }

    const makeReq = (token: string) => {
      const headers = new Headers(options?.headers);
      headers.set("Authorization", `Bearer ${token}`);
      return fetch(`${process.env.FASTAPI_URL}${path}`, {
        ...options,
        headers,
        cache: "no-store",
      });
    };

    let response: Response | undefined;
    let refreshedTokens: TokenPair | undefined;

    if (accessToken) {
      response = await makeReq(accessToken);
    }

    if ((!response || response.status === 401) && refreshToken) {
      refreshedTokens = (await refreshAuthTokens(refreshToken)) ?? undefined;
      if (!refreshedTokens) {
        return createUnauthorizedResponse("Your session has expired.");
      }
      response = await makeReq(refreshedTokens.access_token);
    }

    if (!response) {
      return createUnauthorizedResponse("Authentication failed");
    }

    if (response.status === 204) {
      const emptyRes = new NextResponse(null, { status: 204 });
      if (refreshedTokens) setAuthCookies(emptyRes, refreshedTokens);
      return emptyRes;
    }

    const contentType = response.headers.get("Content-Type") ?? "application/json";
    const body = await response.text();

    const nextRes = new NextResponse(body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        "Content-Type": contentType,
      },
    });

    if (refreshedTokens) {
      setAuthCookies(nextRes, refreshedTokens);
    }

    return nextRes;
  } catch {
    return NextResponse.json(
      { detail: "Failed to connect to backend server" },
      { status: 500 }
    );
  }
}
