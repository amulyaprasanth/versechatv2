import { cookies } from "next/headers";
import { NextResponse } from "next/server";

type UserProfile = {
  fullname: string;
  email: string;
};

type TokenPair = {
  access_token: string;
  refresh_token: string;
};

function setAuthCookies(response: NextResponse, tokens: TokenPair) {
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
  const secure = process.env.NODE_ENV === "production";
  for (const name of ["token", "refreshToken"]) {
    response.cookies.set(name, "", {
      httpOnly: true,
      secure,
      sameSite: "lax",
      path: "/",
      maxAge: 0,
    });
  }
}

async function readProfile(accessToken: string) {
  return fetch(`${process.env.FASTAPI_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
}

export async function GET() {
  try {
    const cookieStore = await cookies();
    const accessToken = cookieStore.get("token")?.value;
    const refreshToken = cookieStore.get("refreshToken")?.value;

    if (!accessToken && !refreshToken) {
      return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
    }

    let response = accessToken ? await readProfile(accessToken) : undefined;
    let refreshedTokens: TokenPair | undefined;

    if ((!response || response.status === 401) && refreshToken) {
      const refreshResponse = await fetch(
        `${process.env.FASTAPI_URL}/auth/refresh`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh_token: refreshToken }),
          cache: "no-store",
        },
      );

      if (!refreshResponse.ok) {
        const result = NextResponse.json(
          { detail: "Your session has expired." },
          { status: 401 },
        );
        clearAuthCookies(result);
        return result;
      }

      const tokenData: unknown = await refreshResponse.json();
      if (
        !tokenData ||
        typeof tokenData !== "object" ||
        typeof (tokenData as Partial<TokenPair>).access_token !== "string" ||
        typeof (tokenData as Partial<TokenPair>).refresh_token !== "string"
      ) {
        return NextResponse.json(
          { detail: "Authentication service returned invalid tokens." },
          { status: 502 },
        );
      }

      refreshedTokens = tokenData as TokenPair;
      response = await readProfile(refreshedTokens.access_token);
    }

    if (!response?.ok) {
      const result = NextResponse.json(
        { detail: "Unable to load profile." },
        { status: response?.status ?? 502 },
      );
      if (refreshedTokens) setAuthCookies(result, refreshedTokens);
      if (response?.status === 401) clearAuthCookies(result);
      return result;
    }

    const profile: unknown = await response.json();
    if (
      !profile ||
      typeof profile !== "object" ||
      typeof (profile as Partial<UserProfile>).fullname !== "string" ||
      typeof (profile as Partial<UserProfile>).email !== "string"
    ) {
      return NextResponse.json(
        { detail: "Authentication service returned an invalid profile." },
        { status: 502 },
      );
    }

    const result = NextResponse.json({
      fullname: (profile as UserProfile).fullname,
      email: (profile as UserProfile).email,
    });
    if (refreshedTokens) setAuthCookies(result, refreshedTokens);
    return result;
  } catch {
    return NextResponse.json(
      { detail: "Unable to load profile." },
      { status: 500 },
    );
  }
}
