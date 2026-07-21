import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface Dashboard {
	total_requests: number;
	new_requests: number;
	in_progress_requests: number;
	closed_requests: number;
	upcoming_appointments: number;
	active_services: number;
	locations: number;
	published_articles: number;
}

export const load: PageLoad = async ({ fetch }) => {
	const stats = await apiCall<Dashboard>('/admin/dashboard', { fetchFn: fetch });
	return { stats };
};
