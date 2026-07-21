import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface Differentiator {
	title: string;
	description: string;
}

export interface CompanyAbout {
	founded_year: string;
	legal_form: string;
	headquarters: string;
	vision: string;
	missions: string[];
	values: string[];
	differentiators: Differentiator[];
}

export const load: PageLoad = async ({ fetch }) => {
	const [settings, about] = await Promise.all([
		apiCall<{ values: Record<string, string> }>('/admin/settings', { fetchFn: fetch }),
		apiCall<CompanyAbout>('/admin/settings/about', { fetchFn: fetch })
	]);
	return { settings, about };
};
