import { serverApiGet } from '@iumc/api/server';
import type { PublicArticleSummary } from '$lib/content';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ fetch }) => {
	const articles = await serverApiGet<PublicArticleSummary[]>('/articles', fetch);
	return { articles };
};
