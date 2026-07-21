// Appels API côté serveur (SSR du site public, ADR-0009).
//
// Dans le réseau Docker Compose, le serveur Node joint FastAPI par le nom de
// service (API_INTERNAL_URL=http://backend:8000/api/v1) alors que le
// navigateur passe par l'URL publique. Ce module n'est importable que côté
// serveur ($env/dynamic/private).

import { env as privateEnv } from '$env/dynamic/private';
import { env as publicEnv } from '$env/dynamic/public';
import { ApiError } from './client';

function apiBase(): string {
	return (
		privateEnv.API_INTERNAL_URL ||
		publicEnv.PUBLIC_API_BASE_URL ||
		'http://localhost:8000/api/v1'
	);
}

/** GET JSON côté serveur ; propage 404 en ApiError pour les pages de détail. */
export async function serverApiGet<T>(path: string, fetchFn: typeof fetch = fetch): Promise<T> {
	const response = await fetchFn(`${apiBase()}${path}`);
	if (!response.ok) {
		throw new ApiError(response.status, `Erreur ${response.status} sur ${path}`);
	}
	return response.json();
}

export { ApiError };
