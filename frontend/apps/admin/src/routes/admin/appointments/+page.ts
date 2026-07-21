import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface AppointmentRow {
	id: number;
	date: string;
	time: string | null;
	status: string;
	note: string | null;
	assignee_name: string | null;
	request_id: number;
	request_reference: string | null;
	request_full_name: string;
}

export interface AppointmentPage {
	items: AppointmentRow[];
	total: number;
	page: number;
	page_size: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const appointmentsPage = await apiCall<AppointmentPage>(
		`/admin/appointments?page=${page}&page_size=15`,
		{ fetchFn: fetch }
	);
	return { appointmentsPage };
};
