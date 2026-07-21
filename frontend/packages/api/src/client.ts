import { env } from '$env/dynamic/public';

export const API_BASE = env.PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface AuthUser {
	id: number;
	name: string;
	email: string;
	role: string;
}

export class ApiError extends Error {
	constructor(
		public status: number,
		message: string
	) {
		super(message);
	}
}

/** Appel API JSON avec cookies inclus (auth JWT httpOnly, ADR-0008). */
export async function apiCall<T>(
	path: string,
	options: { method?: string; body?: unknown; fetchFn?: typeof fetch } = {}
): Promise<T> {
	const { method = 'GET', body, fetchFn = fetch } = options;
	const response = await fetchFn(`${API_BASE}${path}`, {
		method,
		credentials: 'include',
		headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
		body: body !== undefined ? JSON.stringify(body) : undefined
	});
	if (!response.ok) {
		let detail = `Erreur ${response.status}`;
		try {
			const data = await response.json();
			if (typeof data.detail === 'string') detail = data.detail;
		} catch {
			// corps non JSON, on garde le message générique
		}
		throw new ApiError(response.status, detail);
	}
	if (response.status === 204) return undefined as T;
	return response.json();
}
