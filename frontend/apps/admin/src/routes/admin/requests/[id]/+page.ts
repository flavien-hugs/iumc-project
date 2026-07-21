import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface HistoryEntry {
	id: number;
	previous_status: string | null;
	new_status: string;
	user_name: string | null;
	note: string | null;
	created_at: string;
}

export interface AppointmentSummary {
	id: number;
	date: string;
	time: string | null;
	status: string;
	assignee_name: string | null;
	note: string | null;
}

export interface ServiceRequestDetail {
	id: number;
	reference: string | null;
	full_name: string;
	company: string | null;
	phone: string;
	email: string | null;
	city: string | null;
	client_type: string | null;
	division: string;
	service: string;
	subject: string | null;
	description: string;
	contact_preference: string;
	preferred_appointment_date: string | null;
	status: string;
	agent_id: number | null;
	agent_name: string | null;
	created_at: string;
	attachment: string | null;
	history: HistoryEntry[];
	appointments: AppointmentSummary[];
}

export interface UserRow {
	id: number;
	name: string;
	role: string;
	is_active: boolean;
}

export const load: PageLoad = async ({ params, fetch }) => {
	const [request, usersPage] = await Promise.all([
		apiCall<ServiceRequestDetail>(`/admin/service-requests/${params.id}`, { fetchFn: fetch }),
		apiCall<{ items: UserRow[] }>('/admin/users?page_size=100', { fetchFn: fetch }).catch(
			() => ({ items: [] as UserRow[] })
		)
	]);
	return { request, users: usersPage.items };
};
