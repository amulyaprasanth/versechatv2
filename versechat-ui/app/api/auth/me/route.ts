import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import {
  refreshAuthTokens,
  setAuthCookies,
  type TokenPair,
} from "../../fetch-backend";

type UserProfile = {
  fullname: string;
  email: string;
};

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

function isUserProfile(value: unknown): value is UserProfile {
  if (!value || typeof value !== "object") return false;
  const profile = value as Partial<UserProfile>;
  return typeof profile.fullname === "string" && typeof profile.email === "string";
}

async function readProfile(accessToken: string) {
  return fetch(`${process.env.FASTAPI_URL}/auth/me`, {
    headers: { Authorization: `Bearer ${accessToken}` },
    cache: "no-store",
  });
}

function sessionExpiredResponse() {
  const response = NextResponse.json(
    { detail: "Your session has expired." },
    { status: 401 },
  );
  clearAuthCookies(response);
  return response;
}

function errorResponse(
  detail: string,
  status: number,
  tokens?: TokenPair,
) {
  const response = NextResponse.json({ detail }, { status });
  if (tokens) setAuthCookies(response, tokens);
  return response;
}

export async function GET() {
  try {
    const cookieStore = await cookies();
    const accessToken = cookieStore.get("token")?.value;
    const refreshToken = cookieStore.get("refreshToken")?.value;
    if (!accessToken && !refreshToken) return sessionExpiredResponse();

    let response = accessToken ? await readProfile(accessToken) : undefined;
    let refreshedTokens: TokenPair | undefined;

    if ((!response || response.status === 401) && refreshToken) {
      refreshedTokens = await refreshAuthTokens(refreshToken) ?? undefined;
      if (!refreshedTokens) return sessionExpiredResponse();
      response = await readProfile(refreshedTokens.access_token);
    }

    if (!response?.ok) {
      const statusCode = response?.status ?? 502;
      if (statusCode === 401) return sessionExpiredResponse();
      return errorResponse("Unable to load profile.", statusCode, refreshedTokens);
    }

    const profile: unknown = await response.json().catch(() => null);
    if (!isUserProfile(profile)) {
      return errorResponse(
        "Authentication service returned an invalid profile.",
        502,
        refreshedTokens,
      );
    }

    const result = NextResponse.json({
      fullname: profile.fullname,
      email: profile.email,
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
