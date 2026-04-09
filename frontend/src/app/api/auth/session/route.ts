import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

const JWT_COOKIE_NAME = 'jwt';
const JWT_EXPIRY_HOURS = 24;

/**
 * GET /api/auth/session
 * Retrieves the JWT from the httpOnly cookie
 */
export async function GET() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get(JWT_COOKIE_NAME)?.value;

    if (!token) {
      return NextResponse.json({ token: null }, { status: 200 });
    }

    return NextResponse.json({ token }, { status: 200 });
  } catch (error) {
    console.error('Failed to get session:', error);
    return NextResponse.json(
      { error: 'Failed to get session' },
      { status: 500 }
    );
  }
}

/**
 * POST /api/auth/session
 * Sets the JWT in an httpOnly cookie
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { token } = body;

    if (!token) {
      return NextResponse.json(
        { error: 'Token is required' },
        { status: 400 }
      );
    }

    const response = NextResponse.json({ ok: true }, { status: 200 });
    const cookieStore = await cookies();

    // Set httpOnly cookie with JWT
    // In production, secure should be true
    cookieStore.set(JWT_COOKIE_NAME, token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: JWT_EXPIRY_HOURS * 60 * 60, // 24 hours in seconds
      path: '/',
    });

    return response;
  } catch (error) {
    console.error('Failed to set session:', error);
    return NextResponse.json(
      { error: 'Failed to set session' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/auth/session
 * Clears the JWT cookie
 */
export async function DELETE() {
  try {
    const cookieStore = await cookies();
    cookieStore.delete(JWT_COOKIE_NAME);

    return NextResponse.json({ ok: true }, { status: 200 });
  } catch (error) {
    console.error('Failed to delete session:', error);
    return NextResponse.json(
      { error: 'Failed to delete session' },
      { status: 500 }
    );
  }
}