import { serverApiGet } from '@iumc/api/server';
import type { PublicArticleSummary, PublicPage } from '$lib/content';
import type { PageServerLoad } from './$types';

const PAGE_SIZE = 9;

export const load: PageServerLoad = async ({ fetch, url }) => {
	const q = url.searchParams.get('q')?.trim() ?? '';
	const category = url.searchParams.get('category') ?? '';
	const page = Math.max(1, Number(url.searchParams.get('page')) || 1);

	const params = new URLSearchParams({ page: String(page), page_size: String(PAGE_SIZE) });
	if (q) params.set('q', q);
	if (category) params.set('category', category);

	const [articlesPage, categories] = await Promise.all([
		serverApiGet<PublicPage<PublicArticleSummary>>(`/articles?${params}`, fetch),
		serverApiGet<string[]>('/article-categories', fetch)
	]);
	return { articlesPage, categories, q, category };
};
