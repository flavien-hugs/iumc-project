import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface LocationRow {
	id: number;
	name: string;
	city: string;
	district: string | null;
	address: string | null;
	latitude: number | null;
	longitude: number | null;
	status: string;
	phone: string | null;
	whatsapp: string | null;
	email: string | null;
	opening_hours: string | null;
	manager_name: string | null;
	description: string | null;
	is_visible: boolean;
	updated_at: string;
}

export interface LocationPage {
	items: LocationRow[];
	total: number;
	page: number;
	page_size: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const q = url.searchParams.get('q') ?? '';
	const status = url.searchParams.get('status') ?? '';

	const params = new URLSearchParams({ page, page_size: '10' });
	if (q) params.set('q', q);
	if (status) params.set('status_filter', status);

	const data = await apiCall<LocationPage>(`/admin/locations?${params}`, { fetchFn: fetch });
	return { locationsPage: data, q, status };
};
