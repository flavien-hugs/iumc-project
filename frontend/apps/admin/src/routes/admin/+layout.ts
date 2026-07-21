import { redirect } from '@sveltejs/kit';
import { apiCall, type AuthUser } from '@iumc/api';
import type { LayoutLoad } from './$types';

// Panel d'administration : rendu côté client (ADR-0009), pas d'enjeu SEO.
export const ssr = false;

export const load: LayoutLoad = async ({ url, fetch }) => {
	const publicPages = ['/admin/login', '/admin/forgot-password', '/admin/reset-password'];
	if (publicPages.some((path) => url.pathname.startsWith(path))) {
		return { user: null };
	}

	let user: AuthUser | null = null;
	try {
		user = await apiCall<AuthUser>('/auth/me', { fetchFn: fetch });
	} catch {
		user = null;
	}
	if (user === null) {
		redirect(307, '/admin/login');
	}
	return { user };
};
