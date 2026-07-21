import { serverApiGet } from '@iumc/api/server';
import type { PublicArticleSummary, PublicPage } from '$lib/content';
import type { PageServerLoad } from './$types';

interface PublicCompany {
	about: {
		values: string[];
		differentiators: { title: string; description: string }[];
	};
}

export const load: PageServerLoad = async ({ fetch }) => {
	const [articlesPage, company, locations] = await Promise.all([
		serverApiGet<PublicPage<PublicArticleSummary>>('/articles?page_size=3', fetch),
		serverApiGet<PublicCompany>('/company', fetch),
		serverApiGet<{ status: string }[]>('/locations', fetch)
	]);
	return { articles: articlesPage.items, company, locationsCount: locations.length };
};
