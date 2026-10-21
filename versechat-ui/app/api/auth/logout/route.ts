import { cookies } from "next/headers";
import { NextResponse } from "next/server";

const AUTH_COOKIE_NAMES = ["token", "refreshToken"] as const;

export async function POST() {
  const cookieStore = await cookies();
  const refreshToken = cookieStore.get("refreshToken")?.value;

  // Revoke the server-side refresh-token family before dropping the browser
  // cookies. Logout remains successful locally if the auth service is down.
  if (refreshToken) {
    try {
      await fetch(`${process.env.FASTAPI_URL}/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
        cache: "no-store",
      });
    } catch {
      // Always clear the browser's credentials even if backend revocation fails.
    }
  }

  const response = NextResponse.json({ ok: true });
  for (const name of AUTH_COOKIE_NAMES) {
    response.cookies.set(name, "", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: 0,
    });
  }

  return response;
}
