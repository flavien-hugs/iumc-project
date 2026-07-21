import { serverApiGet } from '@iumc/api/server';
import type { PublicArticleSummary } from '$lib/content';
import type { PageServerLoad } from './$types';

interface PublicCompany {
	about: {
		values: string[];
		differentiators: { title: string; description: string }[];
	};
}

export const load: PageServerLoad = async ({ fetch }) => {
	const [articles, company] = await Promise.all([
		serverApiGet<PublicArticleSummary[]>('/articles?limit=3', fetch),
		serverApiGet<PublicCompany>('/company', fetch)
	]);
	return { articles, company };
};
