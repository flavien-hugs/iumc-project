import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface AuditLogRow {
	id: number;
	user_name: string | null;
	action: string;
	resource: string | null;
	resource_id: number | null;
	ip_address: string | null;
	details: Record<string, unknown> | null;
	created_at: string;
}

export interface AuditLogPage {
	items: AuditLogRow[];
	total: number;
	page: number;
	page_size: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const dateFrom = url.searchParams.get('date_from') ?? '';
	const dateTo = url.searchParams.get('date_to') ?? '';

	const params = new URLSearchParams({ page, page_size: '20' });
	if (dateFrom) params.set('date_from', dateFrom);
	if (dateTo) params.set('date_to', dateTo);

	const logsPage = await apiCall<AuditLogPage>(`/admin/audit-logs?${params}`, { fetchFn: fetch });
	return { logsPage, dateFrom, dateTo };
};
