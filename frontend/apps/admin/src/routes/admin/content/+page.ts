import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface ServiceRow {
	id: number;
	title: string;
	slug: string;
	status: string;
}

export interface DivisionRow {
	id: number;
	name: string;
	slug: string;
	status: string;
	sort_order: number;
	services: ServiceRow[];
}

export const load: PageLoad = async ({ fetch }) => {
	const divisions = await apiCall<DivisionRow[]>('/admin/divisions', { fetchFn: fetch });
	return { divisions };
};
