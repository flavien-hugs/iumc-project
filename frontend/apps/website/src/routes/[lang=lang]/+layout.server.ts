import { serverApiGet } from '@iumc/api/server';
import type { PublicDivision } from '$lib/content';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ params, fetch }) => {
	// Pôles et services actifs, éditables depuis le panel (statuts respectés).
	const divisions = await serverApiGet<PublicDivision[]>('/divisions', fetch);
	return { lang: params.lang, divisions };
};
