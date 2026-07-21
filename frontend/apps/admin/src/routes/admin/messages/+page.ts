import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface ContactMessageRow {
	id: number;
	name: string;
	phone: string;
	email: string | null;
	subject: string;
	message: string;
	is_processed: boolean;
	created_at: string;
}

export interface ContactMessagePage {
	items: ContactMessageRow[];
	total: number;
	page: number;
	page_size: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const messagesPage = await apiCall<ContactMessagePage>(
		`/admin/contact-messages?page=${page}&page_size=10`,
		{ fetchFn: fetch }
	);
	return { messagesPage };
};
