import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface FaqRow {
	id: number;
	question: string;
	answer: string;
	division_id: number | null;
	service_id: number | null;
	is_published: boolean;
	sort_order: number;
}

export interface FaqPage {
	items: FaqRow[];
	total: number;
	page: number;
	page_size: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const q = url.searchParams.get('q') ?? '';
	const published = url.searchParams.get('published') ?? '';

	const params = new URLSearchParams({ page, page_size: '10' });
	if (q) params.set('q', q);
	if (published) params.set('is_published', published);

	const faqsPage = await apiCall<FaqPage>(`/admin/faqs?${params}`, { fetchFn: fetch });
	return { faqsPage, q, published };
};
