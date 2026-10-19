import { NextRequest, NextResponse } from "next/server";

export function proxy(request: NextRequest) {
  const hasAccessToken = request.cookies.has("token");
  const hasRefreshToken = request.cookies.has("refreshToken");

  if (!hasAccessToken && !hasRefreshToken) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/chat/:path*"],
};
