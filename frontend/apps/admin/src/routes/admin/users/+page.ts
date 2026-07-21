import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface UserRow {
	id: number;
	name: string;
	email: string;
	phone: string | null;
	role: string;
	location_id: number | null;
	is_active: boolean;
	deleted_at: string | null;
	last_login_at: string | null;
}

export interface UserPage {
	items: UserRow[];
	total: number;
	page: number;
	page_size: number;
}

export interface LocationOption {
	id: number;
	name: string;
	city: string;
}

interface LocationListPage {
	items: LocationOption[];
	total: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const includeDeleted = url.searchParams.get('include_deleted') === 'true';
	const [usersPage, locationsPage] = await Promise.all([
		apiCall<UserPage>(
			`/admin/users?page=${page}&page_size=10&include_deleted=${includeDeleted}`,
			{ fetchFn: fetch }
		),
		apiCall<LocationListPage>('/admin/locations?page=1&page_size=100', { fetchFn: fetch })
	]);
	return { usersPage, locations: locationsPage.items, includeDeleted };
};
