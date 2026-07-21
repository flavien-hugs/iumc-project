import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface ServiceRequestSummary {
	id: number;
	reference: string | null;
	full_name: string;
	phone: string;
	city: string | null;
	client_type: string | null;
	division: string;
	service: string;
	status: string;
	created_at: string;
}

export interface ServiceRequestPage {
	items: ServiceRequestSummary[];
	total: number;
	page: number;
	page_size: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const q = url.searchParams.get('q') ?? '';
	const status = url.searchParams.get('status') ?? '';
	const dateFrom = url.searchParams.get('date_from') ?? '';
	const dateTo = url.searchParams.get('date_to') ?? '';
	const sort = url.searchParams.get('sort') ?? 'desc';
	const pageNumber = url.searchParams.get('page') ?? '1';

	const params = new URLSearchParams();
	if (q) params.set('q', q);
	if (status) params.set('status_filter', status);
	if (dateFrom) params.set('date_from', dateFrom);
	if (dateTo) params.set('date_to', dateTo);
	params.set('sort', sort);
	params.set('page', pageNumber);
	params.set('page_size', '10');

	const requestsPage = await apiCall<ServiceRequestPage>(`/admin/service-requests?${params}`, {
		fetchFn: fetch
	});
	return { requestsPage, q, status, dateFrom, dateTo, sort };
};
