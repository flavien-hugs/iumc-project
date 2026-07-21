import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface MediaRow {
	id: number;
	name: string;
	path: string;
	mime_type: string;
	size: number;
	created_at: string;
}

export interface MediaPage {
	items: MediaRow[];
	total: number;
	page: number;
	page_size: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const mediaPage = await apiCall<MediaPage>(`/admin/media?page=${page}&page_size=12`, {
		fetchFn: fetch
	});
	return { mediaPage };
};
