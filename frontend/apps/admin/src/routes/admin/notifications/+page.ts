import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface NotificationRow {
	id: number;
	type: string;
	title: string;
	resource: string | null;
	resource_id: number | null;
	is_read: boolean;
	created_at: string;
}

export interface NotificationPage {
	items: NotificationRow[];
	total: number;
	page: number;
	page_size: number;
	unread_count: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const notificationsPage = await apiCall<NotificationPage>(
		`/admin/notifications?page=${page}&page_size=15`,
		{ fetchFn: fetch }
	);
	return { notificationsPage };
};
